"""Tests for OpensearchVectorStore with Docker auto-provisioning."""
import uuid
from pathlib import Path
from unittest.mock import patch

import docker
import pytest

from docker_db import OpenSearchConfig
from tests.conftest import TEMP_DIR, free_port, stop_containers


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_containers():
    stop_containers("test-pydocker-opensearch")
    yield
    stop_containers("test-pydocker-opensearch")


@pytest.fixture
def os_port():
    return free_port()


@pytest.fixture
def os_config(os_port):
    name = f"test-pydocker-opensearch-{uuid.uuid4().hex[:8]}"
    return OpenSearchConfig(
        project_name="test",
        container_name=name,
        volume_path=Path(TEMP_DIR, "osdata", name),
        port=os_port,
        retries=30,
        delay=3,
    )


# ── localhost / Docker tests ──────────────────────────────────────────────────

@pytest.mark.timeout(300)
def test_localhost_starts_container(os_config, os_port):
    from llama_index_pydocker import OpensearchVectorStore

    store = OpensearchVectorStore(
        index_name="test_index",
        endpoint=f"http://localhost:{os_port}",
        docker_config=os_config,
        embed_dim=4,
    )

    assert store._db is not None
    store.stop()


@pytest.mark.timeout(300)
def test_context_manager_stops_container(os_config, os_port):
    from llama_index_pydocker import OpensearchVectorStore

    with OpensearchVectorStore(
        index_name="test_index",
        endpoint=f"http://localhost:{os_port}",
        docker_config=os_config,
        embed_dim=4,
    ) as store:
        assert store._db is not None

    client = docker.from_env()
    containers = [c.name for c in client.containers.list(all=True)]
    assert os_config.container_name not in containers


@pytest.mark.timeout(300)
def test_port_inferred_from_url(os_config, os_port):
    from llama_index_pydocker import OpensearchVectorStore

    wrong_port_config = os_config.model_copy(update={"port": 9999})

    with OpensearchVectorStore(
        index_name="test_index",
        endpoint=f"http://localhost:{os_port}",
        docker_config=wrong_port_config,
        embed_dim=4,
    ) as store:
        assert store._db.config.port == os_port


# ── remote / passthrough tests ────────────────────────────────────────────────

def test_remote_url_no_docker():
    from llama_index.vector_stores.opensearch import OpensearchVectorStore as _Base
    from llama_index_pydocker import OpensearchVectorStore

    remote = "https://my-cluster.us-east-1.es.amazonaws.com"

    with patch.object(_Base, "__init__", return_value=None) as mock_init:
        store = OpensearchVectorStore(
            index_name="my_index",
            endpoint=remote,
            embed_dim=768,
        )

    assert store._db is None
    mock_init.assert_called_once_with(
        index_name="my_index",
        endpoint=remote,
        embed_dim=768,
    )
