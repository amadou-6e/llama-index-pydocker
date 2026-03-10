"""Shared fixtures and helpers for llama-index-pydocker tests."""
import os
import shutil
import socket
import sys
from pathlib import Path
from typing import Any

import docker
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

TEST_DIR = Path(__file__).resolve().parent
TEMP_DIR = TEST_DIR / "tmp"
os.environ.setdefault("WORKDIR", str(Path(__file__).resolve().parents[2]))


# ── helpers ───────────────────────────────────────────────────────────────────

def free_port() -> int:
    """Get an available local TCP port.

    Returns
    -------
    int
        Free port number bound on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def nuke_dir(path: Path):
    """Remove a directory tree if it exists.

    Parameters
    ----------
    path : Path
        Directory path to delete recursively.
    """
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def stop_containers(prefix: str):
    """Stop and remove all Docker containers matching a name prefix.

    Parameters
    ----------
    prefix : str
        Container name prefix to match.
    """
    client = docker.from_env()
    for c in client.containers.list(all=True):
        if c.name.startswith(prefix):
            try:
                c.stop()
                c.remove()
            except Exception:
                pass


# ── session-level tmp dir ─────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def tmp_dir():
    """Provide a fresh temporary test directory for each test.

    Yields
    ------
    Path
        Temporary directory path under ``tests/tmp``.
    """
    nuke_dir(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    yield TEMP_DIR
    nuke_dir(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ── container-log dump on failure (mirrors py-dockerdb pattern) ───────────────

def _pick_container_name(funcargs: dict[str, Any]) -> str | None:
    """Walk fixture values to find a container name to fetch logs from."""
    # 1. Store fixtures expose ._db.config.container_name
    for val in funcargs.values():
        db = getattr(val, "_db", None)
        if db is None:
            continue
        name = getattr(getattr(db, "config", None), "container_name", None)
        if isinstance(name, str) and name:
            return name

    # 2. Raw config fixtures
    for val in funcargs.values():
        name = getattr(val, "container_name", None)
        if isinstance(name, str) and name:
            return name

    # 3. Manager fixtures (config.container_name)
    for val in funcargs.values():
        name = getattr(getattr(val, "config", None), "container_name", None)
        if isinstance(name, str) and name:
            return name

    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach pytest phase reports to each test item.

    Parameters
    ----------
    item : pytest.Item
        Current test item.
    call : pytest.CallInfo
        Current pytest call info.

    Yields
    ------
    object
        Hook wrapper result passed through to pytest.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def _dump_logs_on_failure(request):
    """Print container logs when a test fails.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Active pytest request object.

    Yields
    ------
    None
        Fixture teardown hook.
    """
    yield
    report = getattr(request.node, "rep_call", None) or getattr(request.node, "rep_setup", None)
    if not report or not report.failed:
        return

    name = _pick_container_name(getattr(request.node, "funcargs", {}))
    if not name:
        return

    try:
        client = docker.from_env()
        container = client.containers.get(name)
        logs = container.logs(tail=300).decode("utf-8", errors="replace")
    except Exception as exc:
        logs = f"<could not fetch logs for {name}: {exc}>"

    terminal = request.config.pluginmanager.get_plugin("terminalreporter")
    if terminal:
        terminal.write_sep("-", f"Failed test {request.node.nodeid} | container logs: {name}")
        terminal.write_line(logs.rstrip() or "<empty>")
