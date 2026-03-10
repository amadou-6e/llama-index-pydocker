# Ollama LLM and Embeddings

`Ollama` and `OllamaEmbedding` are drop-in replacements for
[`llama_index.llms.ollama.Ollama`](https://docs.llamaindex.ai/en/stable/api_reference/llms/ollama/) and
[`llama_index.embeddings.ollama.OllamaEmbedding`](https://docs.llamaindex.ai/en/stable/api_reference/embeddings/ollama/).
On a localhost `base_url` they start an Ollama Docker container and pull the
requested model automatically. On any other host they connect to the remote
Ollama server without touching Docker.

> **Note:** First run pulls the Ollama image and model weights. Allow a few minutes
> depending on your connection speed. Downloaded weights are cached in `volume_path`
> and reused on subsequent runs.

## Installation

```bash
pip install "llama-index-pydocker[ollama]"
```

## Basic usage

Both classes accept the same constructor arguments as their LlamaIndex originals,
plus an optional `docker_config`.

```python
from llama_index_pydocker import OllamaEmbedding, Ollama

embed_model = OllamaEmbedding(
    model_name="all-minilm",          # 46 MB — smallest available embedding model
    base_url="http://localhost:11434",
)

llm = Ollama(
    model="tinyllama",
    base_url="http://localhost:11434",
    request_timeout=120.0,
)

embeddings = embed_model.get_text_embedding_batch(["Hello world"])
response = llm.complete("In one sentence, what is Docker?")

embed_model.stop()  # stops the shared container
```

`OllamaEmbedding` and `Ollama` share the same Docker container when given the same
`base_url`. The second instantiation finds the container already running and skips
startup. Call `stop()` on either object — both reference the same container.

## Sharing one container

Use a fixed `container_name` in `OllamaConfig` to ensure both classes bind to the
same container:

```python
from docker_db import OllamaConfig
from llama_index_pydocker import OllamaEmbedding, Ollama

cfg = OllamaConfig(
    container_name="ollama-dev",
    volume_path="/data/ollama",   # model weights persist across runs
)

embed_model = OllamaEmbedding(
    model_name="all-minilm",
    base_url="http://localhost:11434",
    docker_config=cfg,
)

llm = Ollama(
    model="llama3",
    base_url="http://localhost:11434",
    docker_config=cfg,          # same config — reuses the running container
)
```

## Routing

| `base_url` host | Behaviour |
|---|---|
| `localhost` / `127.0.0.1` | Docker container started (or reused); model pulled if not present |
| Any other host | Direct connection — Docker is never contacted |

```python
# Remote Ollama server — Docker is never started
embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://my-gpu-server:11434",
)

llm = Ollama(
    model="llama3",
    base_url="http://my-gpu-server:11434",
)
```

## Docker configuration

Key `OllamaConfig` fields:

| Field | Purpose |
|---|---|
| `container_name` | Fixed name — reuses an existing container; ensures embedding and LLM share one instance |
| `volume_path` | Host directory where Ollama caches model weights across runs |
| `retries` / `delay` | Startup polling — model pulls can take several minutes on first run |
| `image_name` | Override the Ollama Docker image tag |

## Full example

See the [Ollama notebook](../../usage/ollama_example.ipynb) for a complete workflow:
shared container setup, embedding a text batch with `all-minilm`, generating text
with `tinyllama`, and context manager teardown.
