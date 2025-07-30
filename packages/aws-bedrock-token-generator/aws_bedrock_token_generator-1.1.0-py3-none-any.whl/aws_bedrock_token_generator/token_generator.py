"""
AWS Bedrock Token Generator

This module provides the BedrockTokenGenerator class for generating short-term bearer tokens
for AWS Bedrock API authentication using SigV4 signed requests.
"""

import base64

from botocore.auth import SigV4QueryAuth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

DEFAULT_HOST: str = "bedrock.amazonaws.com"
DEFAULT_URL: str = f"https://{DEFAULT_HOST}/"
SERVICE_NAME: str = "bedrock"
AUTH_PREFIX: str = "bedrock-api-key-"
TOKEN_VERSION: str = "&Version=1"
TOKEN_DURATION: int = 43200  # 12 hours in seconds


def _generate_token(credentials: Credentials, region: str, expires: int) -> str:
    """
    Internal method to build the presigned bearer token.

    Args:
        credentials: AWS credentials.
        region: AWS region.
        expires: Expiry time in seconds.

    Returns:
        A base64-encoded bearer token string.
    """
    request = AWSRequest(
        method="POST",
        url=DEFAULT_URL,
        headers={"host": DEFAULT_HOST},
        params={"Action": "CallWithBearerToken"},
    )

    auth = SigV4QueryAuth(credentials, SERVICE_NAME, region, expires=expires)
    auth.add_auth(request)

    presigned_url = request.url.replace("https://", "") + TOKEN_VERSION
    encoded_token = base64.b64encode(presigned_url.encode("utf-8")).decode("utf-8")

    return f"{AUTH_PREFIX}{encoded_token}"


class BedrockTokenGenerator:
    """Generates short-lived AWS Bedrock bearer tokens."""

    def __init__(self) -> None:
        pass

    def get_token(self, credentials: Credentials, region: str) -> str:
        """
        Generate a token using provided credentials and region.

        Args:
            credentials: AWS credentials to sign the request.
            region: AWS region.

        Returns:
            A bearer token string.

        Raises:
            ValueError: If inputs are invalid.
        """
        if not credentials:
            raise ValueError("Credentials cannot be None")

        if not region or not isinstance(region, str):
            raise ValueError("Region must be a non-empty string")

        return _generate_token(credentials, region, TOKEN_DURATION)
