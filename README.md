# llama-index-pydocker

*LlamaIndex store wrappers that spin up Docker containers automatically — one import swap away.*

[![Build](https://img.shields.io/github/actions/workflow/status/amadou-6e/llama-index-pydocker/cicd.yml?branch=main&label=tests)](https://github.com/amadou-6e/llama-index-pydocker/actions)
[![PyPI](https://img.shields.io/pypi/v/llama-index-pydocker)](https://pypi.org/project/llama-index-pydocker/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](./LICENSE)

```bash
pip install llama-index-pydocker
```

`llama-index-pydocker` wraps every LlamaIndex store class that needs a running
database. Pass a `localhost` URL and the right Docker container starts
automatically via [`py-dockerdb`](https://github.com/amadou-6e/docker-db). Pass a
cloud URL and the wrapper is invisible — nothing Docker-related ever runs.

Switch from a local Neo4j graph store to a hosted one without touching your
pipeline. Prototype a pgvector RAG index on your laptop, deploy to RDS with one
URL change. Give every student an isolated vector store in seconds.

## When to use this

- **Local GraphRAG prototype:** one import swap gives you a Neo4j container that
  LlamaIndex talks to directly, with automatic teardown via context manager.
- **pgvector RAG on localhost:** spin up Postgres + pgvector, run your retrieval
  pipeline, shut everything down — without ever opening a terminal.
- **Qdrant / OpenSearch experiments:** same pattern, same API. Swap backends by
  changing the URL and the `docker_config` type.
- **Production passthrough:** point any store at a cloud endpoint and
  `llama-index-pydocker` behaves exactly like the upstream LlamaIndex class.

## Supported Stores

[![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?logo=neo4j&logoColor=white)](https://neo4j.com/docs/)
[![PostgreSQL](https://img.shields.io/badge/pgvector-4169E1?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Qdrant](https://img.shields.io/badge/Qdrant-FF6534?logo=qdrant&logoColor=white)](https://qdrant.tech/documentation/)
[![OpenSearch](https://img.shields.io/badge/OpenSearch-005EB8?logo=opensearch&logoColor=white)](https://opensearch.org/docs/)

## Prerequisites

- Python 3.10+ · Docker running · `py-dockerdb` installed

## Installation

```bash
pip install llama-index-pydocker                   # core only
pip install "llama-index-pydocker[neo4j]"          # + Neo4j graph store
pip install "llama-index-pydocker[postgres]"       # + pgvector store
pip install "llama-index-pydocker[qdrant]"         # + Qdrant vector store
pip install "llama-index-pydocker[opensearch]"     # + OpenSearch vector store
pip install "llama-index-pydocker[all]"            # everything
```

## Usage

Change one import. Everything else stays the same.

### Neo4j Graph Store

```python
# Before
from llama_index.graph_stores.neo4j import Neo4jGraphStore

# After — Docker container starts automatically on localhost URLs
from llama_index_pydocker import Neo4jGraphStore
```

```python
from llama_index_pydocker import Neo4jGraphStore

store = Neo4jGraphStore(
    url="bolt://localhost:7687",
    password="test",
)
# Container is up, store is ready
store.stop()          # remove container when done
```

Use a context manager for automatic teardown:

```python
with Neo4jGraphStore(url="bolt://localhost:7687", password="test") as store:
    index = KnowledgeGraphIndex.from_documents(docs, storage_context=..., graph_store=store)
    response = query_engine.query("Who founded Neo4j?")
# Container removed here
```

Point at a cloud instance — Docker is never touched:

```python
store = Neo4jGraphStore(
    url="bolt://my-aura-instance.databases.neo4j.io:7687",
    password="secret",
)
```

### pgvector Store

```python
from llama_index_pydocker import PGVectorStore

store = PGVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/vectordb",
    embed_dim=1536,
)
store.stop()
```

Override Docker config (volume, retries, container name, …):

```python
from docker_db import PostgresConfig
from llama_index_pydocker import PGVectorStore

cfg = PostgresConfig(
    user="user", password="pass", database="vectordb",
    project_name="my-rag",
    retries=30,
)

with PGVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/vectordb",
    embed_dim=1536,
    docker_config=cfg,
) as store:
    index = VectorStoreIndex.from_documents(docs, vector_store=store)
    print(index.as_query_engine().query("What is pgvector?"))
```

### Qdrant Vector Store

```python
from llama_index_pydocker import QdrantVectorStore

with QdrantVectorStore(
    collection_name="docs",
    url="http://localhost:6333",
) as store:
    index = VectorStoreIndex.from_documents(docs, vector_store=store)
    print(index.as_query_engine().query("What is Qdrant?"))
```

Remote cluster — no Docker:

```python
store = QdrantVectorStore(
    collection_name="docs",
    url="https://my-cluster.qdrant.io:6333",
    api_key="sk-...",
)
```

### OpenSearch Vector Store

```python
from llama_index_pydocker import OpensearchVectorStore

with OpensearchVectorStore(
    index_name="docs",
    endpoint="http://localhost:9200",
    embed_dim=1536,
) as store:
    index = VectorStoreIndex.from_documents(docs, vector_store=store)
    print(index.as_query_engine().query("What is OpenSearch?"))
```

## Routing logic

```
url / connection_string / endpoint
        │
        ▼
 is_localhost(host)?
   ┌────┴────┐
  YES        NO
   │          │
   ▼          ▼
 create    passthrough
 Docker    (behaves like
container  upstream class)
```

Port is always inferred from the URL, even when a `docker_config` is supplied.

## More examples

Full runnable notebooks are in [`usage/`](./usage/):

[Neo4j / GraphRAG](./usage/neo4j_graphstore_example.ipynb) · [pgvector RAG](./usage/pgvector_example.ipynb)
· [Qdrant](./usage/qdrant_example.ipynb) · [OpenSearch](./usage/opensearch_example.ipynb)

## Development

```bash
git clone https://github.com/amadou-6e/llama-index-pydocker.git
cd llama-index-pydocker
pip install -e ".[all]"
```

## Testing

```bash
python -m pytest tests/test_utils.py
python -m pytest tests/test_neo4j.py
python -m pytest tests/test_postgres.py
python -m pytest tests/test_qdrant.py
python -m pytest tests/test_opensearch.py
```

## Contributing

PRs welcome. Include tests for behaviour changes.

## License

MIT License. See `LICENSE`.
