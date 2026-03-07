# Marketing Prose: llama-index-pydocker

**Target audience:** Data scientists and research engineers building GraphRAG and RAG pipelines with LlamaIndex — primarily Neo4j GraphRAG, with pgvector, Qdrant, and OpenSearch as secondary stores.
**Keyword targets:** `llamaindex neo4j docker python`, `graphrag local setup python`, `llamaindex docker`, `pgvector docker python llamaindex`, `llamaindex qdrant local`

---

## 1. README Hero Section

```markdown
# llama-index-pydocker

LlamaIndex store wrappers that spin up Docker containers automatically — one import swap away.

[![Build](https://img.shields.io/github/actions/workflow/status/amadou-6e/llama-index-pydocker/cicd.yml?branch=main&label=tests)](https://github.com/amadou-6e/llama-index-pydocker/actions)
[![PyPI](https://img.shields.io/pypi/v/llama-index-pydocker)](https://pypi.org/project/llama-index-pydocker/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](./LICENSE)

```bash
pip install llama-index-pydocker
```

Every LlamaIndex GraphRAG and RAG tutorial starts the same way: run a Docker command, wait for the container, confirm the port, then write your pipeline. `llama-index-pydocker` removes those steps.

Pass a `localhost` URL and the right Docker container — Neo4j, pgvector, Qdrant, or OpenSearch — starts automatically via [`py-dockerdb`](https://github.com/amadou-6e/docker-db). Pass a cloud URL and the wrapper disappears: the class behaves identically to the upstream LlamaIndex original.

Build your GraphRAG index against a local Neo4j container. Deploy it against Neo4j Aura. Change one line — the URL.
```

---

## 2. PyPI Long Description Intro

`llama-index-pydocker` auto-provisions Docker containers for LlamaIndex stores — Neo4j, pgvector, Qdrant, and OpenSearch — when the connection URL resolves to localhost. Point at a remote or cloud endpoint and the library does nothing: the class is a transparent pass-through to the upstream LlamaIndex store.

**The problem it solves:** building a local GraphRAG pipeline with LlamaIndex and Neo4j requires a running Neo4j container. Setting one up manually — `docker run`, port-mapping, environment variables, readiness checks — is infrastructure work that interrupts the data science workflow. The same pattern repeats for every store: pgvector needs a Postgres + pgvector container, Qdrant needs its own, OpenSearch needs its own. `llama-index-pydocker` handles all of it from within the Python import.

**What changes:** one import line. `Neo4jGraphStore`, `PGVectorStore`, `QdrantVectorStore`, and `OpensearchVectorStore` keep the same names and accept the same kwargs as their LlamaIndex originals. Context managers are supported for automatic container teardown.

**What doesn't change:** your pipeline code, your store configuration, your production deployment. Swap the URL from `bolt://localhost:7687` to your Aura endpoint — the library steps out of the way.

```python
# Before (requires running: docker run -p 7474:7474 -p 7687:7687 neo4j ...)
from llama_index.graph_stores.neo4j import Neo4jGraphStore

# After — container starts automatically on localhost URLs
from llama_index_pydocker import Neo4jGraphStore
```

Supported stores: Neo4j (GraphRAG, knowledge graphs), PostgreSQL + pgvector (vector RAG), Qdrant (vector search), OpenSearch (hybrid search). Python 3.10+. MIT license.

---

## 3. GitHub "About" One-Liner

LlamaIndex stores (Neo4j, pgvector, Qdrant, OpenSearch) that auto-start Docker containers on localhost. One import change. Remote URLs pass through unchanged.

---

## 4. Social Share Blurbs

### Twitter / X — GraphRAG angle (primary)
Every LlamaIndex + Neo4j GraphRAG tutorial starts with `docker run`. `llama-index-pydocker` skips that step entirely.

Change one import. Container starts automatically on localhost. Point at Neo4j Aura — it disappears.

`pip install llama-index-pydocker`

### Twitter / X — pgvector angle
Local pgvector RAG with LlamaIndex, without opening a terminal:

