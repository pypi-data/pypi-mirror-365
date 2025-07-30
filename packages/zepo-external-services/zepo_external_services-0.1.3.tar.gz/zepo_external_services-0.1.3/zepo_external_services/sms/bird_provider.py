import asyncio
from typing import Optional

import messagebird
from messagebird.client import ErrorException

from zepo_external_services.core.config import BaseConfig
from zepo_external_services.core.exceptions import (
    AuthenticationError,
    InvalidRecipientError,
    SmsProviderError,
)
from zepo_external_services.core.factory import register_provider
from zepo_external_services.sms.base import AbstractSmsProvider


class MessageBirdConfig(BaseConfig):
    access_key: str
    default_originator: str


@register_provider("sms", "bird")
class MessageBirdSmsProvider(AbstractSmsProvider):
    """
    Concrete implementation of the SMS provider for MessageBird.
    """

    def __init__(self, config: MessageBirdConfig):
        super().__init__(config)

    def _initialize_client(self) -> messagebird.Client:
        """Initializes the MessageBird client."""
        try:
            return messagebird.Client(self.config.access_key)
        except Exception as e:
            self.logger.error("Failed to initialize MessageBird client: %s", e)
            raise AuthenticationError("MessageBird authentication failed.") from e

    def send(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an SMS message using MessageBird's synchronous API.
        """
        self.logger.info(
            "Sending SMS via MessageBird to %s with request_id: %s", to, request_id
        )
        try:
            sent_message = self._client.message_create(
                originator=sender_id or self.config.default_originator,
                recipients=[to],
                body=message,
            )
            # Assuming the first recipient is the one we care about
            message_id = sent_message.recipients.items[0].message_id
            self.logger.info(
                "SMS sent successfully via MessageBird. Message ID: %s", message_id
            )
            return message_id
        except ErrorException as e:
            # MessageBird uses error codes to specify issues
            if any(error.code == 2 for error in e.errors):  # Invalid recipient
                self.logger.warning("Invalid recipient number for MessageBird: %s", to)
                raise InvalidRecipientError(f"Invalid 'to' number: {to}") from e
            self.logger.error("MessageBird API error: %s", e)
            raise SmsProviderError(f"Failed to send SMS via MessageBird: {e}") from e
        except Exception as e:
            self.logger.error("An unexpected error occurred with MessageBird: %s", e)
            raise SmsProviderError(f"An unexpected error occurred: {e}") from e

    async def asend(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an SMS message asynchronously using asyncio.to_thread.
        """
        return await asyncio.to_thread(
            self.send,
            to=to,
            message=message,
            sender_id=sender_id,
            request_id=request_id,
        )
