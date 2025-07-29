"""
Client information management for Sanctum AWS Cognito integration.
"""

from typing import Any, Dict

from .auth import BaseAuthenticator
from .exceptions import SanctumError


class ClientInfoManager(BaseAuthenticator):
    """Manager for client configuration and information."""

    def get_client_info(self) -> Dict[str, Any]:
        """
        Get information about the Cognito User Pool client configuration.

        Returns:
            Dict containing client configuration details

        Raises:
            SanctumError: If unable to retrieve client information
        """
        try:
            response = self._cognito_client.describe_user_pool_client(
                UserPoolId=self.config.user_pool_id, ClientId=self.config.client_id
            )

            client_details = response["UserPoolClient"]

            return {
                "client_name": client_details.get("ClientName"),
                "explicit_auth_flows": client_details.get("ExplicitAuthFlows", []),
                "generate_secret": client_details.get("GenerateSecret", False),
                "refresh_token_validity": client_details.get("RefreshTokenValidity"),
                "access_token_validity": client_details.get("AccessTokenValidity"),
                "id_token_validity": client_details.get("IdTokenValidity"),
            }
        except Exception as e:
            raise SanctumError(f"Failed to get client information: {str(e)}")

    def get_user_pool_info(self) -> Dict[str, Any]:
        """
        Get information about the Cognito User Pool.

        Returns:
            Dict containing user pool configuration details

        Raises:
            SanctumError: If unable to retrieve user pool information
        """
        try:
            response = self._cognito_client.describe_user_pool(
                UserPoolId=self.config.user_pool_id
            )

            pool_details = response["UserPool"]

            return {
                "pool_name": pool_details.get("Name"),
                "creation_date": pool_details.get("CreationDate"),
                "last_modified_date": pool_details.get("LastModifiedDate"),
                "status": pool_details.get("Status"),
                "policies": pool_details.get("Policies", {}),
                "auto_verified_attributes": pool_details.get(
                    "AutoVerifiedAttributes", []
                ),
                "verification_message_template": pool_details.get(
                    "VerificationMessageTemplate", {}
                ),
                "mfa_configuration": pool_details.get("MfaConfiguration"),
            }
        except Exception as e:
            raise SanctumError(f"Failed to get user pool information: {str(e)}")

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return status.

        Returns:
            Dict containing validation results

        Raises:
            SanctumError: If validation fails
        """
        try:
            client_info = self.get_client_info()

            # Check for common configuration issues
            issues = []
            recommendations = []

            # Check auth flows
            auth_flows = client_info.get("explicit_auth_flows", [])
            if not auth_flows:
                issues.append("No explicit auth flows configured")
            else:
                if "ALLOW_USER_PASSWORD_AUTH" not in auth_flows:
                    recommendations.append(
                        "Consider enabling ALLOW_USER_PASSWORD_AUTH for basic authentication"
                    )
                if "ALLOW_ADMIN_USER_PASSWORD_AUTH" not in auth_flows:
                    recommendations.append(
                        "Consider enabling ALLOW_ADMIN_USER_PASSWORD_AUTH for admin operations"
                    )
                if "ALLOW_REFRESH_TOKEN_AUTH" not in auth_flows:
                    issues.append(
                        "ALLOW_REFRESH_TOKEN_AUTH should be enabled for token refresh"
                    )

            # Check client secret configuration
            has_secret = client_info.get("generate_secret", False)
            if has_secret and not self.config.client_secret:
                issues.append(
                    "Client has secret but no secret provided in configuration"
                )
            elif not has_secret and self.config.client_secret:
                issues.append(
                    "Client secret provided but client doesn't generate secret"
                )

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "recommendations": recommendations,
                "auth_flows": auth_flows,
                "has_secret": has_secret,
            }
        except Exception as e:
            raise SanctumError(f"Failed to validate configuration: {str(e)}")
