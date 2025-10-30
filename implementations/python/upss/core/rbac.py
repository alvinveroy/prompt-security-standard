"""RBAC (Role-Based Access Control) for UPSS."""

import json
from pathlib import Path
from typing import Dict, List, Set

from ..core.exceptions import PermissionError


class RBACManager:
    """Manages role-based access control for UPSS."""

    def __init__(self, roles_file: Path):
        """
        Initialize RBAC manager.

        Args:
            roles_file: Path to roles.json file
        """
        self.roles_file = roles_file
        self._ensure_file()

    def _ensure_file(self):
        """Ensure roles file exists with default structure."""
        if not self.roles_file.exists():
            default_roles = {
                "roles": {
                    "reader": ["read"],
                    "writer": ["read", "write"],
                    "admin": ["read", "write", "approve", "deploy"],
                },
                "assignments": {},
            }
            with open(self.roles_file, "w", encoding="utf-8") as f:
                json.dump(default_roles, f, indent=2)

    def _load_roles(self) -> Dict:
        """Load roles configuration."""
        with open(self.roles_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_roles(self, roles_data: Dict):
        """Save roles configuration."""
        with open(self.roles_file, "w", encoding="utf-8") as f:
            json.dump(roles_data, f, indent=2)

    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        Check if user has permission.

        Args:
            user_id: User identifier
            permission: Required permission (read, write, approve, deploy)

        Returns:
            True if user has permission

        Raises:
            PermissionError: If user lacks permission
        """
        roles_data = self._load_roles()
        user_roles = roles_data.get("assignments", {}).get(user_id, [])

        # Collect all permissions from user's roles
        user_permissions: Set[str] = set()
        for role in user_roles:
            role_permissions = roles_data.get("roles", {}).get(role, [])
            user_permissions.update(role_permissions)

        if permission not in user_permissions:
            raise PermissionError(
                f"User {user_id} lacks permission: {permission}",
                details={"user_id": user_id, "required": permission},
            )

        return True

    def assign_role(self, user_id: str, role: str):
        """
        Assign a role to a user.

        Args:
            user_id: User identifier
            role: Role name
        """
        roles_data = self._load_roles()

        if role not in roles_data.get("roles", {}):
            raise ValueError(f"Role not found: {role}")

        if user_id not in roles_data["assignments"]:
            roles_data["assignments"][user_id] = []

        if role not in roles_data["assignments"][user_id]:
            roles_data["assignments"][user_id].append(role)

        self._save_roles(roles_data)

    def revoke_role(self, user_id: str, role: str):
        """
        Revoke a role from a user.

        Args:
            user_id: User identifier
            role: Role name
        """
        roles_data = self._load_roles()

        if user_id in roles_data.get("assignments", {}):
            if role in roles_data["assignments"][user_id]:
                roles_data["assignments"][user_id].remove(role)
                self._save_roles(roles_data)

    def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get roles assigned to a user.

        Args:
            user_id: User identifier

        Returns:
            List of role names
        """
        roles_data = self._load_roles()
        return roles_data.get("assignments", {}).get(user_id, [])
