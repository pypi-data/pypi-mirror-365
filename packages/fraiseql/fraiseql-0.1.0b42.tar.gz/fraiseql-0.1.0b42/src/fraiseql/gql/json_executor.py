"""JSON passthrough executor for optimized GraphQL queries.

This module provides the integration between GraphQL resolvers and raw JSON
passthrough, enabling direct database-to-HTTP response flow.
"""

import inspect
import logging
import re
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def should_use_json_passthrough(context: dict[str, Any]) -> bool:
    """Determine if JSON passthrough should be used for this request.

    Args:
        context: The GraphQL request context

    Returns:
        True if JSON passthrough is enabled and conditions are met
    """
    # Check if explicitly enabled
    if not context.get("json_passthrough", False):
        return False

    # Only in production mode
    if context.get("mode") != "production":
        return False

    # Check if database supports raw JSON methods
    db = context.get("db")
    if not db or not hasattr(db, "find_raw_json"):
        return False

    return True


async def execute_json_query(fn: Callable, info: Any, **kwargs: Any) -> Any:
    """Execute a query function with JSON passthrough optimization if possible.

    This function analyzes the resolver to determine if it can use raw JSON
    passthrough and executes it accordingly.

    Args:
        fn: The resolver function
        info: GraphQL resolve info
        **kwargs: Query arguments

    Returns:
        Either a RawJSONResult for passthrough or regular Python objects
    """
    # Get the database from context
    context = getattr(info, "context", {})
    db = context.get("db")

    if not db:
        # Fall back to normal execution
        return await fn(info, **kwargs)

    # Try to analyze the function for simple patterns
    try:
        source = inspect.getsource(fn)

        # Extract the GraphQL field name from info
        field_name = info.field_name

        # Look for simple db.find_one patterns
        find_one_match = re.search(
            r'(?:return\s+)?(?:await\s+)?db\.find_one\s*\(\s*["\']([^"\']+)["\']', source
        )
        if find_one_match:
            view_name = find_one_match.group(1)
            logger.debug(f"Using raw JSON for find_one query on {view_name}")

            # Check if there are complex filters or custom logic
            if _has_complex_logic(source):
                logger.debug("Complex logic detected, falling back to normal execution")
                return await fn(info, **kwargs)

            # Execute with raw JSON
            result = await db.find_one_raw_json(view_name, field_name, **kwargs)
            return result

        # Look for simple db.find patterns
        find_match = re.search(
            r'(?:return\s+)?(?:await\s+)?db\.find\s*\(\s*["\']([^"\']+)["\']', source
        )
        if find_match:
            view_name = find_match.group(1)
            logger.debug(f"Using raw JSON for find query on {view_name}")

            # Check if there are complex filters or custom logic
            if _has_complex_logic(source):
                logger.debug("Complex logic detected, falling back to normal execution")
                return await fn(info, **kwargs)

            # Execute with raw JSON
            result = await db.find_raw_json(view_name, field_name, **kwargs)
            return result

    except Exception as e:
        logger.debug(f"Could not analyze function for JSON passthrough: {e}")

    # Fall back to normal execution
    return await fn(info, **kwargs)


def execute_sync_json_query(fn: Callable, info: Any, **kwargs: Any) -> Any:
    """Execute a sync query function (currently just calls the function).

    JSON passthrough is primarily for async queries, so sync queries
    execute normally.

    Args:
        fn: The resolver function
        info: GraphQL resolve info
        **kwargs: Query arguments

    Returns:
        The result of calling the function
    """
    # For sync functions, we don't use JSON passthrough
    # Just execute normally
    return fn(info, **kwargs)


def _has_complex_logic(source: str) -> bool:
    """Check if the function source has complex logic that prevents JSON passthrough.

    Args:
        source: The function source code

    Returns:
        True if complex logic is detected
    """
    # Check for patterns that indicate complex logic
    complex_patterns = [
        r"\bfor\b",  # Loops
        r"\bwhile\b",  # Loops
        r"\bif\b.*\belse\b",  # Complex conditionals
        r"\.filter\(",  # Additional filtering
        r"\.map\(",  # Transformations
        r"append\(",  # Building lists
        r"extend\(",  # Building lists
        r"\+\s*=",  # Augmented assignment
        r"try:",  # Exception handling beyond simple queries
    ]

    for pattern in complex_patterns:
        if re.search(pattern, source):
            return True

    # Check if there are multiple database calls
    db_call_count = len(re.findall(r"db\.\w+\(", source))
    if db_call_count > 1:
        return True

    return False


def create_json_passthrough_resolver(
    fn: Callable,
    field_name: str,
    return_type: Any,
    arg_name_mapping: Optional[dict[str, str]] = None,
) -> Callable:
    """Create a resolver that uses JSON passthrough when possible.

    This is an alternative to wrapping in the query builder. It provides
    more control over when JSON passthrough is used.

    Args:
        fn: The original resolver function
        field_name: The GraphQL field name
        return_type: The expected return type
        arg_name_mapping: Mapping from GraphQL to Python argument names

    Returns:
        A wrapped resolver function
    """
    import asyncio

    if asyncio.iscoroutinefunction(fn):

        async def async_json_resolver(root, info, **kwargs):
            # Map argument names if needed
            if arg_name_mapping:
                mapped_kwargs = {}
                for gql_name, value in kwargs.items():
                    python_name = arg_name_mapping.get(gql_name, gql_name)
                    mapped_kwargs[python_name] = value
                kwargs = mapped_kwargs

            # Check if JSON passthrough should be used
            if hasattr(info, "context") and should_use_json_passthrough(info.context):
                return await execute_json_query(fn, info, **kwargs)
            return await fn(info, **kwargs)

        return async_json_resolver

    def sync_json_resolver(root, info, **kwargs):
        # Map argument names if needed
        if arg_name_mapping:
            mapped_kwargs = {}
            for gql_name, value in kwargs.items():
                python_name = arg_name_mapping.get(gql_name, gql_name)
                mapped_kwargs[python_name] = value
            kwargs = mapped_kwargs

        return fn(info, **kwargs)

    return sync_json_resolver
