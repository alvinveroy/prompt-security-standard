"""
Simple role-based access control middleware.

This module provides basic RBAC without requiring complex infrastructure.
"""

from typing import Dict, Optional, Set

from ..core.middleware import SecurityContext, SecurityMiddleware, SecurityResult


class SimpleRBAC(SecurityMiddleware):
    """
    Simple role-based access control middleware.

    Enforces access control based on user roles and prompt categories.
    Uses a simple mapping of roles to allowed categories.

    Default roles:
    - admin: Can access all prompt categories
    - developer: Can access user and fallback prompts
    - user: Can only access user prompts

    Example:
        pipeline = SecurityPipeline()
        pipeline.use(SimpleRBAC())

        # Or with custom roles
        pipeline.use(SimpleRBAC(roles_config={
            "admin": {"system", "user", "fallback"},
            "developer": {"user", "fallback"},
            "user": {"user"}
        }))

        # Use with context metadata
        context = SecurityContext(
            user_id="alice",
            prompt_id="system-prompt",
            metadata={"role": "user", "category": "system"}
        )
        result = await pipeline.execute(prompt, context)
    """

    DEFAULT_ROLES = {
        "admin": {"system", "user", "fallback", "internal"},
        "developer": {"user", "fallback", "internal"},
        "user": {"user"},
    }

    def __init__(self, roles_config: Optional[Dict[str, Set[str]]] = None):
        """
        Initialize RBAC middleware.

        Args:
            roles_config: Mapping of role names to sets of allowed categories
        """
        self.roles = roles_config if roles_config is not None else self.DEFAULT_ROLES

    async def process(self, prompt: str, context: SecurityContext) -> SecurityResult:
        """
        Check if user's role allows access to the prompt category.

        Args:
            prompt: The prompt text
            context: Security context (must include 'role' and 'category' in metadata)

        Returns:
            SecurityResult indicating whether access is allowed
        """
        # Get role and category from context metadata
        metadata = context.metadata or {}
        user_role = metadata.get("role", "user")
        prompt_category = metadata.get("category", "user")

        # Get allowed categories for this role
        allowed_categories = self.roles.get(user_role, set())

        # Check if access is allowed
        if prompt_category not in allowed_categories:
            return SecurityResult(
                prompt=prompt,
                is_safe=False,
                risk_score=1.0,
                violations=[
                    f"Access denied: Role '{user_role}' cannot access "
                    f"category '{prompt_category}'"
                ],
                metadata={
                    "rbac_check": "failed",
                    "user_role": user_role,
                    "prompt_category": prompt_category,
                    "allowed_categories": list(allowed_categories),
                },
            )

        # Access allowed
        return SecurityResult(
            prompt=prompt,
            is_safe=True,
            risk_score=0.0,
            violations=[],
            metadata={
                "rbac_check": "passed",
                "user_role": user_role,
                "prompt_category": prompt_category,
            },
        )

    def add_role(self, role: str, categories: Set[str]) -> None:
        """
        Add or update a role.

        Args:
            role: Role name
            categories: Set of allowed categories for this role
        """
        self.roles[role] = categories

    def remove_role(self, role: str) -> None:
        """
        Remove a role.

        Args:
            role: Role name to remove
        """
        if role in self.roles:
            del self.roles[role]

    def get_role_permissions(self, role: str) -> Set[str]:
        """
        Get allowed categories for a role.

        Args:
            role: Role name

        Returns:
            Set of allowed categories, or empty set if role doesn't exist
        """
        return self.roles.get(role, set())
