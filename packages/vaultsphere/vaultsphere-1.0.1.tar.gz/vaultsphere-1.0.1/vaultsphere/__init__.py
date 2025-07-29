"""
VaultSphere - La mejor librería NoSQL cifrada del siglo 🚀🔒

Módulo principal que expone la clase VaultSphere y funciones útiles de cifrado.
"""

from .core import VaultSphere
from .crypto import generate_key, encrypt, decrypt
from .schema import validate_document
from .index import IndexManager
from .utils import match_query, apply_query_operator

__all__ = [
    "VaultSphere",
    "generate_key",
    "encrypt",
    "decrypt",
    "validate_document",
    "IndexManager",
    "match_query",
    "apply_query_operator",
]
