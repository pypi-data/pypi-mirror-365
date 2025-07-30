"""Raw JSON resolver wrapper for simple query optimization.

This module provides a wrapper that automatically switches simple database queries
to use raw JSON passthrough in production mode, bypassing Python object creation
and GraphQL validation for maximum performance.
"""

import asyncio
import functools
import inspect
import logging
import re
from typing import Any, Callable

from fraiseql.core.raw_json_executor import RawJSONResult

logger = logging.getLogger(__name__)


def create_raw_json_resolver(
    fn: Callable,
    field_name: str,
    arg_name_mapping: dict[str, str] | None = None,
) -> Callable:
    """Create a resolver that uses raw JSON for simple queries in production mode.

    This wrapper detects simple query patterns (db.find/find_one) and automatically
    switches to raw JSON methods in production mode for maximum performance.

    Args:
        fn: The original resolver function
        field_name: The GraphQL field name
        arg_name_mapping: Mapping from GraphQL to Python argument names

    Returns:
        A wrapped resolver function
    """
    # Get the source code to analyze the resolver
    try:
        source = inspect.getsource(fn)
    except OSError:
        # Can't get source, return original function
        logger.debug(f"Cannot get source for {fn.__name__}, skipping raw JSON optimization")
        return fn

    # Check if this is a simple query
    is_simple = _is_simple_query(source)
    
    if not is_simple:
        logger.debug(f"Query {field_name} is not simple, using normal execution")
        return fn

    logger.debug(f"Query {field_name} is simple, enabling raw JSON optimization")

    if asyncio.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(root: Any, info: Any, **kwargs: Any) -> Any:
            # Store GraphQL info and field name in context for repository
            if hasattr(info, "context"):
                info.context["graphql_info"] = info
                info.context["graphql_field_name"] = info.field_name
                
                # Also update the repository's context if it exists
                if "db" in info.context and hasattr(info.context["db"], "context"):
                    info.context["db"].context["graphql_info"] = info
                    info.context["db"].context["graphql_field_name"] = info.field_name
            
            # Check if we should use raw JSON
            context = getattr(info, "context", {})
            mode = context.get("mode", "development")
            
            if mode != "production":
                # Development mode - use normal execution
                return await _execute_with_mapping(fn, info, kwargs, arg_name_mapping)
            
            # Production mode - try to use raw JSON
            db = context.get("db")
            if not db or not hasattr(db, "find_raw_json"):
                # No raw JSON support, fall back to normal
                return await _execute_with_mapping(fn, info, kwargs, arg_name_mapping)
            
            # Store field name in db context for proper JSON wrapping
            db.context["graphql_field_name"] = field_name
            
            # Intercept the db calls
            result = await _execute_with_raw_json(fn, info, kwargs, arg_name_mapping)
            
            # If we got a RawJSONResult, return it directly
            if isinstance(result, RawJSONResult):
                return result
            
            # Otherwise fall back to normal result
            return result

        return async_wrapper
    else:
        @functools.wraps(fn)
        def sync_wrapper(root: Any, info: Any, **kwargs: Any) -> Any:
            # Sync resolvers don't support raw JSON optimization
            return _execute_with_mapping_sync(fn, info, kwargs, arg_name_mapping)

        return sync_wrapper


def _is_simple_query(source: str) -> bool:
    """Check if a query is simple (just calls db.find or db.find_one).

    Args:
        source: The source code of the resolver

    Returns:
        True if the query is simple
    """
    # Remove comments and normalize whitespace
    lines = []
    for line in source.split('\n'):
        # Remove comments
        if '#' in line:
            line = line[:line.index('#')]
        line = line.strip()
        if line:
            lines.append(line)
    
    cleaned = ' '.join(lines)
    
    # Check for patterns that make it complex
    complex_patterns = [
        r'for\s+\w+\s+in',  # Loops
        r'if\s+',  # Conditionals (beyond simple None checks)
        r'await\s+(?!db\.find)',  # Other async calls
        r'\.append\(',  # List building
        r'\.extend\(',  # List extending
        r'\+',  # String/list concatenation
        r'filter\(',  # Filtering
        r'map\(',  # Mapping
        r'lambda',  # Lambda functions
        r'def\s+',  # Nested functions
    ]
    
    for pattern in complex_patterns:
        if re.search(pattern, cleaned):
            return False
    
    # Check if it has db.find or db.find_one
    has_find = bool(re.search(r'db\.find(?:_one)?\s*\(', cleaned))
    
    # Check if the result is directly returned
    has_direct_return = bool(re.search(r'return\s+(?:await\s+)?(?:db\.find|result|data|row)', cleaned))
    
    return has_find and has_direct_return


async def _execute_with_mapping(
    fn: Callable,
    info: Any,
    kwargs: dict[str, Any],
    arg_name_mapping: dict[str, str] | None,
) -> Any:
    """Execute resolver with argument mapping."""
    if arg_name_mapping:
        mapped_kwargs = {}
        for gql_name, value in kwargs.items():
            python_name = arg_name_mapping.get(gql_name, gql_name)
            mapped_kwargs[python_name] = value
        kwargs = mapped_kwargs
    
    return await fn(info, **kwargs)


def _execute_with_mapping_sync(
    fn: Callable,
    info: Any,
    kwargs: dict[str, Any],
    arg_name_mapping: dict[str, str] | None,
) -> Any:
    """Execute sync resolver with argument mapping."""
    if arg_name_mapping:
        mapped_kwargs = {}
        for gql_name, value in kwargs.items():
            python_name = arg_name_mapping.get(gql_name, gql_name)
            mapped_kwargs[python_name] = value
        kwargs = mapped_kwargs
    
    return fn(info, **kwargs)


async def _execute_with_raw_json(
    fn: Callable,
    info: Any,
    kwargs: dict[str, Any],
    arg_name_mapping: dict[str, str] | None,
) -> Any:
    """Execute resolver with raw JSON db methods.

    This function temporarily replaces the db.find and db.find_one methods
    with their raw JSON equivalents during resolver execution.
    """
    # Map arguments
    if arg_name_mapping:
        mapped_kwargs = {}
        for gql_name, value in kwargs.items():
            python_name = arg_name_mapping.get(gql_name, gql_name)
            mapped_kwargs[python_name] = value
        kwargs = mapped_kwargs
    
    # Get the database
    db = info.context.get("db")
    if not db:
        return await fn(info, **kwargs)
    
    # Store original methods
    orig_find = db.find
    orig_find_one = db.find_one
    
    # Get field name from db context
    field_name = db.context.get("graphql_field_name")
    
    # Replace with raw JSON methods
    async def find_raw_wrapper(view_name: str, **find_kwargs: Any) -> RawJSONResult:
        return await db.find_raw_json(view_name, field_name, info, **find_kwargs)
    
    async def find_one_raw_wrapper(view_name: str, **find_kwargs: Any) -> RawJSONResult:
        return await db.find_one_raw_json(view_name, field_name, info, **find_kwargs)
    
    try:
        # Temporarily replace methods
        db.find = find_raw_wrapper
        db.find_one = find_one_raw_wrapper
        
        # Execute resolver
        result = await fn(info, **kwargs)
        
        return result
    finally:
        # Restore original methods
        db.find = orig_find
        db.find_one = orig_find_one