"""
Custom exceptions for the Sanctum library.
"""


class SanctumError(Exception):
    """Base exception class for Sanctum library."""


class AuthenticationError(SanctumError):
    """Raised when authentication fails."""


class ValidationError(SanctumError):
    """Raised when input validation fails."""


class CognitoError(SanctumError):
    """Raised when AWS Cognito operations fail."""


class TokenError(SanctumError):
    """Raised when token operations fail."""


class UserPoolError(SanctumError):
    """Raised when user pool operations fail."""
