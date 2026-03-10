"""Ollama LLM with automatic Docker provisioning."""
from __future__ import annotations

from llama_index.llms.ollama import Ollama as _Ollama

from docker_db import OllamaConfig, OllamaDB
from llama_index_pydocker._url import is_localhost, parse_url
from llama_index_pydocker.ollama.pull import pull_model_verbose


class Ollama(_Ollama):
    """
    Drop-in replacement for ``llama_index.llms.ollama.Ollama``.

    When ``base_url`` resolves to localhost the Ollama Docker container is
    started automatically via ``py-dockerdb``.  If the model is not yet
    present locally it is pulled with a live tqdm progress bar per layer.
    For any non-localhost URL the class is a transparent passthrough — Docker
    is never touched.

    Parameters
    ----------
    model : str
        Ollama model name, e.g. ``"llama3"`` or ``"mistral"``.
    base_url : str
        Ollama API base URL. Default ``"http://localhost:11434"``.
        The port is always inferred from this value.
    docker_config : OllamaConfig, optional
        ``py-dockerdb`` config object. Controls ``volume_path``,
        ``container_name``, ``retries``, etc.
        The ``port`` field is always overridden from ``base_url``.
    **kwargs
        Forwarded to the upstream ``Ollama.__init__``
        (e.g. ``temperature``, ``context_window``, ``request_timeout``).
    """

    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://localhost:11434",
        docker_config: OllamaConfig | None = None,
        **kwargs,
    ):
        """Initialize an Ollama LLM with optional Docker provisioning.

        Parameters
        ----------
        model : str
            Ollama model name.
        base_url : str, default="http://localhost:11434"
            Ollama API base URL.
        docker_config : OllamaConfig | None, optional
            Container configuration used when URL resolves to localhost.
        **kwargs
            Extra keyword arguments forwarded to the base LLM.
        """
        _db: OllamaDB | None = None
        host, port = parse_url(base_url)

        if is_localhost(host):
            cfg = docker_config or OllamaConfig()
            cfg = cfg.model_copy(update={"port": port or cfg.port})
            _db = OllamaDB(cfg)
            _db.create_db()
            _ensure_model(_db, base_url, model)

        super().__init__(model=model, base_url=base_url, **kwargs)
        # Bypass Pydantic's __setattr__ — Ollama extends BaseModel.
        object.__setattr__(self, "_db", _db)

    def stop(self):
        """Stop and remove the managed Docker container, if any.

        Returns
        -------
        None
            This method has side effects only.
        """
        db = self.__dict__.get("_db")
        if db is not None:
            db.delete_db(running_ok=True)

    def __enter__(self):
        """Enter context-manager mode.

        Returns
        -------
        Ollama
            The current LLM instance.
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


def _ensure_model(db: OllamaDB, base_url: str, model: str) -> None:
    """Ensure an Ollama model is available in the local model registry.

    Parameters
    ----------
    db : OllamaDB
        Running Ollama database manager used to list installed models.
    base_url : str
        Ollama API base URL used for pull operations.
    model : str
        Target model name.

    Returns
    -------
    None
        This function has side effects only.
    """
    present = {m.get("name", "") for m in db.list_models()}
    # Ollama tags: "llama3" may be stored as "llama3:latest"
    if model not in present and f"{model}:latest" not in present:
        pull_model_verbose(base_url, model)
