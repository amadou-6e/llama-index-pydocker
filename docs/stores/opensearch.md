# OpenSearch Vector Store

`OpensearchVectorStore` is a drop-in replacement for
[`llama_index.vector_stores.opensearch.OpensearchVectorStore`](https://docs.llamaindex.ai/en/stable/api_reference/storage/vector_stores/opensearch/).
On a localhost endpoint it starts an OpenSearch Docker container automatically.
On any other host it connects directly to the remote cluster without touching Docker.

> **Note:** The OpenSearch Docker image is approximately 1 GB and takes 1-2 minutes
> to become ready on first pull.

## Installation

```bash
pip install "llama-index-pydocker[opensearch]"
```

## Basic usage

```python
from llama_index_pydocker import OpensearchVectorStore

store = OpensearchVectorStore(
    index_name="docs",
    endpoint="http://localhost:9200",
    embed_dim=1536,
)
# OpenSearch container is running. Store is ready.

# ... index documents and query ...

store.stop()  # remove the container when done
```

Use a context manager for automatic teardown:

```python
with OpensearchVectorStore(
    index_name="docs",
    endpoint="http://localhost:9200",
    embed_dim=1536,
) as store:
    storage_context = StorageContext.from_defaults(vector_store=store)
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
    results = index.as_retriever().retrieve("How does hybrid search work?")
# Container removed here
```

## Routing

| Endpoint host | Behaviour |
|---|---|
| `localhost` / `127.0.0.1` | Docker container started (or reused if already running) |
| Any other host | Direct connection — Docker is never contacted |

```python
# Amazon OpenSearch Service — Docker is never started
store = OpensearchVectorStore(
    index_name="docs",
    endpoint="https://my-cluster.us-east-1.es.amazonaws.com",
    embed_dim=1536,
)
```

## Docker configuration

Pass an `OpenSearchConfig` from `py-dockerdb` to control container behaviour:

```python
from docker_db import OpenSearchConfig
from llama_index_pydocker import OpensearchVectorStore

cfg = OpenSearchConfig(
    container_name="opensearch-dev",
    volume_path="/data/opensearch",  # persist index data across runs
    retries=30,
    delay=3,
)

store = OpensearchVectorStore(
    index_name="docs",
    endpoint="http://localhost:9200",
    embed_dim=1536,
    docker_config=cfg,
)
```

Key `OpenSearchConfig` fields:

| Field | Purpose |
|---|---|
| `container_name` | Fixed name — reuses an existing container if already running |
| `volume_path` | Host directory for persistent OpenSearch data |
| `retries` / `delay` | Startup polling — increase to 30+ for the large image |
| `image_name` | Override the OpenSearch Docker image tag |

## Full example

See the [OpenSearch notebook](../../usage/opensearch_example.ipynb) for a complete
workflow: document indexing, retrieval validation, context manager teardown, and
Amazon OpenSearch Service passthrough.
