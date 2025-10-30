"""Migration tools for transitioning to UPSS."""

from typing import Callable, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def migrate_prompt(prompt_name: str):
    """
    Decorator for gradual migration from hardcoded prompts to UPSS.

    Usage:
        @migrate_prompt("assistant-system")
        async def get_system_prompt(user_id: str):
            return "fallback hardcoded prompt"

    Args:
        prompt_name: Name of the prompt in UPSS

    Returns:
        Decorator function
    """

    def decorator(fallback_func: Callable) -> Callable:
        @wraps(fallback_func)
        async def wrapper(*args: Any, **kwargs: Any) -> str:
            try:
                from ..core.client import UPSSClient

                async with UPSSClient() as client:
                    user_id = kwargs.get("user_id", "default@user")
                    prompt = await client.load(prompt_name, user_id=user_id)
                    logger.info(f"Loaded prompt from UPSS: {prompt_name}")
                    return prompt.content
            except Exception as e:
                logger.warning(
                    f"UPSS load failed for {prompt_name}, using fallback: {e}"
                )
                return await fallback_func(*args, **kwargs)

        return wrapper

    return decorator
