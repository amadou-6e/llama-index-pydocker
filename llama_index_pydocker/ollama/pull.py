"""Shared helper for verbose Ollama model pulls with tqdm progress bars."""
from __future__ import annotations

import json
import sys

try:
    from tqdm import tqdm as _tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False


def pull_model_verbose(base_url: str, model: str) -> None:
    """
    Pull an Ollama model, streaming download progress via tqdm.

    Each layer is shown as a separate progress bar.  If tqdm is not installed
    a plain text fallback is used instead.  The pull is a no-op (fast manifest
    check) when the model is already present locally.

    Parameters
    ----------
    base_url : str
        Ollama API base URL, e.g. ``"http://localhost:11434"``.
    model : str
        Model name to pull, e.g. ``"llama3"`` or ``"nomic-embed-text"``.
    """
    import requests

    print(f"Pulling Ollama model '{model}' ...", flush=True)
    response = requests.post(
        f"{base_url}/api/pull",
        json={"model": model, "stream": True},
        stream=True,
        timeout=600,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Failed to pull model '{model}': {response.text}")

    if not _HAS_TQDM:
        _pull_plain(response, model)
        return

    _pull_tqdm(response)


def _pull_plain(response, model: str) -> None:
    """Stream pull progress without tqdm and print status lines.

    Parameters
    ----------
    response : requests.Response
        Streaming HTTP response from the Ollama pull endpoint.
    model : str
        Model name used for pull logging context.

    Returns
    -------
    None
        This function has side effects only.
    """
    seen: set[str] = set()
    for raw_line in response.iter_lines():
        if not raw_line:
            continue
        data = json.loads(raw_line)
        status = data.get("status", "")
        digest = data.get("digest", "")
        if digest:
            key = f"{status}:{digest[:12]}"
            if key not in seen:
                seen.add(key)
                print(f"  {status} {digest[:12]}", flush=True)
        else:
            print(f"  {status}", flush=True)


def _pull_tqdm(response) -> None:
    """Stream pull progress and render one tqdm bar per model layer.

    Parameters
    ----------
    response : requests.Response
        Streaming HTTP response from the Ollama pull endpoint.

    Returns
    -------
    None
        This function has side effects only.
    """
    bars: dict[str, _tqdm] = {}

    for raw_line in response.iter_lines():
        if not raw_line:
            continue
        data = json.loads(raw_line)
        status: str = data.get("status", "")
        digest: str | None = data.get("digest")
        total: int | None = data.get("total")
        completed: int = data.get("completed", 0)

        if digest and total:
            if digest not in bars:
                bars[digest] = _tqdm(
                    total=total,
                    desc=f"  {status[:20]:<20} {digest[:12]}",
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    leave=True,
                    file=sys.stdout,
                )
            bar = bars[digest]
            bar.n = completed
            bar.refresh()
            if completed >= total:
                bar.close()
                del bars[digest]
        else:
            # Status-only message (manifest check, verify, write, success …)
            print(f"  {status}", flush=True)

    for bar in bars.values():
        bar.close()
