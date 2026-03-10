"""Tests for Ollama LLM and OllamaEmbedding with Docker auto-provisioning."""
import tempfile
import uuid
from pathlib import Path

import docker
import pytest

from docker_db import OllamaConfig
from tests.conftest import TEMP_DIR, free_port, stop_containers


# all-minilm: 46 MB — smallest available Ollama embedding model
EMBED_MODEL = "all-minilm"
# tinyllama: 637 MB — smallest reasonable generative model
LLM_MODEL = "tinyllama"

# Kept outside TEMP_DIR so the autouse function-scoped tmp_dir fixture
# (which nukes TEMP_DIR between every test) does not delete the pulled model.
_SHARED_TMPDIR = tempfile.mkdtemp(prefix="pydocker-ollama-shared-")
SHARED_VOLUME = Path(_SHARED_TMPDIR, "ollamadata")


# ── module-level cleanup ───────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_containers():
    """Ensure Ollama test containers are removed before and after module tests."""
    stop_containers("test-pydocker-ollama")
    yield
    stop_containers("test-pydocker-ollama")


# ── shared container fixture (model pulled once per test session) ──────────────

@pytest.fixture(scope="module")
def shared_embed(cleanup_containers):
    """One Ollama container + all-minilm pulled once; reused by multiple tests."""
    from llama_index_pydocker import OllamaEmbedding

    SHARED_VOLUME.mkdir(parents=True, exist_ok=True)
    port = free_port()
    cfg = OllamaConfig(
        project_name="test",
        container_name="test-pydocker-ollama-shared",
        volume_path=SHARED_VOLUME,
        port=port,
        retries=30,
        delay=2,
    )
    em = OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=f"http://localhost:{port}",
        docker_config=cfg,
    )
    yield em
    em.stop()


# ── per-test config for lifecycle tests ───────────────────────────────────────

@pytest.fixture
def fresh_config():
    """Fresh container config with its own volume (no cached models)."""
    port = free_port()
    name = f"test-pydocker-ollama-{uuid.uuid4().hex[:8]}"
    vol = Path(TEMP_DIR, "ollamadata", name)
    vol.mkdir(parents=True, exist_ok=True)
    return OllamaConfig(
        project_name="test",
        container_name=name,
        volume_path=vol,
        port=port,
        retries=30,
        delay=2,
    )


# ── embedding tests ───────────────────────────────────────────────────────────

@pytest.mark.timeout(600)
def test_embedding_starts_container(shared_embed):
    """Embedding fixture should hold a running managed container."""
    assert shared_embed._db is not None


@pytest.mark.timeout(600)
def test_embedding_produces_vectors(shared_embed):
    """Embedding model should return vectors for a text batch."""
    texts = [
        "Ollama runs models locally.",
        "Docker makes infrastructure reproducible.",
    ]
    embeddings = shared_embed.get_text_embedding_batch(texts)
    assert len(embeddings) == 2
    assert all(len(e) > 0 for e in embeddings)


@pytest.mark.timeout(600)
def test_model_pulled_when_not_present(fresh_config):
    """A fresh container with empty volume pulls the model on first init."""
    from llama_index_pydocker import OllamaEmbedding

    em = OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=f"http://localhost:{fresh_config.port}",
        docker_config=fresh_config,
    )
    models = {m["name"] for m in em._db.list_models()}
    em.stop()

    assert any(EMBED_MODEL in name for name in models)


@pytest.mark.timeout(600)
def test_model_not_pulled_again_when_present(shared_embed):
    """Second OllamaEmbedding pointing at the same container skips the pull."""
    from llama_index_pydocker import OllamaEmbedding

    cfg = shared_embed._db.config
    models_before = {m["name"] for m in shared_embed._db.list_models()}

    # Re-init pointing at the already-running container
    em2 = OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=f"http://localhost:{cfg.port}",
        docker_config=cfg,
    )
    models_after = {m["name"] for m in em2._db.list_models()}
    # Don't stop — shared container is owned by shared_embed fixture

    assert models_before == models_after


# ── LLM test ──────────────────────────────────────────────────────────────────

@pytest.mark.timeout(600)
def test_llm_starts_and_generates(fresh_config):
    """Ollama LLM starts a container, pulls tinyllama, and generates text."""
    from llama_index_pydocker import Ollama

    llm = Ollama(
        model=LLM_MODEL,
        base_url=f"http://localhost:{fresh_config.port}",
        docker_config=fresh_config,
        request_timeout=120.0,
    )
    assert llm._db is not None

    response = llm.complete("In one sentence, what is Docker?")
    assert len(response.text.strip()) > 0

    llm.stop()


# ── lifecycle tests ────────────────────────────────────────────────────────────

@pytest.mark.timeout(600)
def test_context_manager_stops_container(fresh_config):
    """Context exit should stop and remove the managed Ollama container."""
    from llama_index_pydocker import OllamaEmbedding

    with OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=f"http://localhost:{fresh_config.port}",
        docker_config=fresh_config,
    ) as em:
        container_name = em._db.config.container_name
        assert em._db is not None

    client = docker.from_env()
    containers = [c.name for c in client.containers.list(all=True)]
    assert container_name not in containers


@pytest.mark.timeout(600)
def test_port_inferred_from_url(fresh_config):
    """Port from Ollama base URL should override docker config port."""
    from llama_index_pydocker import OllamaEmbedding

    wrong_port_cfg = fresh_config.model_copy(update={"port": 9999})

    with OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=f"http://localhost:{fresh_config.port}",
        docker_config=wrong_port_cfg,
    ) as em:
        assert em._db.config.port == fresh_config.port


# ── remote passthrough tests ──────────────────────────────────────────────────

def test_embedding_remote_url_no_docker():
    """Remote Ollama embedding URL should bypass Docker provisioning."""
    from unittest.mock import patch
    from llama_index.embeddings.ollama import OllamaEmbedding as _Base
    from llama_index_pydocker import OllamaEmbedding

    with patch.object(_Base, "__init__", return_value=None):
        em = OllamaEmbedding(
            model_name=EMBED_MODEL,
            base_url="http://my-gpu-server:11434",
        )

    assert em._db is None


def test_llm_remote_url_no_docker():
    """Remote Ollama LLM URL should bypass Docker provisioning."""
    from unittest.mock import patch
    from llama_index.llms.ollama import Ollama as _Base
    from llama_index_pydocker import Ollama

    with patch.object(_Base, "__init__", return_value=None):
        llm = Ollama(
            model=LLM_MODEL,
            base_url="http://my-gpu-server:11434",
        )

    assert llm._db is None
