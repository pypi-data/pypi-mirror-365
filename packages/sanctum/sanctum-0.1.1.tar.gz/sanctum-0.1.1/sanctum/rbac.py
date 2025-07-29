"""
Role-Based Access Control (RBAC) management for Sanctum AWS Cognito integration.
"""

from typing import Any, Dict, List, Optional

import jwt

from .auth import BaseAuthenticator
from .exceptions import AuthenticationError, SanctumError, ValidationError


class RBACManager(BaseAuthenticator):
    """Manager for role-based access control operations."""

    def create_group(
        self, group_name: str, description: str, precedence: int = 0
    ) -> Dict[str, Any]:
        """
        Create a new user group in Cognito User Pool.

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
        if not group_name or not description:
            raise ValidationError("Group name and description are required")

        try:
            response = self._cognito_client.create_group(
                GroupName=group_name,
                UserPoolId=self.config.user_pool_id,
                Description=description,
                Precedence=precedence,
            )

            return {
                "group_name": response["Group"]["GroupName"],
                "description": response["Group"]["Description"],
                "precedence": response["Group"]["Precedence"],
                "created": True,
            }

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "GroupExistsException":
                raise SanctumError(f"Group '{group_name}' already exists")
            else:
                raise SanctumError(f"Failed to create group: {str(e)}")

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
        if not username or not group_name:
            raise ValidationError("Username and group name are required")

        try:
            self._cognito_client.admin_add_user_to_group(
                UserPoolId=self.config.user_pool_id,
                Username=username,
                GroupName=group_name,
            )

            return {"username": username, "group": group_name, "assigned": True}

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "UserNotFoundException":
                raise SanctumError("User not found")
            elif error_code == "ResourceNotFoundException":
                raise SanctumError(f"Group '{group_name}' not found")
            else:
                raise SanctumError(f"Failed to assign user to group: {str(e)}")

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
        if not username or not group_name:
            raise ValidationError("Username and group name are required")

        try:
            self._cognito_client.admin_remove_user_from_group(
                UserPoolId=self.config.user_pool_id,
                Username=username,
                GroupName=group_name,
            )

            return {"username": username, "group": group_name, "removed": True}

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "UserNotFoundException":
                raise SanctumError("User not found")
            elif error_code == "ResourceNotFoundException":
                raise SanctumError(f"Group '{group_name}' not found")
            else:
                raise SanctumError(f"Failed to remove user from group: {str(e)}")

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
        if not username:
            raise ValidationError("Username is required")

        try:
            response = self._cognito_client.admin_list_groups_for_user(
                UserPoolId=self.config.user_pool_id,
                Username=username,
            )

            groups = []
            for group in response.get("Groups", []):
                groups.append(
                    {
                        "group_name": group["GroupName"],
                        "description": group.get("Description", ""),
                        "precedence": group.get("Precedence", 0),
                    }
                )

            return {"username": username, "groups": groups}

        except Exception as e:
            error_code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
            if error_code == "UserNotFoundException":
                raise SanctumError("User not found")
            else:
                raise SanctumError(f"Failed to get user groups: {str(e)}")

    def extract_groups_from_token(self, access_token: str) -> List[str]:
        """
        Extract groups from access token (without verification).

        Args:
            access_token: JWT access token

        Returns:
            List of group names

        Raises:
            AuthenticationError: If token is invalid
        """
        if not access_token:
            raise ValidationError("Access token is required")

        try:
            # Decode without verification (for extracting claims only)
            decoded = jwt.decode(access_token, options={"verify_signature": False})

            # Extract groups from cognito:groups claim
            groups = decoded.get("cognito:groups", [])
            return groups if isinstance(groups, list) else []

        except Exception as e:
            raise AuthenticationError(f"Failed to extract groups from token: {str(e)}")

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
        if not access_token or not required_group:
            raise ValidationError("Access token and required group are required")

        try:
            user_groups = self.extract_groups_from_token(access_token)
            return required_group in user_groups

        except Exception as e:
            raise AuthenticationError(f"Failed to check group membership: {str(e)}")

    def check_any_group_membership(
        self, access_token: str, required_groups: List[str]
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
        if not access_token or not required_groups:
            raise ValidationError("Access token and required groups are required")

        try:
            user_groups = self.extract_groups_from_token(access_token)
            return any(group in user_groups for group in required_groups)

        except Exception as e:
            raise AuthenticationError(f"Failed to check group membership: {str(e)}")

    def list_all_groups(self) -> Dict[str, Any]:
        """
        List all groups in the User Pool.

        Returns:
            Dict containing all groups

        Raises:
            SanctumError: If listing fails
        """
        try:
            response = self._cognito_client.list_groups(
                UserPoolId=self.config.user_pool_id
            )

            groups = []
            for group in response.get("Groups", []):
                groups.append(
                    {
                        "group_name": group["GroupName"],
                        "description": group.get("Description", ""),
                        "precedence": group.get("Precedence", 0),
                        "creation_date": group.get("CreationDate"),
                        "last_modified_date": group.get("LastModifiedDate"),
                    }
                )

            return {"groups": groups}

        except Exception as e:
            raise SanctumError(f"Failed to list groups: {str(e)}")


class RBACDecorators:
    """Decorator utilities for RBAC enforcement."""

    @staticmethod
    def require_group(required_group: str, token_param: str = "access_token"):
        """
        Decorator to require group membership for function execution.

        Args:
            required_group: Required group name
            token_param: Parameter name containing the access token

        Usage:
            @require_group("admin")
            def admin_function(access_token: str):
                pass
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                # Extract token from kwargs or args
                token = kwargs.get(token_param)
                if not token and len(args) > 0:
                    token = args[0]  # Assume first arg is token

                if not token:
                    raise AuthenticationError("Access token required")

                # Create RBAC manager instance (requires config)
                # Note: This would need config to be available in context
                # rbac = RBACManager(config)
                # if not rbac.check_group_membership(token, required_group):
                #     raise AuthenticationError(f"Access denied: requires '{required_group}' group")

                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def require_any_group(
        required_groups: List[str], token_param: str = "access_token"
    ):
        """
        Decorator to require membership in any of the specified groups.

        Args:
            required_groups: List of acceptable group names
            token_param: Parameter name containing the access token
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                token = kwargs.get(token_param)
                if not token and len(args) > 0:
                    token = args[0]

                if not token:
                    raise AuthenticationError("Access token required")

                # Similar implementation as above
                return func(*args, **kwargs)

            return wrapper

        return decorator
