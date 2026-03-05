"""PGVector store with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.vector_stores.postgres import PGVectorStore as _PGVectorStore

from docker_db import PostgresConfig, PostgresDB
from llama_index_pydocker._utils import is_localhost, parse_url


class PGVectorStore(_PGVectorStore):
    """
    Drop-in replacement for ``llama_index.vector_stores.postgres.PGVectorStore``.

    When ``connection_string`` resolves to localhost the Postgres Docker container
    is started automatically via ``py-dockerdb``. For any non-localhost host the
    class is a transparent passthrough — Docker is never touched.

    Parameters
    ----------
    connection_string : str
        PostgreSQL DSN, e.g. ``"postgresql://user:pass@localhost:5432/db"``.
        The port is always inferred from this value.
    docker_config : PostgresConfig, optional
        ``py-dockerdb`` config object. Controls ``volume_path``,
        ``container_name``, ``init_script``, etc.
        The ``port`` and ``host`` fields are always overridden from
        ``connection_string``.
    **kwargs
        Forwarded to the upstream ``PGVectorStore.__init__``
        (e.g. ``embed_dim``, ``table_name``, ``schema_name``).
    """

    def __init__(
        self,
        *,
        connection_string: str,
        docker_config: PostgresConfig | None = None,
        **kwargs,
    ):
        self._db: PostgresDB | None = None
        host, port = parse_url(connection_string)

        if is_localhost(host):
            parsed = _parse_pg_dsn(connection_string)
            cfg = docker_config or PostgresConfig(
                user=parsed["user"],
                password=parsed["password"],
                database=parsed["database"],
            )
            cfg = cfg.model_copy(update={"port": port or cfg.port, "host": host})
            self._db = PostgresDB(cfg)
            self._db.create_db()

        super().__init__(connection_string=connection_string, **kwargs)

    def stop(self):
        """Stop and remove the managed Docker container, if any."""
        if self._db is not None:
            self._db.stop_db()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()


def _parse_pg_dsn(dsn: str) -> dict:
    """Extract user, password, database from a postgresql:// DSN."""
    from urllib.parse import urlparse
    p = urlparse(dsn)
    return {
        "user": p.username or "postgres",
        "password": p.password or "",
        "database": p.path.lstrip("/") or "postgres",
    }
