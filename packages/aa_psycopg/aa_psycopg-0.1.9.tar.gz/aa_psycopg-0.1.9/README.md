# aa-psycopg

**Internal Partenamut library for PostgreSQL access using Psycopg 3.**  
Provides a simple and efficient interface for interacting with PostgreSQL using:

- A direct connection (`PostgreSQLConnection`)
- A connection pool (`PostgreSQLPool`)

Supports query execution (SELECT, INSERT, UPDATE, DELETE), transactions, schema caching, and query runtime statistics.

---

## Installation

If you want to install only psycopg functionality (see: [Usage of Psycopg for Direct Connection or Pooling](#usage-of-psycopg-for-direct-connection-or-pooling))

```bash
pip install aa-psycopg
```

If you also want to install features for validating query configuration with pydantic (see [Usage of QueryConfig for Query Management](#usage-of-queryconfig-for-query-management))

```bash
pip install aa-psycopg[pydantic]
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
- `read_in_chunks(query, params=None, chunk_size=500000, query_name=None) -> Iterator[list[dict]]`  
  Execute a SELECT query and **yield results in batches** (streaming mode).
- `write(query, params=None, returning=False, query_name=None) -> list[dict] | None`  
  Execute INSERT/UPDATE/DELETE (optionally returning results). Set `query_name` to track query runtime statistics.
- `execute_transaction(queries_params, query_name=None)`  
  Run multiple queries inside a transaction. Set `query_name` to track query runtime statistics.
- `get_stats() -> dict`  
  Retrieve runtime stats (execution time & call count per `query_name`).  
  For the PostgreSQLPool only: also includes pool stats if available.
- `get_schema(query) -> list[psycopg.Column]`  
  Get schema for a previously executed query.
- `connection() -> ContextManager[psycopg.Connection]`  
  For the PostgreSQLPool: Acquire a **temporary connection** from the pool.  
  For the PostgreSQLConnection: Get the **current connection**.

## Usage of Psycopg for Direct Connection or Pooling

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
    for i, chunk in client.read_in_chunks(
        "SELECT * FROM big_table",
        chunk_size=5000,  # how many rows to fetch per chunk
        query_name="stream_big_table",
    ):
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

    # Get current active connection for specific usage (e.g. use pandas to query)
    with client.connection() as conn:
      df = pd.read_sql("SELECT * FROM users", con=conn)

    # Query stats
    stats = client.get_stats()
    logger.info("Query stats: %s", json.dumps(stats, indent=4))

```

> **⚠️ Warning**  
> Only stay in the `with` block as long as you need your connection to be open!  
> Keep in mind that the connection will remain open as long as the code is running in the with block!

---

### Connection Pool

```python
import logging
import json

import pandas as pd

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
    min_size=0,  # pool starts with 0 connections, only creating connection with first query
    max_size=1  # pool will not exceed 1 connection
) as client:
    # Check connectivity
    client.ping()

    # Fetch results
    results = client.read("SELECT * FROM users WHERE active = true", query_name="active_users")
    logger.info("Fetched results: %s", results[:5])

    # Stream results in chunks (efficient for very large result sets)
    for i, chunk in client.read_in_chunks(
        "SELECT * FROM big_table",
        chunk_size=5000,  # how many rows to fetch per chunk
        query_name="stream_big_table",
    ):
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

    # Acquiring temporary connection from the pool for specific usage (e.g. use pandas to query)
    with client.connection() as conn:
      df = pd.read_sql("SELECT * FROM users", con=conn)

    # Stats (queries + pool) (dump as JSON)
    stats = client.get_stats()
    logger.info("Query stats + Pool stats: %s", json.dumps(stats, indent=4))
```

> **⚠️ Warning**  
> Only stay in the `with` block as long as you need your connection pool to be open!  
> Keep in mind that the pool will remain open as long as the code is running in the with block!

---

## Usage of `QueryConfig` for Query Management

`QueryConfig` is a Pydantic-based configuration class that allows you to manage SQL queries
and their parameters from either a `.sql` file or a raw query string.
It can also load configurations from YAML files for easier organization.

---

### Installation of optional dependency

`QueryConfig` is **optional**. To enable it, install the extra dependencies:

```bash
uv pip install aa-psycopg[pydantic]
```

This will pull in `pydantic`.

---

### Basic Usage

#### Load from a `.sql` file

```python
from pathlib import Path
from aa_psycopg.query_config import QueryConfig
cfg = QueryConfig(path_query=Path("queries/get_users.sql"), params={"user_id": 123})
print(cfg.query)   # Contents of the SQL file
print(cfg.params)  # {"user_id": 123}
```

#### Load directly from a raw query string

```python
from aa_psycopg.query_config import QueryConfig
cfg = QueryConfig(query="SELECT * FROM users WHERE id = %(user_id)s", params={"user_id": 123})
print(cfg.query)  # The query string
```

---

### Loading from YAML

You can define a query configuration in a `.yaml` file:

```yaml
# query_config.yaml
path_query: queries/get_users.sql
params:
  user_id: 123
```

OR

```yaml
# query_config.yaml
query: |
  SELECT * FROM users 
  WHERE id = %(user_id)s
params:
  user_id: 123
```

Load it using `from_yaml`:

```python
from aa_psycopg.query_config import QueryConfig
cfg = QueryConfig.from_yaml("query_config.yaml")
print(cfg.query)   # SQL contents from the file
print(cfg.params)  # {"user_id": 123}
```

---

### Validation

- You must provide **exactly one of** `query` or `path_query`.
- If a `.sql` file is given, it must exist and have a `.sql` extension.
- All parameters defined in the SQL (using `%(param)s` style) must match the keys in `params`.
  If they don’t, a `ValueError` is raised with details. -->
"""

```python
# Example query with a parameter mismatch (SQL expects "id", params gives "user_id")
from aa_psycopg.query_config import QueryConfig
try:
    cfg = QueryConfig(
        query="SELECT * FROM users WHERE id = %(id)s",
        params={"user_id": 123},  # This will cause a validation error
    )
except ValueError as e:
    print("Validation failed, mismatch detected!")
    print(e)
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would
like to change.

Please make sure to update tests as appropriate.

---
