"""Core components for the zepo-external-services library."""

from .base_provider import BaseProvider
from .config import BaseConfig
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    EmailProviderError,
    InvalidRecipientError,
    ProviderError,
    ProviderNotFoundError,
    SmsProviderError,
)
from .factory import get_provider, list_providers, register_provider

__all__ = [
    "BaseProvider",
    "BaseConfig",
    "ProviderError",
    "ProviderNotFoundError",
    "ConfigurationError",
    "AuthenticationError",
    "SmsProviderError",
    "InvalidRecipientError",
    "EmailProviderError",
    "register_provider",
    "get_provider",
    "list_providers",
]
