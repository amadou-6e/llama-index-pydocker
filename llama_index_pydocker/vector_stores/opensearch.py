"""OpenSearch vector store with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.vector_stores.opensearch import OpensearchVectorStore as _OpensearchVectorStore

from docker_db import OpenSearchConfig, OpenSearchDB
from llama_index_pydocker._utils import is_localhost, parse_url


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
    docker_config : OpenSearchConfig, optional
        ``py-dockerdb`` config object. Controls ``volume_path``,
        ``container_name``, etc.
        The ``port`` and ``host`` fields are always overridden from ``endpoint``.
    **kwargs
        Forwarded to the upstream ``OpensearchVectorStore.__init__``
        (e.g. ``embed_dim``, ``text_field``, ``embedding_field``).
    """

    def __init__(
        self,
        *,
        index_name: str,
        endpoint: str,
        docker_config: OpenSearchConfig | None = None,
        **kwargs,
    ):
        self._db: OpenSearchDB | None = None
        host, port = parse_url(endpoint)

        if is_localhost(host):
            cfg = docker_config or OpenSearchConfig()
            cfg = cfg.model_copy(update={"port": port or cfg.port, "host": host})
            self._db = OpenSearchDB(cfg)
            self._db.create_db()

        super().__init__(index_name=index_name, endpoint=endpoint, **kwargs)

    def stop(self):
        """Stop and remove the managed Docker container, if any."""
        if self._db is not None:
            self._db.stop_db()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()
