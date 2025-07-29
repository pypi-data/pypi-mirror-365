"""
Main client class for Sanctum AWS Cognito integration.
"""

from typing import Any, Callable, Dict, Optional

from .auth import (
    AdminAuthenticator,
    CognitoConfig,
    CustomAuthenticator,
    UserPasswordAuthenticator,
)
from .exceptions import AuthenticationError
from .info import ClientInfoManager
from .rbac import RBACManager
from .tokens import TokenManager
from .user import UserManager


class SanctumClient:
    """
    Developer-friendly AWS Cognito client with clean APIs for managing
    user pools and authentication flows.

    This is the main entry point that orchestrates various authentication
    flows and user management operations through specialized managers.
    """

    def __init__(
        self,
        user_pool_id: str,
        client_id: str,
        region: str = "us-east-1",
        client_secret: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Sanctum client.

        Args:
            user_pool_id: AWS Cognito User Pool ID
            client_id: AWS Cognito App Client ID
            region: AWS region (default: us-east-1)
            client_secret: Optional client secret for server-side apps
            **kwargs: Additional configuration options
        """
        # Create configuration
        self.config = CognitoConfig(
            user_pool_id=user_pool_id,
            client_id=client_id,
            region=region,
            client_secret=client_secret,
        )

        # Initialize managers
        self._user_password_auth = UserPasswordAuthenticator(self.config)
        self._admin_auth = AdminAuthenticator(self.config)
        self._custom_auth = CustomAuthenticator(self.config)
        self._token_manager = TokenManager(self.config)
        self._user_manager = UserManager(self.config)
        self._client_info_manager = ClientInfoManager(self.config)
        self._rbac_manager = RBACManager(self.config)

        # Maintain backward compatibility properties
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self.client_secret = client_secret

    # Client Information Methods
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get information about the Cognito User Pool client configuration.

        Returns:
            Dict containing client configuration details

        Raises:
            SanctumError: If unable to retrieve client information
        """
        return self._client_info_manager.get_client_info()

    def get_user_pool_info(self) -> Dict[str, Any]:
        """
        Get information about the Cognito User Pool.

        Returns:
            Dict containing user pool configuration details

        Raises:
            SanctumError: If unable to retrieve user pool information
        """
        return self._client_info_manager.get_user_pool_info()

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return status.

        Returns:
            Dict containing validation results

        Raises:
            SanctumError: If validation fails
        """
        return self._client_info_manager.validate_config()

    # Authentication Methods
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with username and password using USER_PASSWORD_AUTH flow.

        Args:
            username: User's username or email
            password: User's password

        Returns:
            Dict containing authentication tokens and user info

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If parameters are invalid
        """
        try:
            return self._user_password_auth.authenticate(username, password)
        except AuthenticationError:
            # Fallback to admin auth if user password auth fails
            try:
                return self._admin_auth.authenticate_admin_password(username, password)
            except Exception:
                raise AuthenticationError("Invalid username or password")

    def authenticate_admin(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user using ADMIN_USER_PASSWORD_AUTH flow.

        Args:
            username: User's username or email
            password: User's password

        Returns:
            Dict containing authentication tokens and user info

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If parameters are invalid
        """
        return self._admin_auth.authenticate_user_password(username, password)

    def authenticate_custom(
        self,
        username: str,
        challenge_responses: Optional[Dict[str, str]] = None,
        custom_challenge_handler: Optional[
            Callable[[Dict[str, Any]], Dict[str, str]]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Authenticate a user using CUSTOM_AUTH flow with custom challenges.

        Args:
            username: User's username or email
            challenge_responses: Pre-defined responses to custom challenges
            custom_challenge_handler: Callback function to handle custom challenges

        Returns:
            Dict containing authentication tokens and user info

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If parameters are invalid
        """
        return self._custom_auth.authenticate(
            username=username,
            challenge_responses=challenge_responses,
            custom_challenge_handler=custom_challenge_handler,
        )

    # Token Management Methods
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
        return self._token_manager.refresh_token(refresh_token)

    def respond_to_auth_challenge(
        self,
        challenge_name: str,
        challenge_responses: Dict[str, str],
        session: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Respond to authentication challenges (MFA, new password, etc.).

        Args:
            challenge_name: Challenge name (e.g., 'SMS_MFA', 'NEW_PASSWORD_REQUIRED')
            challenge_responses: Responses to the challenge
            session: Session token from auth call

        Returns:
            Dict containing response (may include next challenge or final result)
        """
        return self._token_manager.respond_to_auth_challenge(
            challenge_name, challenge_responses, session
        )

    # User Management Methods
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
        return self._user_manager.sign_up(
            username=username,
            password=password,
            email=email,
            **attributes,
        )

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
        return self._user_manager.confirm_sign_up(username, confirmation_code)

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
        return self._user_manager.get_user(access_token)

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
        return self._user_manager.resend_confirmation_code(username)

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
        return self._user_manager.initiate_forgot_password(username)

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
        return self._user_manager.confirm_forgot_password(
            username, confirmation_code, new_password
        )

    # RBAC Methods
    def create_group(
        self, group_name: str, description: str, precedence: int = 0
    ) -> Dict[str, Any]:
        """
        Create a new user group.

        Args:
            group_name: Name of the group
            description: Description of the group
            precedence: Group precedence (lower number = higher precedence)

        Returns:
            Dict containing group creation result

        Raises:
            ValidationError: If parameters are invalid
            SanctumError: If group creation fails
        """
        return self._rbac_manager.create_group(group_name, description, precedence)

    def assign_user_to_group(self, username: str, group_name: str) -> Dict[str, Any]:
        """
        Assign user to a group.

        Args:
            username: User's username
            group_name: Name of the group

        Returns:
            Dict containing assignment result

        Raises:
            ValidationError: If parameters are invalid
            SanctumError: If assignment fails
        """
        return self._rbac_manager.assign_user_to_group(username, group_name)

    def remove_user_from_group(self, username: str, group_name: str) -> Dict[str, Any]:
        """
        Remove user from a group.

        Args:
            username: User's username
            group_name: Name of the group

        Returns:
            Dict containing removal result

        Raises:
            ValidationError: If parameters are invalid
            SanctumError: If removal fails
        """
        return self._rbac_manager.remove_user_from_group(username, group_name)

    def get_user_groups(self, username: str) -> Dict[str, Any]:
        """
        Get all groups that a user belongs to.

        Args:
            username: User's username

        Returns:
            Dict containing user's groups

        Raises:
            ValidationError: If username is missing
            SanctumError: If retrieval fails
        """
        return self._rbac_manager.get_user_groups(username)

    def check_group_membership(self, access_token: str, required_group: str) -> bool:
        """
        Check if user belongs to a specific group.

        Args:
            access_token: JWT access token
            required_group: Required group name

        Returns:
            True if user belongs to the group

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If token is invalid
        """
        return self._rbac_manager.check_group_membership(access_token, required_group)

    def check_any_group_membership(
        self, access_token: str, required_groups: list
    ) -> bool:
        """
        Check if user belongs to any of the specified groups.

        Args:
            access_token: JWT access token
            required_groups: List of acceptable group names

        Returns:
            True if user belongs to any of the groups

        Raises:
            ValidationError: If parameters are invalid
            AuthenticationError: If token is invalid
        """
        return self._rbac_manager.check_any_group_membership(
            access_token, required_groups
        )

    def list_all_groups(self) -> Dict[str, Any]:
        """
        List all groups in the User Pool.

        Returns:
            Dict containing all groups

        Raises:
            SanctumError: If listing fails
        """
        return self._rbac_manager.list_all_groups()

    @property
    def rbac(self) -> RBACManager:
        """Access to RBAC manager for advanced operations."""
        return self._rbac_manager
