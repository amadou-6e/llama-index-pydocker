# Quickstart

By the end of this page you will have a local Neo4j container running, a
`KnowledgeGraphIndex` built against it, and a GraphRAG query returning results — all
without running a single Docker command in your terminal.

## Prerequisites

- Python 3.10 or later
- Docker Desktop must be running

## Installation

```bash
pip install "llama-index-pydocker[neo4j]"
```

For other stores, replace `neo4j` with `postgres`, `qdrant`, `opensearch`, or use `all`
to install every backend.

## Your first llama-index-pydocker workflow

The import below replaces `from llama_index.graph_stores.neo4j import Neo4jGraphStore`.
Everything else — constructor signature, method names, LlamaIndex integration — stays
the same.

```python
from llama_index_pydocker import Neo4jGraphStore

store = Neo4jGraphStore(
    url="bolt://localhost:7687",
    password="test",
)
# Neo4j container is running. Store is ready.
```

Build a `KnowledgeGraphIndex` and query it:

```python
from llama_index.core import StorageContext, KnowledgeGraphIndex
from llama_index.core.schema import Document

documents = [
    Document(text="Vaswani introduced the Transformer architecture in 2017."),
    Document(text="The Transformer replaced recurrent networks for sequence modelling."),
]

storage_context = StorageContext.from_defaults(graph_store=store)

index = KnowledgeGraphIndex.from_documents(
    documents,
    storage_context=storage_context,
    max_triplets_per_chunk=3,
    include_embeddings=False,
)

query_engine = index.as_query_engine(
    include_text=True,
    retriever_mode="keyword",
)

response = query_engine.query("What did Vaswani introduce?")
print(response)
```

Remove the container when you are done:

```python
store.stop()
```

Or use a context manager for automatic teardown:

```python
with Neo4jGraphStore(url="bolt://localhost:7687", password="test") as store:
    storage_context = StorageContext.from_defaults(graph_store=store)
    index = KnowledgeGraphIndex.from_documents(docs, storage_context=storage_context)
    response = index.as_query_engine().query("Who introduced the Transformer?")
# Container removed here automatically
```

## What just happened

`llama-index-pydocker` inspected the `url` argument. Because the host resolves to
`localhost`, it called `py-dockerdb` to start (or reuse) a Neo4j Docker container on
port 7687 before passing control to the upstream `Neo4jGraphStore` constructor.
The `KnowledgeGraphIndex` then wrote knowledge triplets directly to that container
through the same LlamaIndex store interface it would use against any other Neo4j
instance. When `stop()` was called, the container was removed.

Point `url` at a hosted instance — `bolt://my-aura.databases.neo4j.io:7687` — and none
of the Docker logic runs. The object behaves identically to the upstream LlamaIndex
class.

## Next steps

- [Neo4j GraphRAG notebook](../usage/neo4j_graphstore_example.ipynb) — full workflow:
  Cypher queries, `KnowledgeGraphIndex`, context manager teardown, remote passthrough
- [pgvector RAG notebook](../usage/pgvector_example.ipynb) — `PGVectorStore`, document
  indexing, retrieval validation, RDS passthrough
- [Qdrant notebook](../usage/qdrant_example.ipynb) — `QdrantVectorStore` with hybrid
  search and remote cluster passthrough
- [OpenSearch notebook](../usage/opensearch_example.ipynb) — `OpensearchVectorStore`
  with local and hosted OpenSearch Service endpoints
