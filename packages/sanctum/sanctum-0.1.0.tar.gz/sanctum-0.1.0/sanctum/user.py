"""
User management for Sanctum AWS Cognito integration.
"""

from typing import Any, Dict

from .auth import BaseAuthenticator
from .exceptions import AuthenticationError, SanctumError, ValidationError


class UserManager(BaseAuthenticator):
    """Manager for user operations like registration, confirmation, and profile management."""

    def sign_up(
        self, username: str, password: str, email: str, **attributes: Any
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            username: Desired username
            password: User's password
            email: User's email address
            **attributes: Additional user attributes

        Returns:
            Dict containing user registration info

        Raises:
            ValidationError: If parameters are invalid
            SanctumError: If registration fails
        """
        if not username or not password or not email:
            raise ValidationError("Username, password, and email are required")

        try:
            # Prepare user attributes
            user_attributes = [{"Name": "email", "Value": email}]

            # Add additional attributes
            for attr_name, attr_value in attributes.items():
                user_attributes.append({"Name": attr_name, "Value": str(attr_value)})

            response = self._cognito_client.sign_up(
                ClientId=self.config.client_id,
                Username=username,
                Password=password,
                UserAttributes=user_attributes,
            )

            return {
                "user_sub": response["UserSub"],
                "confirmation_required": not response["UserConfirmed"],
            }

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "UsernameExistsException":
                raise ValidationError("Username already exists")
            elif error_code == "InvalidPasswordException":
                raise ValidationError("Password does not meet requirements")
            else:
                raise SanctumError(f"Sign up failed: {str(e)}")

    def confirm_sign_up(self, username: str, confirmation_code: str) -> Dict[str, Any]:
        """
        Confirm user registration with confirmation code.

        Args:
            username: User's username
            confirmation_code: Confirmation code sent to user

        Returns:
            Dict containing confirmation result

        Raises:
            ValidationError: If parameters are invalid
            SanctumError: If confirmation fails
        """
        if not username or not confirmation_code:
            raise ValidationError("Username and confirmation code are required")

        try:
            self._cognito_client.confirm_sign_up(
                ClientId=self.config.client_id,
                Username=username,
                ConfirmationCode=confirmation_code,
            )

            return {"confirmed": True}

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "CodeMismatchException":
                raise SanctumError("Invalid confirmation code")
            elif error_code == "ExpiredCodeException":
                raise SanctumError("Confirmation code has expired")
            elif error_code == "UserNotFoundException":
                raise SanctumError("User not found")
            else:
                raise SanctumError(f"Confirmation failed: {str(e)}")

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information using access token.

        Args:
            access_token: Valid access token

        Returns:
            Dict containing user information

        Raises:
            AuthenticationError: If token is invalid
            ValidationError: If access token is missing
        """
        if not access_token:
            raise ValidationError("Access token is required")

        try:
            response = self._cognito_client.get_user(AccessToken=access_token)

            # Convert user attributes to a more convenient format
            user_data = {
                "username": response["Username"],
                "user_attributes": {},
            }

            for attr in response.get("UserAttributes", []):
                user_data["user_attributes"][attr["Name"]] = attr["Value"]

            return user_data

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "NotAuthorizedException":
                raise AuthenticationError("Invalid or expired access token")
            else:
                raise AuthenticationError(f"Failed to get user information: {str(e)}")

    def resend_confirmation_code(self, username: str) -> Dict[str, Any]:
        """
        Resend confirmation code for user registration.

        Args:
            username: User's username

        Returns:
            Dict containing delivery information

        Raises:
            ValidationError: If username is missing
            SanctumError: If resend fails
        """
        if not username:
            raise ValidationError("Username is required")

        try:
            response = self._cognito_client.resend_confirmation_code(
                ClientId=self.config.client_id,
                Username=username,
            )

            return {
                "delivery_details": {
                    "delivery_medium": response.get("CodeDeliveryDetails", {}).get(
                        "DeliveryMedium"
                    ),
                    "destination": response.get("CodeDeliveryDetails", {}).get(
                        "Destination"
                    ),
                }
            }

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "UserNotFoundException":
                raise SanctumError("User not found")
            elif error_code == "InvalidParameterException":
                raise SanctumError(f"Invalid parameter: {str(e)}")
            else:
                raise SanctumError(f"Failed to resend confirmation code: {str(e)}")

    def initiate_forgot_password(self, username: str) -> Dict[str, Any]:
        """
        Initiate forgot password flow.

        Args:
            username: User's username

        Returns:
            Dict containing delivery information

        Raises:
            ValidationError: If username is missing
            SanctumError: If initiation fails
        """
        if not username:
            raise ValidationError("Username is required")

        try:
            response = self._cognito_client.forgot_password(
                ClientId=self.config.client_id,
                Username=username,
            )

            return {
                "delivery_details": {
                    "delivery_medium": response.get("CodeDeliveryDetails", {}).get(
                        "DeliveryMedium"
                    ),
                    "destination": response.get("CodeDeliveryDetails", {}).get(
                        "Destination"
                    ),
                }
            }

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "UserNotFoundException":
                raise SanctumError("User not found")
            else:
                raise SanctumError(f"Failed to initiate forgot password: {str(e)}")

    def confirm_forgot_password(
        self, username: str, confirmation_code: str, new_password: str
    ) -> Dict[str, Any]:
        """
        Confirm forgot password with new password.

        Args:
            username: User's username
            confirmation_code: Confirmation code received
            new_password: New password

        Returns:
            Dict containing confirmation result

        Raises:
            ValidationError: If parameters are invalid
            SanctumError: If confirmation fails
        """
        if not username or not confirmation_code or not new_password:
            raise ValidationError(
                "Username, confirmation code, and new password are required"
            )

        try:
            self._cognito_client.confirm_forgot_password(
                ClientId=self.config.client_id,
                Username=username,
                ConfirmationCode=confirmation_code,
                Password=new_password,
            )

            return {"confirmed": True}

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "CodeMismatchException":
                raise SanctumError("Invalid confirmation code")
            elif error_code == "ExpiredCodeException":
                raise SanctumError("Confirmation code has expired")
            elif error_code == "InvalidPasswordException":
                raise ValidationError("Password does not meet requirements")
            else:
                raise SanctumError(f"Failed to confirm forgot password: {str(e)}")
