"""OpenSearch vector store with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.vector_stores.opensearch import (
    OpensearchVectorClient,
    OpensearchVectorStore as _OpensearchVectorStore,
)

from docker_db import OpenSearchConfig, OpenSearchDB
from llama_index_pydocker._url import is_localhost, parse_url


class OpensearchVectorStore(_OpensearchVectorStore):
    """
    Drop-in replacement for
    ``llama_index.vector_stores.opensearch.OpensearchVectorStore``.

    When ``endpoint`` resolves to localhost the OpenSearch Docker container is
    started automatically via ``py-dockerdb``. For any non-localhost endpoint
    the class is a transparent passthrough — Docker is never touched.

    Parameters
    ----------
    index_name : str
        OpenSearch index name.
    endpoint : str
        OpenSearch HTTP endpoint, e.g. ``"http://localhost:9200"``.
        The port is always inferred from this value.
    embed_dim : int
        Embedding dimensionality (required by OpensearchVectorClient).
    docker_config : OpenSearchConfig, optional
        ``py-dockerdb`` config object. Controls ``volume_path``,
        ``container_name``, etc.
        The ``port`` and ``host`` fields are always overridden from ``endpoint``.
    **kwargs
        Forwarded to ``OpensearchVectorClient.__init__``
        (e.g. ``embedding_field``, ``text_field``, ``engine``).
    """

    def __init__(
        self,
        *,
        index_name: str,
        endpoint: str,
        embed_dim: int,
        docker_config: OpenSearchConfig | None = None,
        **kwargs,
    ):
        """Initialize an OpenSearch vector store with optional Docker provisioning.

        Parameters
        ----------
        index_name : str
            Name of the OpenSearch index.
        endpoint : str
            OpenSearch endpoint URL.
        embed_dim : int
            Embedding dimensionality used by the vector client.
        docker_config : OpenSearchConfig | None, optional
            Container configuration used when endpoint resolves to localhost.
        **kwargs
            Extra keyword arguments forwarded to ``OpensearchVectorClient``.
        """
        host, port = parse_url(endpoint)
        _db: OpenSearchDB | None = None

        if is_localhost(host):
            cfg = docker_config or OpenSearchConfig()
            cfg = cfg.model_copy(update={"port": port or cfg.port, "host": host})
            _db = OpenSearchDB(cfg)
            _db.create_db()

        client = OpensearchVectorClient(
            endpoint=endpoint,
            index=index_name,
            dim=embed_dim,
            **kwargs,
        )
        super().__init__(client=client)
        # Use object.__setattr__ to bypass Pydantic's __setattr__ and store _db
        # directly in the instance __dict__.
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
        OpensearchVectorStore
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
