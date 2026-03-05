"""Shared fixtures and helpers for llama-index-pydocker tests."""
import os
import shutil
import socket
import sys
from pathlib import Path

import docker
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

TEST_DIR = Path(__file__).resolve().parent
TEMP_DIR = TEST_DIR / "tmp"
os.environ.setdefault("WORKDIR", str(Path(__file__).resolve().parents[2]))


# ── helpers ───────────────────────────────────────────────────────────────────

def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def nuke_dir(path: Path):
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def stop_containers(prefix: str):
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
    nuke_dir(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    yield TEMP_DIR
    nuke_dir(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ── container-log dump on failure ─────────────────────────────────────────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def _dump_logs_on_failure(request):
    yield
    report = getattr(request.node, "rep_call", None) or getattr(request.node, "rep_setup", None)
    if not report or not report.failed:
        return
    # try to find a store fixture and dump its container logs
    for val in getattr(request.node, "funcargs", {}).values():
        db = getattr(val, "_db", None)
        if db is None:
            continue
        name = getattr(getattr(db, "config", None), "container_name", None)
        if not name:
            continue
        try:
            client = docker.from_env()
            logs = client.containers.get(name).logs(tail=200).decode("utf-8", errors="replace")
            terminal = request.config.pluginmanager.get_plugin("terminalreporter")
            if terminal:
                terminal.write_sep("-", f"container logs: {name}")
                terminal.write_line(logs.rstrip() or "<empty>")
        except Exception:
            pass
