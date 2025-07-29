# bilberrydb/__init__.py
"""
BilberryDB - Python SDK for Image Vector Search
A simple and efficient vector database client for image similarity search.
"""

__version__ = "1.0.0"
__author__ = "BilberryDB Team"
__email__ = "support@bilberrydb.com"

from .client import BilberryClient
from .exceptions import (
    BilberryError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    APIError
)

def init(api_key=None, api_id=None, base_url="https://appbilberry.com"):
    """
    Initialize BilberryDB client

    Args:
        api_key (str, optional): API key for authentication
        api_id (str): User email/ID for API access
        base_url (str): Base URL for the API

    Returns:
        BilberryClient: Initialized client instance

    Example:
        >>> import bilberrydb as bd
        >>> client = bd.init(api_key="your-key", api_id="user@example.com")
    """
    return BilberryClient(api_key=api_key, api_id=api_id, base_url=base_url)