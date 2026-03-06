"""
llama-index-pydocker
--------------------
Drop-in replacements for LlamaIndex store classes that automatically provision
Docker containers via py-dockerdb when the target host is localhost.

Each integration is guarded by a try/except so that importing this package
only requires the extras relevant to the stores you actually use.
"""

__all__ = []

try:
    from llama_index_pydocker.graph_stores import Neo4jGraphStore
    __all__.append("Neo4jGraphStore")
except ImportError:
    pass

try:
    from llama_index_pydocker.vector_stores import QdrantVectorStore
    __all__.append("QdrantVectorStore")
except ImportError:
    pass

try:
    from llama_index_pydocker.vector_stores import PGVectorStore
    __all__.append("PGVectorStore")
except ImportError:
    pass

try:
    from llama_index_pydocker.vector_stores import OpensearchVectorStore
    __all__.append("OpensearchVectorStore")
except ImportError:
    pass

try:
    from llama_index_pydocker.llms import Ollama
    __all__.append("Ollama")
except ImportError:
    pass

try:
    from llama_index_pydocker.embeddings import OllamaEmbedding
    __all__.append("OllamaEmbedding")
except ImportError:
    pass
