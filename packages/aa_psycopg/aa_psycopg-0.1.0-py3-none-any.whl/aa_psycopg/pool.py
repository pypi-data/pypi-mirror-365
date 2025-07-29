import functools
import logging
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Generator, Callable, Any, Self
from urllib.parse import quote_plus

import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


def track_query_stats(method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(self: "PostgreSQLPool", *args, **kwargs):
        query_name: str | None = kwargs.get("query_name")
        start = time.perf_counter()
        result = method(self, *args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(
            "Query runtime (query_name=%s): %.6fs",
            query_name,
            elapsed,
        )
        if query_name:
            stats = self._query_stats[query_name]
            stats["total_time"] += elapsed
            stats["count"] += 1
        return result

    return wrapper


class PostgreSQLPool:
    """
    A synchronous PostgreSQL client using psycopg3 and connection pooling.

    Provides methods for querying (SELECT, INSERT, UPDATE, DELETE) and
    transaction execution, while tracking query runtimes.
    """

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int,
        db: str,
        min_size: int = 0,
        max_size: int = 1,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Postgres client. Pool is created lazily in context manager.

        Args:
            user (str): Database username.
            password (str): Database password.
            host (str): PostgreSQL server hostname.
            port (int): PostgreSQL server port.
            db (str): Database name.
            min_size (int, optional): Minimum pool size. Defaults to 0.
            max_size (int, optional): Maximum pool size. Defaults to 1.
            **kwargs (Any): Extra arguments passed to `ConnectionPool`.

        Usage:
            with PostgreSQLPool(user, password, host, port, db) as client:
                client.ping()
                res = client.read("SELECT * FROM my_table", query_name="my_query")
        """
        # Escape special characters (e.g., %, @, :) so the password is valid in the DSN URL
        safe_password = quote_plus(password)
        self._dsn = f"postgresql://{user}:{safe_password}@{host}:{port}/{db}?client_encoding=UTF8"
        self._dsn_masked: str = f"postgresql://{user}:***@{host}:{port}/{db}"
        self._min_size: int = min_size
        self._max_size: int = max_size
        self._extra_pool_params: dict[str, Any] = kwargs
        self._pool: ConnectionPool | None = None
        self._in_context: bool = False
        self._query_stats: defaultdict[str, dict[str, float | int]] = defaultdict(
            lambda: {"total_time": 0.0, "count": 0}
        )
        self._schemas: dict[str, list[psycopg.Column]] = {}
        logger.info("Initialized Postgres client (pool not created yet): %s", self)

    def __repr__(self) -> str:
        """Get a masked DSN (password hidden).

        Returns:
            str: DSN string with password masked.
        """
        return f"{self.__class__.__name__}({self._dsn_masked})"

    def __enter__(self) -> Self:
        """Create a connection pool when entering context.

        Returns:
            SyncPostgresClient: This instance with initialized pool.
        """
        if self._pool is None:
            self._pool = ConnectionPool(
                conninfo=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                **self._extra_pool_params,
            )
            logger.info("Connection pool created: %s", self)
        self._in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the pool when exiting context.

        Args:
            exc_type (type): Exception type, if any.
            exc_val (BaseException): Exception value, if any.
            exc_tb (TracebackType): Traceback, if any.
        """
        self._in_context = False
        if self._pool is not None:
            logger.info("Closing connection pool: %s", self)
            self._pool.close()
            self._pool = None

    def get_stats(self) -> dict[str, dict[str, float | int]]:
        """Get aggregated query stats.

        Returns:
            dict[str, dict[str, float | int]]: Query statistics, keyed by query name,
            including total execution time and call count.
        """
        return dict(self._query_stats)

    def get_schema(self, query: str) -> list[psycopg.Column] | None:
        """Get the schema for a specific query.

        Args:
            query (str): The SQL query string.

        Returns:
            list[psycopg.Column] | None: List of columns if schema exists, otherwise None.
        """
        schema = self._schemas.get(query)
        if schema is None:
            logger.error("No schema found for query: %s", query)
            raise ValueError(
                f"No schema found for query: {query}. "
                "Ensure the query has been executed at least once."
            )
        return schema

    def _ensure_in_context(self) -> None:
        """Ensure the client is used inside a `with` block.

        Raises:
            RuntimeError: If used outside a context manager.
        """
        if not self._in_context:
            raise RuntimeError(
                "SyncPostgresClient must be used within a 'with' context manager block.\n"
                "Example:\n"
                "  with SyncPostgresClient(...) as client:\n"
                "      client.select(..., query_name='my_query')"
            )

    def _log_query(self, msg: str, query_name: str | None = None) -> None:
        """Log a query execution message.

        Args:
            msg (str): The message to log.
            query_name (str | None): Optional query name for tracking.
        """
        if query_name:
            logger.info("%s on %s (query_name=%s)", msg, self, query_name)
        else:
            logger.info("%s on %s", msg, self)

    @contextmanager
    def _connection(
        self,
    ) -> Generator[tuple[psycopg.Connection, psycopg.Cursor], None, None]:
        """Yield a pooled database connection and cursor.

        Yields:
            tuple[psycopg.Connection, psycopg.Cursor]: Active connection and cursor.

        Raises:
            psycopg.Error: If a database error occurs.
            Exception: For any unexpected error.
        """
        self._ensure_in_context()
        logger.info("Acquiring connection from pool: %s", self)
        try:
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    yield conn, cur
        except psycopg.Error as e:
            logger.error("Database error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise
        finally:
            logger.info("Connection returned to pool: %s", self)

    @track_query_stats
    def ping(
        self, retries: int = 0, timeout: float = 60, query_name: str | None = "ping"
    ) -> bool:
        """Ping the database by executing a simple query.

        Args:
            retries (int, optional): Number of retry attempts. Defaults to 0.
            timeout (float, optional): Delay between retries in seconds. Defaults to 60.
            query_name (str | None, optional): Name for query statistics tracking.

        Returns:
            bool: True if ping succeeds, False otherwise.
        """
        for attempt in range(retries + 1):
            try:
                with self._connection() as (_, cur):
                    cur.execute("SELECT 1")
                    self._log_query("Ping executed successfully", query_name=query_name)
                    return True
            except Exception as e:
                logger.warning("Postgres ping failed (attempt %d): %s", attempt + 1, e)
                if attempt < retries:
                    time.sleep(timeout)
        return False

    @track_query_stats
    def read(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        query_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a READ query.

        Args:
            query (str): SQL query.
            params (dict[str, Any] | None): Optional query parameters.
            return_df (bool): If True, return results as a DataFrame (not implemented).
            query_name (str | None): Optional query name for tracking.

        Returns:
            list[dict[str, Any]]: List of rows as dictionaries.
        """
        self._log_query("Executing READ", query_name=query_name)
        with self._connection() as (_, cur):
            cur.execute(query, params)
            results = cur.fetchall()
            self._schemas[query] = cur.description
            return results

    @track_query_stats
    def write(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        returning: bool = False,
        query_name: str | None = None,
    ) -> list[dict[str, Any]] | None:
        """Execute a WRITE (INSERT, UPDATE, or DELETE) query.

        Args:
            query (str): SQL query.
            params (dict[str, Any] | None): Query parameters.
            returning (bool): If True, return query results (for RETURNING clauses).
            query_name (str | None): Query name for stats.

        Returns:
            list[dict[str, Any]] | None: Fetched rows if returning is True, otherwise None.
        """
        self._log_query("Executing INSERT", query_name=query_name)
        with self._connection() as (_, cur):
            cur.execute(query, params)
            if returning:
                result = cur.fetchall()
                return result
            return None

    @track_query_stats
    def execute_transaction(
        self,
        queries_params: list[tuple[str, dict[str, Any] | None]],
        query_name: str | None = None,
    ) -> None:
        """Execute multiple queries within a single transaction.

        Args:
            queries_params (list[tuple[str, dict[str, Any] | None]]): List of (query, params) pairs.
            query_name (str | None): Optional query name for stats.

        Returns:
            None
        """
        self._log_query("Executing TRANSACTION", query_name=query_name)
        with self._connection() as (conn, cur):
            for query, params in queries_params:
                cur.execute(query, params)
            conn.commit()
