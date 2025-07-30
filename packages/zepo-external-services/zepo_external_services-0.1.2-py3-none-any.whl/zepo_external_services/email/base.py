from abc import abstractmethod
from typing import List, Optional

from zepo_external_services.core.base_provider import BaseProvider


class AbstractEmailProvider(BaseProvider):
    """Abstract interface for all Email providers."""

    @abstractmethod
    def send(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        from_email: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an email message synchronously.
        Returns the message ID from the provider.
        Raises:
            EmailProviderError: If the message fails to send.
        """
        raise NotImplementedError

    @abstractmethod
    async def asend(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        from_email: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an email message asynchronously.
        For providers with synchronous SDKs, this should be implemented
        using asyncio.to_thread to avoid blocking the event loop.
        """
        raise NotImplementedError
