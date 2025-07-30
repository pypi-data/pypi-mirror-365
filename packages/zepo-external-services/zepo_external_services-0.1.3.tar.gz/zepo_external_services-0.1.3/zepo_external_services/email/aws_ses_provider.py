import asyncio
from typing import List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from zepo_external_services.core.config import BaseConfig
from zepo_external_services.core.factory import register_provider
from zepo_external_services.core.exceptions import (
    EmailProviderError,
    ConfigurationError,
)
from .base import AbstractEmailProvider


class AwsSesConfig(BaseConfig):
    """Pydantic model for AWS SES configuration."""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    from_email: str


@register_provider("email", "aws_ses")
class AwsSesEmailProvider(AbstractEmailProvider):
    """
    Concrete implementation of the Email provider for AWS SES.
    """

    def __init__(self, config: AwsSesConfig):
        super().__init__(config)

    def _initialize_client(self):
        """Initializes the AWS SES client."""
        try:
            return boto3.client(
                "ses",
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.aws_region,
            )
        except (BotoCoreError, ClientError) as e:
            raise ConfigurationError(f"Failed to initialize AWS SES client: {e}") from e

    def send(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        from_email: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an email using AWS SES.
        """
        self.logger.info(
            f"Attempting to send email to {', '.join(to)} with request_id: {request_id}"
        )
        try:
            response = self._client.send_email(
                Source=from_email or self.config.from_email,
                Destination={"ToAddresses": to},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Html": {"Data": body_html}},
                },
            )
            message_id = response["MessageId"]
            self.logger.info(
                f"Email sent successfully to {', '.join(to)}. Message ID: {message_id}"
            )
            return message_id
        except ClientError as e:
            self.logger.error(
                f"AWS SES error sending email: {e.response['Error']['Message']}",
                exc_info=True,
            )
            raise EmailProviderError(
                f"Failed to send email via AWS SES: {e.response['Error']['Message']}"
            ) from e
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {e}", exc_info=True)
            raise EmailProviderError(f"An unexpected error occurred: {e}") from e

    async def asend(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        from_email: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Sends an email asynchronously using asyncio.to_thread.
        """
        return await asyncio.to_thread(
            self.send,
            to=to,
            subject=subject,
            body_html=body_html,
            from_email=from_email,
            request_id=request_id,
        )
