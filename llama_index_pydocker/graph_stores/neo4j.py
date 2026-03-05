"""Neo4j graph store with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.graph_stores.neo4j import Neo4jGraphStore as _Neo4jGraphStore

from docker_db import Neo4jConfig, Neo4jDB
from llama_index_pydocker._utils import is_localhost, parse_url


class Neo4jGraphStore(_Neo4jGraphStore):
    """
    Drop-in replacement for ``llama_index.graph_stores.neo4j.Neo4jGraphStore``.

    When ``url`` resolves to localhost the Neo4j Docker container is started
    automatically via ``py-dockerdb`` before the store is initialised.
    For any non-localhost URL the class is a transparent passthrough to the
    upstream LlamaIndex implementation — Docker is never touched.

    Parameters
    ----------
    username : str
        Neo4j username. Default ``"neo4j"``.
    password : str
        Neo4j password.
    url : str
        Bolt URI, e.g. ``"bolt://localhost:7687"``.
        The port is always inferred from this value.
    database : str
        Neo4j database name. Default ``"neo4j"``.
    docker_config : Neo4jConfig, optional
        ``py-dockerdb`` config object. Use this to control ``volume_path``,
        ``container_name``, ``env_vars``, ``retries``, etc.
        The ``port`` and ``host`` fields are always overridden from ``url``.
    **kwargs
        Forwarded to the upstream ``Neo4jGraphStore.__init__``.
    """

    def __init__(
        self,
        *,
        url: str,
        username: str = "neo4j",
        password: str,
        database: str = "neo4j",
        docker_config: Neo4jConfig | None = None,
        **kwargs,
    ):
        self._db: Neo4jDB | None = None
        host, port = parse_url(url)

        if is_localhost(host):
            cfg = docker_config or Neo4jConfig(password=password)
            cfg = cfg.model_copy(update={"port": port or cfg.port, "host": host})
            self._db = Neo4jDB(cfg)
            self._db.create_db()

        super().__init__(
            username=username,
            password=password,
            url=url,
            database=database,
            **kwargs,
        )

    def stop(self):
        """Stop and remove the managed Docker container, if any."""
        if self._db is not None:
            self._db.stop_db()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()
