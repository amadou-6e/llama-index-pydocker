"""URL parsing and localhost detection utilities."""
from urllib.parse import urlparse

_LOCALHOST_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def parse_url(url: str) -> tuple[str, int | None]:
    """Return (host, port) parsed from a URL string."""
    parsed = urlparse(url)
    return parsed.hostname, parsed.port


def is_localhost(host: str) -> bool:
    return (host or "").lower() in _LOCALHOST_HOSTS
