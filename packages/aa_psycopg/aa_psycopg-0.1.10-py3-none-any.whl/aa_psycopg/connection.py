import functools
import logging
import time

from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Callable, Generator, Iterator, Self
from urllib.parse import quote_plus

import psycopg

from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


def track_query_stats(method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(self: "PostgreSQLConnection", *args, **kwargs):
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


class PostgreSQLConnection:
    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int,
        db: str,
        **kwargs: Any,
    ) -> None:
        """Initialize a PostgreSQL connection. Connection is lazily openened in context manager.

        Args:
            user (str): Database username.
            password (str): Database password.
            host (str): Database host.
            port (int): Database port.
            db (str): Database name.
            **kwargs: Additional connection parameters.

        Usage:
            with PostgreSQLConnection(user, password, host, port, db) as client:
                client.ping()
                res = client.read("SELECT * FROM my_table", query_name="my_query")
        """
        safe_password = quote_plus(password)
        self._dsn = f"postgresql://{user}:{safe_password}@{host}:{port}/{db}?client_encoding=UTF8"
        self._dsn_masked: str = f"postgresql://{user}:***@{host}:{port}/{db}"
        self._conn: psycopg.Connection | None = None
        self._in_context: bool = False
        self._query_stats: defaultdict[str, dict[str, float | int]] = defaultdict(
            lambda: {"total_time": 0.0, "count": 0}
        )
        self._schemas: dict[str, list[psycopg.Column]] = {}
        self._extra_connection_kwargs = kwargs
        logger.info("Initialized Postgres client (connection not opened yet): %s", self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._dsn_masked})"

    def __enter__(self) -> Self:
        if self._conn is None:
            self._conn = psycopg.connect(self._dsn, **self._extra_connection_kwargs)
            logger.info("Connection opened: %s", self)
        self._in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._in_context = False
        if self._conn is not None:
            try:
                if exc_type is None:
                    self._conn.commit()
                    logger.info("Transaction committed: %s", self)
                else:
                    self._conn.rollback()
                    logger.warning("Transaction rolled back due to exception: %s", self)
            except Exception as e:
                logger.error("Error during commit/rollback: %s", e)
            finally:
                logger.info("Closing connection: %s", self)
                self._conn.close()
                self._conn = None

    @property
    def connection(self) -> Generator[psycopg.Connection, None, None]:
        """Get the current connection object."""
        self._ensure_in_context()
        return self._conn

    def get_stats(self) -> dict[str, dict[str, float | int]]:
        return dict(self._query_stats)

    def get_schema(self, query: str) -> list[psycopg.Column]:
        schema = self._schemas.get(query)
        if schema is None:
            raise ValueError(
                f"No schema found for query: {query}, "
                "please execute the `read()` method first."
            )
        return schema

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
                with self._cursor() as cur:
                    cur.execute("SELECT 1")
                    self._log_query("Ping executed successfully", query_name=query_name)
                    return True
            except Exception as e:
                logger.error(
                    "Postgres ping failed (attempt %d/%d): %s", attempt + 1, retries, e
                )
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
        self._log_query("Executing READ query", query_name=query_name)
        with self._cursor() as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            self._schemas[query] = cur.description
            return results

    @track_query_stats
    def read_in_chunks(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        chunk_size: int = 500000,
        query_name: str | None = None,
    ) -> Iterator[list[dict[str, Any]]]:
        """
        Execute a READ query and yield results in chunks.

        Args:
            query (str): SQL query.
            params (dict[str, Any] | None): Query parameters.
            chunk_size (int): Number of rows to fetch per batch.
            query_name (str | None): Optional query name for tracking.

        Yields:
            Iterator[list[dict[str, Any]]]: Batches of rows as dictionaries.
        """
        self._log_query(
            f"Executing READ query in chunks (chunk_size={chunk_size})",
            query_name=query_name,
        )

        with self._cursor() as cur:
            cur.execute(query, params)
            self._schemas[query] = cur.description

            count_rows = 0
            count_chunks = 0
            while True:
                rows = cur.fetchmany(chunk_size)
                if not rows:
                    break
                count_rows += len(rows)
                count_chunks += 1
                yield rows
        logger.info(
            "Read in chunks completed on (query_name=%s): %s rows in %d chunks",
            query_name,
            count_rows,
            count_chunks,
        )

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
        self._log_query("Executing WRITE query", query_name=query_name)
        with self._cursor() as cur:
            cur.execute(query, params)
            if returning:
                return cur.fetchall()
            return None

    def _ensure_in_context(self) -> None:
        if not self._in_context:
            raise RuntimeError(
                f"{self.__class__.__name__} must be used within a 'with' context manager block.\n"
                "Example:\n"
                f"  with {self.__class__.__name__}(...) as client:\n"
                "      client.read(..., query_name='my_query')"
            )

    @contextmanager
    def _cursor(
        self,
    ) -> Generator[psycopg.Cursor, None, None]:
        self._ensure_in_context()
        try:
            with self._conn.cursor(row_factory=dict_row) as cur:
                yield self._conn, cur
        except psycopg.Error as e:
            logger.error("Database error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise

    def _log_query(self, msg: str, query_name: str | None = None) -> None:
        if query_name:
            logger.info("%s (query_name=%s) with %s ", msg, query_name, self)
        else:
            logger.info("%s on %s", msg, self)
