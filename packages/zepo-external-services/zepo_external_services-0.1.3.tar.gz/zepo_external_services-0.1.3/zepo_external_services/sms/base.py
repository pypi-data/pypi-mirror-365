from abc import abstractmethod
from typing import Optional

from zepo_external_services.core.base_provider import BaseProvider


class AbstractSmsProvider(BaseProvider):
    """Abstract interface for all SMS providers."""

    @abstractmethod
    def send(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an SMS message synchronously.
        Returns the message ID from the provider.
        Raises:
            SmsProviderError: If the message fails to send.
        """
        raise NotImplementedError

    @abstractmethod
    async def asend(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an SMS message asynchronously.
        For providers with synchronous SDKs, this should be implemented
        using asyncio.to_thread to avoid blocking the event loop.
        """
        raise NotImplementedError
