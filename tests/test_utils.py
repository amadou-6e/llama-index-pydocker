"""Tests for URL parsing and localhost detection utilities."""
import pytest
from llama_index_pydocker._utils import is_localhost, parse_url


@pytest.mark.parametrize("url,expected_host,expected_port", [
    ("bolt://localhost:7687",        "localhost", 7687),
    ("http://127.0.0.1:6333",       "127.0.0.1", 6333),
    ("http://0.0.0.0:9200",         "0.0.0.0",   9200),
    ("postgresql://user:pw@localhost:5432/db", "localhost", 5432),
    ("bolt://my-aura.neo4j.io:7687","my-aura.neo4j.io", 7687),
    ("https://cluster.qdrant.io:6333", "cluster.qdrant.io", 6333),
])
def test_parse_url(url, expected_host, expected_port):
    host, port = parse_url(url)
    assert host == expected_host
    assert port == expected_port


@pytest.mark.parametrize("host,expected", [
    ("localhost",  True),
    ("127.0.0.1",  True),
    ("0.0.0.0",    True),
    ("::1",        True),
    ("my-aura.neo4j.io", False),
    ("10.0.0.1",   False),
    ("cluster.qdrant.io", False),
])
def test_is_localhost(host, expected):
    assert is_localhost(host) is expected
