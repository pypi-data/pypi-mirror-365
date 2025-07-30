"""
Service factory for creating and managing providers.
"""

from .exceptions import ProviderNotFoundError

PROVIDER_REGISTRY = {"sms": {}, "email": {}, "directory": {}}  # etc.


def register_provider(category: str, name: str):
    """
    A class decorator to auto-register providers in the factory.
    """

    def decorator(cls):
        if category not in PROVIDER_REGISTRY:
            PROVIDER_REGISTRY[category] = {}
        PROVIDER_REGISTRY[category][name] = cls
        return cls

    return decorator


def get_provider(category: str, name: str, config):
    """
    Gets a provider instance from the registry.
    """
    try:
        provider_class = PROVIDER_REGISTRY[category][name]
    except KeyError as e:
        raise ProviderNotFoundError(
            f"Provider '{name}' not found for category '{category}'."
        ) from e
    return provider_class(config=config)


def list_providers(category: str):
    """
    Lists all available providers for a given category.
    """
    return list(PROVIDER_REGISTRY.get(category, {}).keys())


__all__ = ["register_provider", "get_provider", "list_providers"]
