"""JSON-aware query executor for optimized GraphQL query execution.

This module provides functions to execute GraphQL queries with JSON passthrough
optimization, avoiding unnecessary object instantiation.
"""

import inspect
import logging
from typing import Any, Callable, Optional, Type, Union, get_args, get_origin

from fraiseql.core.json_passthrough import JSONPassthrough, wrap_in_passthrough

logger = logging.getLogger(__name__)


def get_list_item_type(type_hint: Type) -> Optional[Type]:
    """Extract the item type from a List type hint.
    
    Args:
        type_hint: The type hint to analyze (e.g., List[User])
        
    Returns:
        The item type if it's a List, None otherwise
    """
    origin = get_origin(type_hint)
    if origin in (list, List):
        args = get_args(type_hint)
        return args[0] if args else None
    return None


def get_optional_type(type_hint: Type) -> Optional[Type]:
    """Extract the actual type from an Optional type hint.
    
    Args:
        type_hint: The type hint to analyze (e.g., Optional[User])
        
    Returns:
        The non-None type if it's Optional, otherwise the original type
    """
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        # Filter out None to get the actual type
        non_none_types = [t for t in args if t is not type(None)]
        if len(non_none_types) == 1:
            return non_none_types[0]
    return type_hint


async def execute_json_query(fn: Callable, info: Any, **kwargs) -> Any:
    """Execute a query function with JSON passthrough optimization.
    
    This function wraps query execution to automatically convert dict results
    into JSONPassthrough objects, providing efficient field access without
    full object instantiation.
    
    Args:
        fn: The query function to execute
        info: GraphQL resolve info
        **kwargs: Query arguments
        
    Returns:
        The query result, potentially wrapped in JSONPassthrough
    """
    # Execute the original query function
    result = await fn(info, **kwargs)
    
    # If result is None or already a non-dict type, return as-is
    if result is None or not isinstance(result, (dict, list)):
        return result
    
    # Get the return type annotation for type hints
    sig = inspect.signature(fn)
    return_type = sig.return_annotation
    
    # Handle Optional types
    actual_return_type = get_optional_type(return_type)
    
    # Wrap the result appropriately
    if isinstance(result, dict):
        # Single object result
        type_name = "Query"  # Default type name
        
        # Try to get type name from annotation
        if hasattr(actual_return_type, "__name__"):
            type_name = actual_return_type.__name__
        elif hasattr(actual_return_type, "__gql_typename__"):
            type_name = actual_return_type.__gql_typename__
        
        # Override with __typename from data if present
        if "__typename" in result:
            type_name = result["__typename"]
        
        logger.debug(f"Wrapping dict result as JSONPassthrough({type_name})")
        return JSONPassthrough(result, type_name, actual_return_type)
    
    elif isinstance(result, list) and result and isinstance(result[0], dict):
        # List of objects result
        item_type = get_list_item_type(actual_return_type)
        
        if item_type:
            type_name = getattr(item_type, "__name__", "Item")
            logger.debug(f"Wrapping list of {len(result)} items as JSONPassthrough({type_name})")
            return [
                JSONPassthrough(
                    item,
                    item.get("__typename", type_name),
                    item_type
                )
                for item in result
            ]
        else:
            # No type hint available, use generic wrapping
            logger.debug(f"Wrapping list of {len(result)} items with generic JSONPassthrough")
            return [
                JSONPassthrough(item, item.get("__typename", "Item"))
                for item in result
            ]
    
    return result


def execute_sync_json_query(fn: Callable, info: Any, **kwargs) -> Any:
    """Execute a synchronous query function with JSON passthrough optimization.
    
    This is the synchronous version of execute_json_query for non-async resolvers.
    
    Args:
        fn: The query function to execute
        info: GraphQL resolve info
        **kwargs: Query arguments
        
    Returns:
        The query result, potentially wrapped in JSONPassthrough
    """
    # Execute the original query function
    result = fn(info, **kwargs)
    
    # If result is None or already a non-dict type, return as-is
    if result is None or not isinstance(result, (dict, list)):
        return result
    
    # Get the return type annotation for type hints
    sig = inspect.signature(fn)
    return_type = sig.return_annotation
    
    # Handle Optional types
    actual_return_type = get_optional_type(return_type)
    
    # Use the same wrapping logic as the async version
    return wrap_in_passthrough(result, actual_return_type)


def should_use_json_passthrough(context: dict) -> bool:
    """Determine if JSON passthrough should be used based on context.
    
    Args:
        context: The GraphQL context dictionary
        
    Returns:
        True if JSON passthrough should be used
    """
    # Check explicit flag in context
    if "json_passthrough" in context:
        return bool(context["json_passthrough"])
    
    # Check mode - use passthrough in production by default
    mode = context.get("mode", "production")
    return mode == "production"


# Import List for type hints
from typing import List