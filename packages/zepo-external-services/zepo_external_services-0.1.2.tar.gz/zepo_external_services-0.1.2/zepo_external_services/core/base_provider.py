import logging
from abc import ABC, abstractmethod
from .config import BaseConfig


class BaseProvider(ABC):
    """Abstract base class for all service providers."""

    def __init__(self, config: BaseConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = self._initialize_client()
        self.logger.info(f"{self.__class__.__name__} initialized.")

    @abstractmethod
    def _initialize_client(self):
        """Initializes the third-party client using self.config."""
        raise NotImplementedError

    def connect(self):
        """Establishes a connection if needed (e.g., RabbitMQ). Can be a no-op."""
        pass

    def disconnect(self):
        """Closes a connection if needed. Can be a no-op."""
        pass

    def __enter__(self):
        """Allows the provider to be used as a context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures disconnection when the context is exited."""
        self.disconnect()

    def _handle_error(self, error, context=""):
        """Centralized error logging."""
        # ... (error logging logic)
        pass
