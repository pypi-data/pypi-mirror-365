"""
Authentication flow handlers for Sanctum AWS Cognito integration.
"""

import base64
import hashlib
import hmac
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

from .exceptions import AuthenticationError, ValidationError


class CognitoConfig:
    """Configuration container for AWS Cognito settings."""

    def __init__(
        self,
        user_pool_id: str,
        client_id: str,
        region: str = "us-east-1",
        client_secret: Optional[str] = None,
    ) -> None:
        """
        Initialize Cognito configuration.

        Args:
            user_pool_id: AWS Cognito User Pool ID
            client_id: AWS Cognito App Client ID
            region: AWS region (default: us-east-1)
            client_secret: Optional client secret for server-side apps
        """
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self.client_secret = client_secret

        # Validate required parameters
        if not user_pool_id:
            raise ValidationError("user_pool_id is required")
        if not client_id:
            raise ValidationError("client_id is required")


class SecretHashCalculator:
    """Utility class for calculating AWS Cognito SECRET_HASH."""

    @staticmethod
    def calculate(username: str, client_id: str, client_secret: str) -> str:
        """
        Calculate SECRET_HASH for AWS Cognito.

        Args:
            username: User's username
            client_id: Cognito client ID
            client_secret: Cognito client secret

        Returns:
            Base64 encoded SECRET_HASH
        """
        message = username + client_id
        return base64.b64encode(
            hmac.new(
                client_secret.encode(),
                message.encode(),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()


class BaseAuthenticator:
    """Base class for authentication handlers."""

    def __init__(self, config: CognitoConfig) -> None:
        """
        Initialize base authenticator.

        Args:
            config: Cognito configuration
        """
        self.config = config
        self._cognito_client = boto3.client("cognito-idp", region_name=config.region)

    def _add_secret_hash(self, auth_params: Dict[str, str], username: str) -> None:
        """Add SECRET_HASH to auth parameters if client secret is configured."""
        if self.config.client_secret:
            auth_params["SECRET_HASH"] = SecretHashCalculator.calculate(
                username, self.config.client_id, self.config.client_secret
            )


class UserPasswordAuthenticator(BaseAuthenticator):
    """Handler for USER_PASSWORD_AUTH flow."""

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate using USER_PASSWORD_AUTH flow.

        Args:
            username: User's username or email
            password: User's password

        Returns:
            Dict containing authentication tokens

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If parameters are invalid
        """
        if not username or not password:
            raise ValidationError("Username and password are required")

        try:
            auth_params = {"USERNAME": username, "PASSWORD": password}
            self._add_secret_hash(auth_params, username)

            response = self._cognito_client.initiate_auth(
                ClientId=self.config.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters=auth_params,
            )

            if "AuthenticationResult" not in response:
                raise AuthenticationError("Authentication failed")

            return response["AuthenticationResult"]

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NotAuthorizedException":
                raise AuthenticationError("Invalid username or password")
            elif error_code == "UserNotConfirmedException":
                raise AuthenticationError("User account is not confirmed")
            elif error_code == "UserNotFoundException":
                raise AuthenticationError("User not found")
            else:
                raise AuthenticationError(f"Authentication failed: {str(e)}")
        except Exception as e:
            error_message = str(e)
            if "Auth flow not enabled" in error_message:
                raise AuthenticationError(
                    "USER_PASSWORD_AUTH flow not enabled for this client. "
                    "Please enable USER_PASSWORD_AUTH in your Cognito User Pool client settings."
                )
            raise AuthenticationError(f"Authentication failed: {error_message}")


class AdminAuthenticator(BaseAuthenticator):
    """Handler for admin authentication flows."""

    def authenticate_admin_password(
        self, username: str, password: str
    ) -> Dict[str, Any]:
        """
        Authenticate using ADMIN_NO_SRP_AUTH flow.

        Args:
            username: User's username or email
            password: User's password

        Returns:
            Dict containing authentication tokens

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            auth_params = {"USERNAME": username, "PASSWORD": password}
            self._add_secret_hash(auth_params, username)

            response = self._cognito_client.admin_initiate_auth(
                UserPoolId=self.config.user_pool_id,
                ClientId=self.config.client_id,
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters=auth_params,
            )

            if "AuthenticationResult" not in response:
                raise AuthenticationError("Authentication failed")

            return response["AuthenticationResult"]

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NotAuthorizedException":
                raise AuthenticationError("Invalid username or password")
            else:
                raise AuthenticationError(f"Admin authentication failed: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Admin authentication failed: {str(e)}")

    def authenticate_user_password(
        self, username: str, password: str
    ) -> Dict[str, Any]:
        """
        Authenticate using ADMIN_USER_PASSWORD_AUTH flow.

        Args:
            username: User's username or email
            password: User's password

        Returns:
            Dict containing authentication tokens

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If parameters are invalid
        """
        if not username or not password:
            raise ValidationError("Username and password are required")

        try:
            auth_params = {"USERNAME": username, "PASSWORD": password}
            self._add_secret_hash(auth_params, username)

            response = self._cognito_client.admin_initiate_auth(
                UserPoolId=self.config.user_pool_id,
                ClientId=self.config.client_id,
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                AuthParameters=auth_params,
            )

            if "AuthenticationResult" not in response:
                raise AuthenticationError("Admin authentication failed")

            return response["AuthenticationResult"]

        except self._cognito_client.exceptions.NotAuthorizedException:
            raise AuthenticationError("Invalid username or password")
        except self._cognito_client.exceptions.UserNotConfirmedException:
            raise AuthenticationError("User account is not confirmed")
        except self._cognito_client.exceptions.UserNotFoundException:
            raise AuthenticationError("User not found")
        except Exception as e:
            error_message = str(e)
            if "Auth flow not enabled" in error_message:
                raise AuthenticationError(
                    "ADMIN_USER_PASSWORD_AUTH flow not enabled for this client. "
                    "Please enable ADMIN_USER_PASSWORD_AUTH in your Cognito User Pool client settings."
                )
            raise AuthenticationError(f"Admin authentication failed: {error_message}")


class CustomAuthenticator(BaseAuthenticator):
    """Handler for custom authentication flows."""

    def authenticate(
        self,
        username: str,
        challenge_responses: Optional[Dict[str, str]] = None,
        custom_challenge_handler: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Authenticate using CUSTOM_AUTH flow.

        Args:
            username: User's username or email
            challenge_responses: Pre-defined responses to custom challenges
            custom_challenge_handler: Callback function to handle custom challenges

        Returns:
            Dict containing authentication tokens

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If parameters are invalid
        """
        if not username:
            raise ValidationError("Username is required")

        try:
            auth_params = {"USERNAME": username}
            self._add_secret_hash(auth_params, username)

            response = self._cognito_client.initiate_auth(
                ClientId=self.config.client_id,
                AuthFlow="CUSTOM_AUTH",
                AuthParameters=auth_params,
            )

            # Handle custom challenges
            while response.get("ChallengeName") == "CUSTOM_CHALLENGE":
                challenge_params = response.get("ChallengeParameters", {})

                # Use provided responses or call custom handler
                if challenge_responses:
                    responses = challenge_responses.copy()
                elif custom_challenge_handler:
                    responses = custom_challenge_handler(challenge_params)
                else:
                    raise AuthenticationError(
                        "Custom challenge encountered but no handler or responses provided. "
                        f"Challenge parameters: {challenge_params}"
                    )

                # Add username and secret hash to responses
                responses["USERNAME"] = username
                if self.config.client_secret:
                    responses["SECRET_HASH"] = auth_params["SECRET_HASH"]

                response = self._cognito_client.respond_to_auth_challenge(
                    ClientId=self.config.client_id,
                    ChallengeName="CUSTOM_CHALLENGE",
                    ChallengeResponses=responses,
                    Session=response.get("Session"),
                )

            if "AuthenticationResult" not in response:
                raise AuthenticationError("Custom authentication failed")

            return response["AuthenticationResult"]

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NotAuthorizedException":
                raise AuthenticationError("Custom authentication not authorized")
            elif error_code == "UserNotConfirmedException":
                raise AuthenticationError("User account is not confirmed")
            elif error_code == "UserNotFoundException":
                raise AuthenticationError("User not found")
            else:
                raise AuthenticationError(f"Custom authentication failed: {str(e)}")
        except Exception as e:
            error_message = str(e)
            if "Auth flow not enabled" in error_message:
                raise AuthenticationError(
                    "CUSTOM_AUTH flow not enabled for this client. "
                    "Please enable CUSTOM_AUTH in your Cognito User Pool client settings."
                )
            raise AuthenticationError(f"Custom authentication failed: {error_message}")
