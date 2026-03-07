# pgvector Store

`PGVectorStore` is a drop-in replacement for
[`llama_index.vector_stores.postgres.PGVectorStore`](https://docs.llamaindex.ai/en/stable/api_reference/storage/vector_stores/postgres/).
On a localhost connection string it starts a PostgreSQL container with the
`pgvector` extension automatically.
On any other host it connects directly to the remote database without touching Docker.

## Installation

```bash
pip install "llama-index-pydocker[postgres]"
```

## Basic usage

```python
from llama_index_pydocker import PGVectorStore

store = PGVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/vectordb",
    embed_dim=1536,
)
# Postgres + pgvector container is running. Store is ready.

# ... index documents and query ...

store.stop()  # remove the container when done
```

Use a context manager for automatic teardown:

```python
with PGVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/vectordb",
    embed_dim=1536,
) as store:
    storage_context = StorageContext.from_defaults(vector_store=store)
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
    results = index.as_retriever().retrieve("What is pgvector?")
# Container removed here
```

## Routing

| Connection string host | Behaviour |
|---|---|
| `localhost` / `127.0.0.1` | Docker container started (or reused if already running) |
| Any other host | Direct connection — Docker is never contacted |

```python
# Remote RDS or Supabase — Docker is never started
store = PGVectorStore(
    connection_string="postgresql://user:pass@my-rds.amazonaws.com:5432/vectordb",
    embed_dim=1536,
)
```

## Docker configuration

Pass a `PostgresConfig` from `py-dockerdb` to control container behaviour:

```python
from docker_db import PostgresConfig
from llama_index_pydocker import PGVectorStore

cfg = PostgresConfig(
    user="user",
    password="pass",
    database="vectordb",
    container_name="pg-dev",
    volume_path="/data/postgres",   # persist data across runs
    retries=20,
    delay=3,
)

store = PGVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/vectordb",
    embed_dim=1536,
    docker_config=cfg,
)
```

Key `PostgresConfig` fields:

| Field | Purpose |
|---|---|
| `user` / `password` / `database` | Postgres credentials (must match the connection string) |
| `container_name` | Fixed name — reuses an existing container if already running |
| `volume_path` | Host directory for persistent Postgres data |
| `retries` / `delay` | Startup polling — increase for slow machines |
| `image_name` | Override the pgvector Docker image tag |

## Full example

See the [pgvector RAG notebook](../../usage/pgvector_example.ipynb) for a complete
workflow: document indexing, retrieval validation, context manager teardown, and remote
passthrough.
