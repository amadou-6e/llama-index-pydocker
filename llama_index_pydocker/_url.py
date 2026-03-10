"""URL parsing and localhost detection utilities."""
from urllib.parse import urlparse

_LOCALHOST_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def parse_url(url: str) -> tuple[str, int | None]:
    """Parse host and port from a URL.

    Parameters
    ----------
    url : str
        URL or DSN string containing a host component.

    Returns
    -------
    tuple[str, int | None]
        A ``(host, port)`` tuple extracted from ``url``.
    """
    parsed = urlparse(url)
    return parsed.hostname, parsed.port


def is_localhost(host: str) -> bool:
    """Check whether a host value targets the local machine.

    Parameters
    ----------
    host : str
        Hostname or IP address value.

    Returns
    -------
    bool
        ``True`` when ``host`` is a loopback/local binding address.
    """
    return (host or "").lower() in _LOCALHOST_HOSTS
