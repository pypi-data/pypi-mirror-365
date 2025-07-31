"""
SPT Neo RAG Client.

A Python client library for interacting with the SPT Neo RAG API.
"""

__version__ = "0.2.0"

from .client import NeoRagClient
from .exceptions import (
    NeoRagException,
    NeoRagApiError,
    AuthenticationError,
    ConfigurationError,
    NetworkError,
)

__all__ = [
    "NeoRagClient",
    "NeoRagException",
    "NeoRagApiError",
    "AuthenticationError", 
    "ConfigurationError",
    "NetworkError",
]
