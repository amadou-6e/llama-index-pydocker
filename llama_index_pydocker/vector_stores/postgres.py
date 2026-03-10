"""PGVector store with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.vector_stores.postgres import PGVectorStore as _PGVectorStore

from docker_db import PostgresConfig, PostgresDB
from llama_index_pydocker._url import is_localhost, parse_url


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
        """Initialize a PGVector store with optional Docker provisioning.

        Parameters
        ----------
        connection_string : str
            PostgreSQL connection string.
        docker_config : PostgresConfig | None, optional
            Container configuration used when host resolves to localhost.
        **kwargs
            Extra keyword arguments forwarded to the base vector store.
        """
        host, port = parse_url(connection_string)
        _db: PostgresDB | None = None

        if is_localhost(host):
            parsed = _parse_pg_dsn(connection_string)
            cfg = docker_config or PostgresConfig(
                user=parsed["user"],
                password=parsed["password"],
                database=parsed["database"],
            )
            cfg = cfg.model_copy(update={"port": port or cfg.port, "host": host})
            _db = PostgresDB(cfg)
            _db.create_db()

        super().__init__(connection_string=connection_string, **kwargs)
        # Use object.__setattr__ to bypass Pydantic's __setattr__ and store _db
        # directly in the instance __dict__.  Plain ``self._db = _db`` would be
        # swallowed or raise because PGVectorStore is a Pydantic model.
        object.__setattr__(self, '_db', _db)

    def stop(self):
        """Stop and remove the managed Docker container, if any.

        Returns
        -------
        None
            This method has side effects only.
        """
        db = self.__dict__.get('_db')
        if db is not None:
            db.delete_db(running_ok=True)

    def __enter__(self):
        """Enter context-manager mode.

        Returns
        -------
        PGVectorStore
            The current store instance.
        """
        return self

    def __exit__(self, *_):
        """Exit context-manager mode and stop managed resources.

        Parameters
        ----------
        *_ : tuple
            Standard context manager exception tuple (unused).

        Returns
        -------
        None
            This method has side effects only.
        """
        self.stop()


def _parse_pg_dsn(dsn: str) -> dict:
    """Extract Postgres credentials and database from a DSN string.

    Parameters
    ----------
    dsn : str
        PostgreSQL DSN string.

    Returns
    -------
    dict
        Dictionary with ``user``, ``password``, and ``database`` keys.
    """
    from urllib.parse import urlparse
    p = urlparse(dsn)
    return {
        "user": p.username or "postgres",
        "password": p.password or "",
        "database": p.path.lstrip("/") or "postgres",
    }
