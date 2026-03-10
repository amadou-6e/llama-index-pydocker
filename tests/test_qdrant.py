"""Tests for QdrantVectorStore with Docker auto-provisioning."""
import uuid
from pathlib import Path
from unittest.mock import patch

import docker
import pytest

from docker_db import QdrantConfig
from tests.conftest import TEMP_DIR, free_port, stop_containers


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_containers():
    """Ensure Qdrant test containers are removed before and after module tests."""
    stop_containers("test-pydocker-qdrant")
    yield
    stop_containers("test-pydocker-qdrant")


@pytest.fixture
def qdrant_port():
    """Provide a free Qdrant port for tests."""
    return free_port()


@pytest.fixture
def qdrant_config(qdrant_port):
    """Create a unique Qdrant Docker config for a test run."""
    name = f"test-pydocker-qdrant-{uuid.uuid4().hex[:8]}"
    return QdrantConfig(
        database="test_collection",
        project_name="test",
        container_name=name,
        volume_path=Path(TEMP_DIR, "qddata", name),
        port=qdrant_port,
        vector_size=4,
        retries=20,
        delay=2,
    )


# ── localhost / Docker tests ──────────────────────────────────────────────────

@pytest.mark.timeout(180)
def test_localhost_starts_container(qdrant_config, qdrant_port):
    """Localhost Qdrant URL should start a managed Docker container."""
    from llama_index_pydocker import QdrantVectorStore

    store = QdrantVectorStore(
        collection_name="test_collection",
        url=f"http://localhost:{qdrant_port}",
        docker_config=qdrant_config,
    )

    assert store._db is not None
    store.stop()


@pytest.mark.timeout(180)
def test_context_manager_stops_container(qdrant_config, qdrant_port):
    """Context exit should stop and remove the managed Qdrant container."""
    from llama_index_pydocker import QdrantVectorStore

    with QdrantVectorStore(
        collection_name="test_collection",
        url=f"http://localhost:{qdrant_port}",
        docker_config=qdrant_config,
    ) as store:
        assert store._db is not None

    client = docker.from_env()
    containers = [c.name for c in client.containers.list(all=True)]
    assert qdrant_config.container_name not in containers


@pytest.mark.timeout(180)
def test_port_inferred_from_url(qdrant_config, qdrant_port):
    """Qdrant port from URL should override docker config port."""
    from llama_index_pydocker import QdrantVectorStore

    wrong_port_config = qdrant_config.model_copy(update={"port": 9999})

    with QdrantVectorStore(
        collection_name="test_collection",
        url=f"http://localhost:{qdrant_port}",
        docker_config=wrong_port_config,
    ) as store:
        assert store._db.config.port == qdrant_port


# ── remote / passthrough tests ────────────────────────────────────────────────

def test_remote_url_no_docker():
    """Remote Qdrant URL should bypass Docker provisioning."""
    from llama_index.vector_stores.qdrant import QdrantVectorStore as _Base
    from llama_index_pydocker import QdrantVectorStore
    from qdrant_client import QdrantClient

    with patch.object(QdrantClient, "__init__", return_value=None), \
         patch.object(_Base, "__init__", return_value=None) as mock_init:
        store = QdrantVectorStore(
            collection_name="docs",
            url="https://my-cluster.qdrant.io:6333",
            api_key="secret",
        )

    assert store._db is None
