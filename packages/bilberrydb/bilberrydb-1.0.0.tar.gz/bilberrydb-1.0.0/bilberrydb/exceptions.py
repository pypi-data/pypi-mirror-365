# bilberrydb/exceptions.py
"""
Custom exceptions for BilberryDB SDK
"""


class BilberryError(Exception):
    """Base exception class for BilberryDB SDK"""
    pass


class AuthenticationError(BilberryError):
    """Raised when authentication fails"""
    pass


class ValidationError(BilberryError):
    """Raised when input validation fails"""
    pass


class NetworkError(BilberryError):
    """Raised when network-related errors occur"""
    pass


class APIError(BilberryError):
    """Raised when API returns an error response"""
    pass