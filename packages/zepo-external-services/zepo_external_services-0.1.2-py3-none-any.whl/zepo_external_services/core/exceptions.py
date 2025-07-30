class ProviderError(Exception):
    """Base exception for the library."""

    pass


class ProviderNotFoundError(ProviderError):
    """Raised when a requested provider is not registered in the factory."""

    pass


class ConfigurationError(ProviderError):
    """Raised for missing or invalid configuration."""

    pass


class AuthenticationError(ProviderError):
    """Raised for credential-related issues."""

    pass


# Category-specific exceptions
class SmsProviderError(ProviderError):
    """Base exception for SMS services."""

    pass


class InvalidRecipientError(SmsProviderError):
    """Raised for invalid phone numbers."""

    pass


class EmailProviderError(ProviderError):
    """Base exception for Email services."""

    pass
