# Neo4j Graph Store

`Neo4jGraphStore` is a drop-in replacement for
[`llama_index.graph_stores.neo4j.Neo4jGraphStore`](https://docs.llamaindex.ai/en/stable/api_reference/storage/graph_stores/neo4j/).
On a localhost URL it starts a Neo4j Docker container automatically.
On any other host it connects directly to the remote instance without touching Docker.

## Installation

```bash
pip install "llama-index-pydocker[neo4j]"
```

## Basic usage

```python
from llama_index_pydocker import Neo4jGraphStore

store = Neo4jGraphStore(
    url="bolt://localhost:7687",
    password="test",
)
# Neo4j container is running. Store is ready.

# ... build your index or run Cypher ...

store.stop()  # remove the container when done
```

Use a context manager for automatic teardown:

```python
with Neo4jGraphStore(url="bolt://localhost:7687", password="test") as store:
    storage_context = StorageContext.from_defaults(graph_store=store)
    index = KnowledgeGraphIndex.from_documents(docs, storage_context=storage_context)
    response = index.as_query_engine().query("Who introduced the Transformer?")
# Container removed here
```

## Routing

| URL host | Behaviour |
|---|---|
| `localhost` / `127.0.0.1` | Docker container started (or reused if already running) |
| Any other host | Direct connection — Docker is never contacted |

```python
# Remote Neo4j Aura instance — Docker is never started
store = Neo4jGraphStore(
    url="bolt+ssc://my-aura.databases.neo4j.io:7687",
    password="<aura-password>",
)
```

## Docker configuration

Pass a `Neo4jConfig` from `py-dockerdb` to control container behaviour:

```python
from docker_db import Neo4jConfig
from llama_index_pydocker import Neo4jGraphStore

cfg = Neo4jConfig(
    container_name="neo4j-dev",
    volume_path="/data/neo4j",          # persist data across runs
    env_vars={"NEO4J_PLUGINS": '["apoc"]'},
    retries=15,
    delay=5,
)

store = Neo4jGraphStore(
    url="bolt://localhost:7687",
    password="test",
    docker_config=cfg,
)
```

The `port` field on `docker_config` is always overridden by the port parsed from
`url`, so the container port and connection port are always in sync.

Key `Neo4jConfig` fields:

| Field | Purpose |
|---|---|
| `container_name` | Fixed name — reuses an existing container if already running |
| `volume_path` | Host directory for persistent Neo4j data |
| `env_vars` | Extra environment variables (e.g. APOC plugin activation) |
| `retries` / `delay` | Startup polling — increase for slow machines |
| `image_name` | Override the Neo4j Docker image tag |

## Full example

See the [Neo4j GraphRAG notebook](../../usage/neo4j_graphstore_example.ipynb) for a
complete workflow: Cypher queries, `KnowledgeGraphIndex`, context manager teardown,
and remote passthrough.
