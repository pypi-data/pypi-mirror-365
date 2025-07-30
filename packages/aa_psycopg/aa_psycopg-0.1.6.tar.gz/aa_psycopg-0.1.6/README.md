# aa-psycopg

**Internal Partenamut library for PostgreSQL access using Psycopg 3.**  
Provides a simple and efficient interface for interacting with PostgreSQL using:

- A direct connection (`PostgreSQLConnection`)
- A connection pool (`PostgreSQLPool`)

Supports query execution (SELECT, INSERT, UPDATE, DELETE), transactions, schema caching, and query runtime statistics.

---

## Installation

```bash
pip install aa-psycopg
```

### Requirements

- Python **3.11+**
- [psycopg 3](https://www.psycopg.org/psycopg3/docs/)
- [psycopg_pool](https://www.psycopg.org/psycopg3/docs/api/pool.html)

---

## Features

- Easy-to-use wrapper for **psycopg3**.
- Connection pooling via **psycopg_pool**.
- Method for **chunked/streamed query execution** (`read_in_chunks`) to avoid loading large datasets into memory.
- Automatic **query runtime tracking**.
- Safe **connection string handling** (masks passwords in logs).
- Schema caching for executed queries.

---

## API overview

- `ping(retries=0, timeout=60, query_name="ping") -> bool`  
  Test database connectivity.
- `read(query, params=None, query_name=None) -> list[dict]`  
  Execute a SELECT query. Set `query_name` to track query runtime statistics.
- `read_in_chunks(query, params=None, chunk_size=500000, query_name=None) -> Generator[list[dict]]`  
  Execute a SELECT query and **yield results in batches** (streaming mode).
- `write(query, params=None, returning=False, query_name=None) -> list[dict] | None`  
  Execute INSERT/UPDATE/DELETE (optionally returning results). Set `query_name` to track query runtime statistics.
- `execute_transaction(queries_params, query_name=None)`  
  Run multiple queries inside a transaction. Set `query_name` to track query runtime statistics.
- `get_stats() -> dict`  
  Retrieve runtime stats (execution time & call count per `query_name`).
- `get_schema(query) -> list[psycopg.Column]`  
  Get schema for a previously executed query.

## Usage

### Direct Connection

```python
import logging
import json

from aa_psycopg.connection import PostgreSQLConnection

# Configure logging (can adjust level or handlers as needed)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

with PostgreSQLConnection(
    user="myuser",
    password="mypassword",
    host="localhost",
    port=5432,
    db="mydatabase"
) as client:
    # Check if database is alive
    client.ping()

    # Fetch results
    results = client.read("SELECT * FROM my_table", query_name="fetch_all")
    logger.info("Fetched results: %s", results[:5])

    # Stream rows in chunks (efficient for very large result sets)
    results_in_chunks = client.read_in_chunks(
        "SELECT * FROM big_table",
        chunk_size=5000,  # how many rows to fetch per chunk
        query_name="stream_big_table"
    )
    for i, chunk in result_in_chunks:
        logger.info("Fetched results of chunk %s: %s", i + 1, chunk[:5])

    # Write data
    client.write(
        "INSERT INTO my_table (name) VALUES (%(name)s)",
        params={"name": "example"},
        query_name="insert_row"
    )
    logger.info("Inserted row into my_table")

    # Transaction
    client.execute_transaction([
        ("INSERT INTO my_table (name) VALUES (%(name)s)", {"name": "row1"}),
        ("INSERT INTO my_table (name) VALUES (%(name)s)", {"name": "row2"}),
    ], query_name="bulk_insert")
    logger.info("Executed bulk insert transaction")

    # Query stats
    stats = client.get_stats()
    logger.info("Query stats: %s", json.dumps(stats, indent=4))

```

---

### Connection Pool

```python
import logging
import json
from aa_psycopg.pool import PostgreSQLPool

# Configure logging (can be redirected to CloudWatch or file)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

with PostgreSQLPool(
    user="myuser",
    password="mypassword",
    host="localhost",
    port=5432,
    db="mydatabase",
    min_size=1,
    max_size=5
) as client:
    # Check connectivity
    client.ping()

    # Fetch results
    results = client.read("SELECT * FROM users WHERE active = true", query_name="active_users")
    logger.info("Fetched results: %s", results[:5])

    # Stream results in chunks (efficient for very large result sets)
    results_in_chunks = client.read_in_chunks(
        "SELECT * FROM big_table",
        chunk_size=5000,  # how many rows to fetch per chunk
        query_name="stream_big_table"
    )
    for i, chunk in result_in_chunks:
        logger.info("Fetched results of chunk %s: %s", i + 1, chunk[:5])

    # Insert with RETURNING
    new_ids = client.write(
        "INSERT INTO users (name) VALUES (%(name)s) RETURNING id",
        params={"name": "Alice"},
        returning=True,
        query_name="insert_user"
    )
    logger.info("Inserted new user IDs: %s", new_ids)

    # Bulk transaction
    client.execute_transaction([
        ("UPDATE users SET active=false WHERE id=%(id)s", {"id": 1}),
        ("DELETE FROM users WHERE active=false", None),
    ], query_name="cleanup")
    logger.info("Executed cleanup transaction")

    # Stats (dump as JSON)
    stats = client.get_stats()
    logger.info("Query stats: %s", json.dumps(stats, indent=4))
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would
like to change.

Please make sure to update tests as appropriate.

---
