"""Qdrant vector store with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.vector_stores.qdrant import QdrantVectorStore as _QdrantVectorStore

from docker_db import QdrantConfig, QdrantDB
from llama_index_pydocker._url import is_localhost, parse_url


class QdrantVectorStore(_QdrantVectorStore):
    """
    Drop-in replacement for ``llama_index.vector_stores.qdrant.QdrantVectorStore``.

    When ``url`` resolves to localhost the Qdrant Docker container is started
    automatically via ``py-dockerdb``. For any non-localhost URL the class is a
    transparent passthrough — Docker is never touched.

    Parameters
    ----------
    collection_name : str
        Qdrant collection name.
    url : str
        Qdrant HTTP URL, e.g. ``"http://localhost:6333"``.
        The port is always inferred from this value.
    docker_config : QdrantConfig, optional
        ``py-dockerdb`` config object. Controls ``volume_path``,
        ``container_name``, ``vector_size``, etc.
        The ``port`` and ``host`` fields are always overridden from ``url``.
    **kwargs
        Forwarded to the upstream ``QdrantVectorStore.__init__``
        (e.g. ``api_key``, ``prefer_grpc``).
    """

    def __init__(
        self,
        *,
        collection_name: str,
        url: str,
        docker_config: QdrantConfig | None = None,
        **kwargs,
    ):
        """Initialize a Qdrant vector store with optional Docker provisioning.

        Parameters
        ----------
        collection_name : str
            Name of the target Qdrant collection.
        url : str
            Qdrant endpoint URL.
        docker_config : QdrantConfig | None, optional
            Container configuration used when ``url`` points to localhost.
        **kwargs
            Extra keyword arguments forwarded to the base vector store.
        """
        host, port = parse_url(url)
        _db: QdrantDB | None = None

        if is_localhost(host):
            cfg = docker_config or QdrantConfig(database=collection_name)
            cfg = cfg.model_copy(update={"port": port or cfg.port, "host": host})
            _db = QdrantDB(cfg)
            _db.create_db()
            client = _db.connection
        else:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=url, **{k: v for k, v in kwargs.items() if k == "api_key"})
            kwargs = {k: v for k, v in kwargs.items() if k != "api_key"}

        super().__init__(collection_name=collection_name, client=client, **kwargs)
        # Use object.__setattr__ to bypass Pydantic's __setattr__ and store _db
        # directly in the instance __dict__.  Plain ``self._db = _db`` would be
        # swallowed or raise because QdrantVectorStore is a Pydantic model.
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
        QdrantVectorStore
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
