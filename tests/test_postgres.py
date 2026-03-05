"""Tests for PGVectorStore with Docker auto-provisioning."""
import uuid
from pathlib import Path
from unittest.mock import patch

import docker
import pytest

from docker_db import PostgresConfig
from tests.conftest import TEMP_DIR, free_port, stop_containers


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_containers():
    stop_containers("test-pydocker-postgres")
    yield
    stop_containers("test-pydocker-postgres")


@pytest.fixture
def pg_port():
    return free_port()


@pytest.fixture
def pg_config(pg_port):
    name = f"test-pydocker-postgres-{uuid.uuid4().hex[:8]}"
    return PostgresConfig(
        user="testuser",
        password="testpassword",
        database="vectordb",
        project_name="test",
        container_name=name,
        volume_path=Path(TEMP_DIR, "pgdata", name),
        port=pg_port,
        retries=20,
        delay=2,
    )


@pytest.fixture
def conn_string(pg_port):
    return f"postgresql://testuser:testpassword@localhost:{pg_port}/vectordb"


# ── localhost / Docker tests ──────────────────────────────────────────────────

@pytest.mark.timeout(180)
def test_localhost_starts_container(pg_config, conn_string):
    from llama_index_pydocker import PGVectorStore

    store = PGVectorStore(
        connection_string=conn_string,
        embed_dim=4,
        docker_config=pg_config,
    )

    assert store._db is not None
    assert store._db.database_created
    store.stop()


@pytest.mark.timeout(180)
def test_context_manager_stops_container(pg_config, conn_string):
    from llama_index_pydocker import PGVectorStore

    with PGVectorStore(
        connection_string=conn_string,
        embed_dim=4,
        docker_config=pg_config,
    ) as store:
        assert store._db is not None

    client = docker.from_env()
    containers = [c.name for c in client.containers.list(all=True)]
    assert pg_config.container_name not in containers


@pytest.mark.timeout(180)
def test_port_inferred_from_url(pg_config, conn_string, pg_port):
    from llama_index_pydocker import PGVectorStore

    wrong_port_config = pg_config.model_copy(update={"port": 9999})

    with PGVectorStore(
        connection_string=conn_string,
        embed_dim=4,
        docker_config=wrong_port_config,
    ) as store:
        assert store._db.config.port == pg_port


# ── remote / passthrough tests ────────────────────────────────────────────────

def test_remote_url_no_docker():
    from llama_index.vector_stores.postgres import PGVectorStore as _Base
    from llama_index_pydocker import PGVectorStore

    remote = "postgresql://user:pass@my-rds.amazonaws.com:5432/vectordb"

    with patch.object(_Base, "__init__", return_value=None) as mock_init:
        store = PGVectorStore(connection_string=remote, embed_dim=1536)

    assert store._db is None
    mock_init.assert_called_once_with(connection_string=remote, embed_dim=1536)
