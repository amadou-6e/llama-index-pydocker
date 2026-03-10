# Qdrant Vector Store

`QdrantVectorStore` is a drop-in replacement for
[`llama_index.vector_stores.qdrant.QdrantVectorStore`](https://docs.llamaindex.ai/en/stable/api_reference/storage/vector_stores/qdrant/).
On a localhost URL it starts a Qdrant Docker container automatically.
On any other host it connects directly to the remote cluster without touching Docker.

## Installation

```bash
pip install "llama-index-pydocker[qdrant]"
```

## Basic usage

```python
from llama_index_pydocker import QdrantVectorStore

store = QdrantVectorStore(
    collection_name="docs",
    url="http://localhost:6333",
)
# Qdrant container is running. Store is ready.

# ... index documents and query ...

store.stop()  # remove the container when done
```

Use a context manager for automatic teardown:

```python
with QdrantVectorStore(collection_name="docs", url="http://localhost:6333") as store:
    storage_context = StorageContext.from_defaults(vector_store=store)
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
    results = index.as_retriever().retrieve("What is Qdrant?")
# Container removed here
```

## Routing

| URL host | Behaviour |
|---|---|
| `localhost` / `127.0.0.1` | Docker container started (or reused if already running) |
| Any other host | Direct connection — Docker is never contacted |

```python
# Remote Qdrant Cloud cluster — Docker is never started
store = QdrantVectorStore(
    collection_name="docs",
    url="https://my-cluster.qdrant.io:6333",
    api_key="sk-...",
)
```

## Docker configuration

Pass a `QdrantConfig` from `py-dockerdb` to control container behaviour:

```python
from docker_db import QdrantConfig
from llama_index_pydocker import QdrantVectorStore

cfg = QdrantConfig(
    container_name="qdrant-dev",
    volume_path="/data/qdrant",     # persist collection data across runs
    vector_size=768,
    retries=20,
    delay=2,
)

store = QdrantVectorStore(
    collection_name="docs",
    url="http://localhost:6333",
    docker_config=cfg,
)
```

Key `QdrantConfig` fields:

| Field | Purpose |
|---|---|
| `container_name` | Fixed name — reuses an existing container if already running |
| `volume_path` | Host directory for persistent Qdrant storage |
| `vector_size` | Default vector dimension for the collection |
| `retries` / `delay` | Startup polling — increase for slow machines |
| `image_name` | Override the Qdrant Docker image tag |

## Full example

See the [Qdrant notebook](../../usage/qdrant_example.ipynb) for a complete workflow:
document indexing, retrieval validation, context manager teardown, and Qdrant Cloud
passthrough.