```python
from llama_index_pydocker import PGVectorStore
store = PGVectorStore(connection_string="postgresql://user:pass@localhost:5432/vectordb")
# Postgres + pgvector container is running
```

### Twitter / X — general
`llama-index-pydocker`: same LlamaIndex store class names, same kwargs, Docker managed for you on localhost.

Neo4j · pgvector · Qdrant · OpenSearch

### LinkedIn
Building local GraphRAG or RAG prototypes with LlamaIndex means setting up Docker containers before writing any pipeline code. `llama-index-pydocker` wraps that setup into the Python import itself.

localhost URL → container starts automatically
Remote/cloud URL → library is invisible, connects directly

Same store class names and kwargs as upstream LlamaIndex. Context managers for automatic teardown. Supports Neo4j, pgvector (PostgreSQL), Qdrant, and OpenSearch.

`pip install "llama-index-pydocker[neo4j]"`

---

## 5. Documentation Meta Description

llama-index-pydocker auto-provisions Neo4j, pgvector, Qdrant, and OpenSearch Docker containers from within a LlamaIndex store import. localhost URL → Docker starts. Remote URL → transparent passthrough. No manual docker run. No docker-compose. Python 3.10+.

---

## 6. GitHub Topics

```
llamaindex
graphrag
neo4j
pgvector
qdrant
opensearch
docker
rag
knowledge-graph
vector-store
llm
python
local-development
```

---

## 7. PyPI Classifiers

```toml
[project]
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "Topic :: Scientific/Engineering :: Artificial Intelligence",
  "Topic :: Database",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Operating System :: OS Independent",
]
```

---

## Audience Cards Considered

### Audience A — ML Engineers / AI Application Developers
**Who:** Python developers building full-stack RAG pipelines, already committed to a specific production store (Neo4j, pgvector, Qdrant, OpenSearch).
**Pain point:** Manual Docker setup before every local dev session. Context switching between terminal and IDE. Risk of picking a local stand-in store (Chroma, Milvus Lite) with different behavior from production.
**Framing:** "Same store, zero setup — prototype to production in one import swap."
**Channels:** GitHub, PyPI, LlamaHub, LlamaIndex Discord, dev.to.
**Keywords:** `llamaindex docker`, `pgvector docker python llamaindex`, `llamaindex qdrant local`.
**Status:** Secondary audience — addressed by the pass-through architecture and multi-store coverage.

### Audience B — Data Scientists / Research Engineers (CONFIRMED PRIMARY)
**Who:** Researchers and data scientists using LlamaIndex for knowledge graph construction, GraphRAG, and document understanding. Technically proficient but not primarily infrastructure engineers.
**Pain point:** GraphRAG with Neo4j is the most powerful LlamaIndex pattern, but local setup requires Docker management — infrastructure work that interrupts the data science workflow.
**Framing:** "GraphRAG in seconds — Neo4j included. Skip the docker run."
**Channels:** LlamaIndex GraphRAG V2 cookbook community, Neo4j Labs developer content, Jupyter/Colab notebook users, Medium tutorials.
**Keywords:** `llamaindex neo4j docker python`, `graphrag local setup python`, `knowledge graph llamaindex neo4j python`.
**Elevator pitch:** "The LlamaIndex GraphRAG cookbook tells you to run a docker command first. `llama-index-pydocker` skips that line. `from llama_index_pydocker import Neo4jGraphStore` — and you have a running Neo4j, ready for your pipeline."

### Audience C — Students and Educators
**Who:** Developers learning RAG and GraphRAG through tutorials or academic coursework.
**Pain point:** Docker prerequisites block tutorial progress. A failed `docker run` stops the learning path before any interesting code runs.
**Framing:** "No Docker prerequisites for your LlamaIndex tutorial."
**Channels:** Medium, Real Python, DataCamp, course platforms.
**Keywords:** `llamaindex local vector store`, `rag prototype local python`.
**Status:** Tertiary audience — benefits from the same zero-config behavior but is not the primary positioning target.
