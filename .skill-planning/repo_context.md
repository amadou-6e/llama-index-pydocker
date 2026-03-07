# Repo Context: llama-index-pydocker

## Identity

- **Package name:** `llama-index-pydocker`
- **PyPI name:** `llama-index-pydocker`
- **Version:** 0.1.0
- **Author:** Amadou Wolfgang Cisse
- **License:** MIT
- **Python:** 3.10+
- **Repo:** https://github.com/amadou-6e/llama-index-pydocker

## What It Does (one sentence)

Drop-in replacements for LlamaIndex store classes that automatically start a Docker container when the connection URL resolves to localhost, and pass through transparently to the real upstream class when pointing at a remote endpoint.

## Tagline (existing)

> "LlamaIndex store wrappers that spin up Docker containers automatically — one import swap away."

## Core Value Proposition

- **One import change.** Same class name, same kwargs as LlamaIndex originals.
- **Automatic localhost detection.** URL → localhost → Docker starts. URL → remote → nothing Docker-related runs.
- **Context-manager support.** Container torn down on exit.
- **Production passthrough.** Swap to a cloud URL — library is invisible.

## Supported Stores

| Class | Backend | py-dockerdb config |
|---|---|---|
| `Neo4jGraphStore` | Neo4j | `Neo4jConfig` |
| `PGVectorStore` | PostgreSQL + pgvector | `PostgresConfig` |
| `QdrantVectorStore` | Qdrant | `QdrantConfig` |
| `OpensearchVectorStore` | OpenSearch | `OpenSearchConfig` |

## Key Dependencies

- `py-dockerdb` (Docker provisioning parent project)
- `llama-index-core`
- Optional extras: `neo4j`, `postgres`, `qdrant`, `opensearch`, `ollama`, `all`

## Use-Case Patterns (from README)

1. **Local GraphRAG prototype** — Neo4j container, `KnowledgeGraphIndex`, automatic teardown
2. **pgvector RAG on localhost** — Postgres + pgvector, `VectorStoreIndex`, no terminal needed
3. **Qdrant / OpenSearch experiments** — same API, swap backends by changing URL
4. **Production passthrough** — cloud endpoint → library does nothing Docker-related

## Routing Logic

```
url
  └── is_localhost? → YES → start/reuse Docker container → connect
                   → NO  → passthrough (behaves like upstream LlamaIndex class)
```

## Stack Signals

- AI / LLM tooling (LlamaIndex ecosystem)
- RAG (Retrieval-Augmented Generation)
- Vector stores, graph stores
- Docker-based local development
- Notebook-friendly (usage/ notebooks provided)

## Existing README Quality

Strong, developer-terse. Clear "before/after" import examples. Good coverage of all four stores. No PyPI classifiers set yet. No explicit GitHub topics.

## Gaps / Missing Inputs

- No `usage/*.ipynb` files visible (referenced in README as existing)
- No existing PyPI classifiers in pyproject.toml
- No existing GitHub topics
- Package not yet published on PyPI (not found in search)
