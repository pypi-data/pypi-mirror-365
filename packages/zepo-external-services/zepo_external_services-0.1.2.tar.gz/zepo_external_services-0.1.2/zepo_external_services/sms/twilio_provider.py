import asyncio
from typing import Optional

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from zepo_external_services.core.config import BaseConfig
from zepo_external_services.core.exceptions import (
    AuthenticationError,
    InvalidRecipientError,
    SmsProviderError,
)
from zepo_external_services.core.factory import register_provider
from zepo_external_services.sms.base import AbstractSmsProvider


class TwilioConfig(BaseConfig):
    account_sid: str
    auth_token: str
    from_number: str


@register_provider("sms", "twilio")
class TwilioSmsProvider(AbstractSmsProvider):
    """
    Concrete implementation of the SMS provider for Twilio.
    """

    def __init__(self, config: TwilioConfig):
        super().__init__(config)

    def _initialize_client(self) -> Client:
        """Initializes the Twilio client."""
        try:
            return Client(self.config.account_sid, self.config.auth_token)
        except Exception as e:
            self.logger.error("Failed to initialize Twilio client: %s", e)
            raise AuthenticationError("Twilio authentication failed.") from e

    def send(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an SMS message using Twilio's synchronous API.
        """
        self.logger.info(
            "Sending SMS via Twilio to %s with request_id: %s", to, request_id
        )
        try:
            sent_message = self._client.messages.create(
                to=to,
                from_=sender_id or self.config.from_number,
                body=message,
            )
            self.logger.info(
                "SMS sent successfully via Twilio. Message SID: %s", sent_message.sid
            )
            return sent_message.sid
        except TwilioRestException as e:
            if e.code == 21211:
                self.logger.warning("Invalid recipient number for Twilio: %s", to)
                raise InvalidRecipientError(f"Invalid 'to' number: {to}") from e
            self.logger.error("Twilio API error: %s", e)
            raise SmsProviderError(f"Failed to send SMS via Twilio: {e}") from e
        except Exception as e:
            self.logger.error("An unexpected error occurred with Twilio: %s", e)
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
