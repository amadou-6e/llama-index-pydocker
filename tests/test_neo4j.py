"""Tests for Neo4jGraphStore with Docker auto-provisioning."""
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import docker
import pytest

from docker_db import Neo4jConfig
from tests.conftest import TEMP_DIR, free_port, stop_containers


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_containers():
    """Ensure Neo4j test containers are removed before and after module tests."""
    stop_containers("test-pydocker-neo4j")
    yield
    stop_containers("test-pydocker-neo4j")


@pytest.fixture
def bolt_port():
    """Provide a free Bolt port for Neo4j tests."""
    return free_port()


@pytest.fixture
def http_port():
    """Provide a free HTTP port for Neo4j tests."""
    return free_port()


@pytest.fixture
def neo4j_config(bolt_port, http_port):
    """Create a unique Neo4j Docker config for a test run."""
    name = f"test-pydocker-neo4j-{uuid.uuid4().hex[:8]}"
    return Neo4jConfig(
        password="testpassword",
        project_name="test",
        container_name=name,
        volume_path=Path(TEMP_DIR, "n4jdata", name),
        port=bolt_port,
        http_port=http_port,
        retries=40,
        delay=3,
    )


# ── localhost / Docker tests ──────────────────────────────────────────────────

@pytest.mark.timeout(300)
def test_localhost_starts_container(neo4j_config, bolt_port):
    """Localhost Neo4j URL should start a managed Docker container."""
    from llama_index_pydocker import Neo4jGraphStore

    store = Neo4jGraphStore(
        username="neo4j",
        password="testpassword",
        url=f"bolt://localhost:{bolt_port}",
        docker_config=neo4j_config,
    )

    assert store._db is not None
    assert store._db.database_created

    result = store.query("RETURN 1 AS n")
    assert result[0]["n"] == 1

    store.stop()


@pytest.mark.timeout(300)
def test_context_manager_stops_container(neo4j_config, bolt_port):
    """Context exit should stop and remove the managed Neo4j container."""
    from llama_index_pydocker import Neo4jGraphStore

    with Neo4jGraphStore(
        username="neo4j",
        password="testpassword",
        url=f"bolt://localhost:{bolt_port}",
        docker_config=neo4j_config,
    ) as store:
        assert store._db is not None
        store.query("RETURN 1 AS ok")

    client = docker.from_env()
    containers = [c.name for c in client.containers.list(all=True)]
    assert neo4j_config.container_name not in containers


@pytest.mark.timeout(300)
def test_graph_write_and_read(neo4j_config, bolt_port):
    """Graph writes should be persisted and queryable in the test container."""
    from llama_index_pydocker import Neo4jGraphStore

    with Neo4jGraphStore(
        username="neo4j",
        password="testpassword",
        url=f"bolt://localhost:{bolt_port}",
        docker_config=neo4j_config,
    ) as store:
        store.query("CREATE (n:Paper {title: $title})", param_map={"title": "Attention Is All You Need"})
        rows = store.query("MATCH (n:Paper) RETURN n.title AS title")
        assert rows[0]["title"] == "Attention Is All You Need"


@pytest.mark.timeout(300)
def test_port_inferred_from_url(neo4j_config, bolt_port):
    """docker_config.port is overridden by the port in the url."""
    from llama_index_pydocker import Neo4jGraphStore

    # Pass a config with the wrong port — url should win
    wrong_port_config = neo4j_config.model_copy(update={"port": 9999})

    with Neo4jGraphStore(
        username="neo4j",
        password="testpassword",
        url=f"bolt://localhost:{bolt_port}",
        docker_config=wrong_port_config,
    ) as store:
        assert store._db.config.port == bolt_port


@pytest.mark.timeout(300)
def test_reuse_running_container(neo4j_config, bolt_port):
    """Second init reuses the running container without error."""
    from llama_index_pydocker import Neo4jGraphStore

    store1 = Neo4jGraphStore(
        username="neo4j",
        password="testpassword",
        url=f"bolt://localhost:{bolt_port}",
        docker_config=neo4j_config,
    )
    store2 = Neo4jGraphStore(
        username="neo4j",
        password="testpassword",
        url=f"bolt://localhost:{bolt_port}",
        docker_config=neo4j_config,
    )
    store2.query("RETURN 1 AS ok")
    store1.stop()


# ── remote / passthrough tests ────────────────────────────────────────────────

def test_remote_url_no_docker():
    """Non-localhost URL must not create a _db instance."""
    from llama_index.graph_stores.neo4j import Neo4jGraphStore as _Base
    from llama_index_pydocker import Neo4jGraphStore

    remote_url = "bolt://my-aura.databases.neo4j.io:7687"

    with patch.object(_Base, "__init__", return_value=None) as mock_init:
        store = Neo4jGraphStore(
            username="neo4j",
            password="secret",
            url=remote_url,
        )

    assert store._db is None
    mock_init.assert_called_once_with(
        username="neo4j",
        password="secret",
        url=remote_url,
        database="neo4j",
        refresh_schema=False,
    )
