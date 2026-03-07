"""Tests for PGVectorStore with Docker auto-provisioning."""
import uuid
from pathlib import Path
from unittest.mock import patch

import docker
import pytest

from docker_db import PostgresConfig
from tests.conftest import TEMP_DIR, TEST_DIR, free_port, stop_containers

_CONFIGS_DIR = TEST_DIR / "configs" / "postgres"

# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_containers():
    """Ensure Postgres test containers are removed before and after module tests."""
    stop_containers("test-pydocker-postgres")
    yield
    stop_containers("test-pydocker-postgres")


@pytest.fixture
def pg_port():
    """Provide a free Postgres port for tests."""
    return free_port()


@pytest.fixture
def pg_config(pg_port):
    """Create a unique Postgres Docker config for a test run."""
    name = f"test-pydocker-postgres-{uuid.uuid4().hex[:8]}"
    return PostgresConfig(
        user="testuser",
        password="testpassword",
        database="vectordb",
        project_name="test",
        image_name=f"test-pydocker-postgres-image-{uuid.uuid4().hex[:8]}:latest",
        container_name=name,
        workdir=_CONFIGS_DIR,
        dockerfile_path=_CONFIGS_DIR / "Dockerfile",
        init_script=_CONFIGS_DIR / "initdb.sh",
        volume_path=Path(TEMP_DIR, "pgdata", name),
        port=pg_port,
        retries=30,
        delay=3,
    )


@pytest.fixture
def conn_string(pg_port):
    """Build a localhost Postgres connection string for tests."""
    return f"postgresql://testuser:testpassword@localhost:{pg_port}/vectordb"


# ── localhost / Docker tests ──────────────────────────────────────────────────

@pytest.mark.timeout(180)
def test_localhost_starts_container(pg_config, conn_string):
    """Localhost PG DSN should start a managed Docker container."""
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
    """Context exit should stop and remove the managed Postgres container."""
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
    """PG port from connection string should override docker config port."""
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
    """Remote PG DSN should bypass Docker provisioning."""
    from llama_index.vector_stores.postgres import PGVectorStore as _Base
    from llama_index_pydocker import PGVectorStore

    remote = "postgresql://user:pass@my-rds.amazonaws.com:5432/vectordb"

    with patch.object(_Base, "__init__", return_value=None) as mock_init:
        store = PGVectorStore(connection_string=remote, embed_dim=1536)

    assert store._db is None
    mock_init.assert_called_once_with(connection_string=remote, embed_dim=1536)
