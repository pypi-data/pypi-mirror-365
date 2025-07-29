"""
Sanctum - Developer-friendly AWS Cognito client for Python.

A clean, intuitive API for managing user pools and authentication flows.
"""

__version__ = "0.1.0"
__author__ = "Sydel Palinlin"
__email__ = "sydel.palinlin@gmail.com"

# Advanced classes for direct use (optional)
from .auth import (
    AdminAuthenticator,
    CognitoConfig,
    CustomAuthenticator,
    SecretHashCalculator,
    UserPasswordAuthenticator,
)

# Main client (primary interface)
from .client import SanctumClient

# Exception classes
from .exceptions import AuthenticationError, SanctumError, ValidationError
from .info import ClientInfoManager
from .rbac import RBACManager
from .tokens import TokenManager
from .user import UserManager

__all__ = [
    # Main interface
    "SanctumClient",
    # Exceptions
    "SanctumError",
    "AuthenticationError",
    "ValidationError",
    # Advanced components (for direct use)
    "CognitoConfig",
    "SecretHashCalculator",
    "UserPasswordAuthenticator",
    "AdminAuthenticator",
    "CustomAuthenticator",
    "TokenManager",
    "UserManager",
    "ClientInfoManager",
    "RBACManager",
]
