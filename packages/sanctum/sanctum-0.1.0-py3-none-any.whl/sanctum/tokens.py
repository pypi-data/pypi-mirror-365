"""
Token management for Sanctum AWS Cognito integration.
"""

from typing import Any, Dict, Optional

import boto3

from .auth import BaseAuthenticator, CognitoConfig
from .exceptions import AuthenticationError, ValidationError


class TokenManager(BaseAuthenticator):
    """Manager for token operations like refresh and validation."""

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict containing new tokens

        Raises:
            AuthenticationError: If token refresh fails
            ValidationError: If refresh token is invalid
        """
        if not refresh_token:
            raise ValidationError("Refresh token is required")

        try:
            response = self._cognito_client.initiate_auth(
                ClientId=self.config.client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token},
            )

            if "AuthenticationResult" not in response:
                raise AuthenticationError("Token refresh failed")

            return response["AuthenticationResult"]

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "NotAuthorizedException":
                raise AuthenticationError("Invalid refresh token")
            else:
                raise AuthenticationError(f"Token refresh failed: {str(e)}")

    def respond_to_auth_challenge(
        self,
        challenge_name: str,
        challenge_responses: Dict[str, str],
        session: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Respond to authentication challenges (MFA, new password, etc.).

        Args:
            challenge_name: Name of the challenge (e.g., 'SMS_MFA', 'NEW_PASSWORD_REQUIRED')
            challenge_responses: Responses to the challenge
            session: Session token from previous auth call

        Returns:
            Dict containing authentication result or next challenge

        Raises:
            AuthenticationError: If challenge response fails
            ValidationError: If parameters are invalid
        """
        if not challenge_name or not challenge_responses:
            raise ValidationError("Challenge name and responses are required")

        try:
            params = {
                "ClientId": self.config.client_id,
                "ChallengeName": challenge_name,
                "ChallengeResponses": challenge_responses,
            }

            # Only add Session if it's provided and not empty
            if session:
                params["Session"] = session

            response = self._cognito_client.respond_to_auth_challenge(**params)

            return response

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "NotAuthorizedException":
                raise AuthenticationError("Challenge response not authorized")
            elif error_code == "CodeMismatchException":
                raise AuthenticationError("Invalid challenge response code")
            elif error_code == "ExpiredCodeException":
                raise AuthenticationError("Challenge response code has expired")
            else:
                raise AuthenticationError(f"Challenge response failed: {str(e)}")
