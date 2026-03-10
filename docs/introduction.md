# llama-index-pydocker

LlamaIndex store wrappers that spin up Docker containers automatically — one import swap away.

```bash
pip install llama-index-pydocker
```

Every LlamaIndex GraphRAG and RAG tutorial starts the same way: run a Docker command,
wait for the container, confirm the port, then write your pipeline.
`llama-index-pydocker` removes those steps.

Pass a `localhost` URL and the right Docker container — Neo4j, pgvector, Qdrant, or
OpenSearch — starts automatically via
[py-dockerdb](https://github.com/amadou-6e/docker-db). Pass a cloud URL and the
wrapper disappears: the class behaves identically to the upstream LlamaIndex original.

---

## Who is this for

**Data scientists and research engineers building GraphRAG pipelines.**
The LlamaIndex GraphRAG cookbook tells you to run a `docker run` command before writing
any pipeline code. With `llama-index-pydocker`, that step does not exist.
Import `Neo4jGraphStore` from `llama_index_pydocker` instead of
`llama_index.graph_stores.neo4j` and a local Neo4j container is ready by the time
your constructor returns. When you are ready to switch to Neo4j Aura or any hosted
instance, change the URL — nothing else in your code changes.

**ML engineers building RAG pipelines with pgvector, Qdrant, or OpenSearch.**
The same pattern applies to every supported store. Prototype against a local container.
Deploy against a managed cloud endpoint. One URL change, no code change, no
`docker-compose.yml` to maintain alongside your application code.

---

## What you can do with llama-index-pydocker

**Run local GraphRAG without leaving Python.**
Provision a Neo4j container, build a `KnowledgeGraphIndex`, and run community-based
GraphRAG queries — all from a notebook or script, with no terminal required.
The container is cleaned up when you call `store.stop()` or exit a `with` block.

**Prototype a pgvector RAG pipeline on localhost.**
Start Postgres with the `pgvector` extension, index documents through
`PGVectorStore`, and validate retrieval — then switch `connection_string` to an RDS
or Supabase DSN to deploy. The `PGVectorStore` object is identical in both cases.

**Run Qdrant or OpenSearch experiments with the same API.**
Swap backends by changing the URL and the `docker_config` type. Each store follows the
same localhost-detection rule: local URL starts the container, remote URL connects
directly.

**Use the upstream LlamaIndex class for production, unchanged.**
`llama-index-pydocker` is transparent on non-localhost URLs. The same import works in
CI and production without any conditional logic or environment checks in your code.

---

## Where to go next

- {doc}`quick_start` — build and query a local Neo4j GraphRAG index in under ten lines
- [Neo4j GraphRAG notebook](../usage/neo4j_graphstore_example.ipynb) — full GraphRAG workflow with `KnowledgeGraphIndex`
- [pgvector RAG notebook](../usage/pgvector_example.ipynb) — index documents and validate retrieval with `PGVectorStore`
- [Qdrant notebook](../usage/qdrant_example.ipynb)
- [OpenSearch notebook](../usage/opensearch_example.ipynb)
