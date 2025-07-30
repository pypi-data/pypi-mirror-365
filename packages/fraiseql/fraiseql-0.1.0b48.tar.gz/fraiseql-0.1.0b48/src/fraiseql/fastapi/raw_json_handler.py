"""Raw JSON query handler for bypassing GraphQL execution.

This module detects simple queries that can be executed directly
without going through GraphQL validation and serialization.
"""

import logging
import re
from typing import Any, Optional

from graphql import GraphQLSchema, OperationDefinitionNode, parse

from fraiseql.core.ast_parser import extract_field_paths_from_info, parse_query_ast
from fraiseql.core.raw_json_executor import RawJSONResult

logger = logging.getLogger(__name__)


async def try_raw_json_execution(
    schema: GraphQLSchema,
    query: str,
    variables: dict[str, Any] | None,
    context: dict[str, Any],
) -> Optional[RawJSONResult]:
    """Try to execute a query using raw JSON passthrough.

    This function checks if a query is simple enough to bypass GraphQL
    execution and use raw JSON passthrough directly.

    Args:
        schema: The GraphQL schema
        query: The GraphQL query string
        variables: Query variables
        context: The request context

    Returns:
        RawJSONResult if the query was executed via raw JSON, None otherwise
    """
    # Only in production mode
    if context.get("mode") != "production":
        return None
    
    # Check if we have a database with raw JSON support
    db = context.get("db")
    if not db or not hasattr(db, "find_raw_json"):
        return None
    
    # Parse the query
    try:
        op, fragments = parse_query_ast(query)
    except Exception as e:
        logger.debug(f"Failed to parse query for raw JSON: {e}")
        return None
    
    # Only handle simple queries (not mutations or subscriptions)
    if op.operation != "query":
        return None
    
    # Get the selections
    selections = op.selection_set.selections
    if len(selections) != 1:
        # Multiple root fields - not simple
        return None
    
    # Get the single field
    field = selections[0]
    if field.kind != "field":
        return None
    
    field_name = field.name.value
    
    # Check if this field exists in the schema
    query_type = schema.type_map.get("Query")
    if not query_type or field_name not in query_type.fields:
        return None
    
    # Get the field definition
    field_def = query_type.fields[field_name]
    
    # Check if the resolver is simple (this is a heuristic)
    resolver = field_def.resolve
    if not resolver:
        return None
    
    # Try to get the original function (before wrapping)
    original_fn = resolver
    while hasattr(original_fn, "__wrapped__"):
        original_fn = original_fn.__wrapped__
    
    # Check if it's a simple db query
    if not _is_simple_db_query(original_fn):
        return None
    
    # Extract the view name from the function
    view_name = _extract_view_name(original_fn)
    if not view_name:
        return None
    
    # Build the arguments
    args = {}
    if field.arguments:
        for arg in field.arguments:
            arg_name = arg.name.value
            arg_value = arg.value
            
            # Handle variable references
            if hasattr(arg_value, "kind") and arg_value.kind == "variable":
                var_name = arg_value.name.value
                if variables and var_name in variables:
                    args[arg_name] = variables[var_name]
            else:
                # Handle literal values
                args[arg_name] = _get_literal_value(arg_value)
    
    # Create a mock info object for field path extraction
    class MockInfo:
        def __init__(self, field_nodes, fragments):
            self.field_nodes = field_nodes
            self.fragments = fragments
    
    mock_info = MockInfo([field], fragments)
    
    # Extract field paths
    from fraiseql.utils.casing import to_snake_case
    field_paths = extract_field_paths_from_info(mock_info, transform_path=to_snake_case)
    
    # Store field name in db context
    db.context["graphql_field_name"] = field_name
    
    # Determine if it's find or find_one
    is_find_one = "find_one" in str(original_fn.__code__.co_names)
    
    try:
        if is_find_one:
            # Execute find_one
            result = await db.find_one_raw_json(view_name, field_name, mock_info, **args)
        else:
            # Execute find
            result = await db.find_raw_json(view_name, field_name, mock_info, **args)
        
        logger.debug(f"Successfully executed query '{field_name}' via raw JSON")
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute raw JSON query: {e}")
        return None


def _is_simple_db_query(fn) -> bool:
    """Check if a function is a simple database query."""
    try:
        import inspect
        source = inspect.getsource(fn)
        
        # Check for simple patterns
        if "db.find_one(" in source or "db.find(" in source:
            # Check for complex patterns
            if any(pattern in source for pattern in [
                "for ", "if ", "filter(", "map(", "lambda", "await (?!db.find)"
            ]):
                return False
            return True
    except:
        pass
    
    return False


def _extract_view_name(fn) -> Optional[str]:
    """Extract the view name from a resolver function."""
    try:
        import inspect
        source = inspect.getsource(fn)
        
        # Look for db.find or db.find_one calls
        match = re.search(r'db\.find(?:_one)?\s*\(\s*["\']([^"\']+)["\']', source)
        if match:
            return match.group(1)
    except:
        pass
    
    return None


def _get_literal_value(value_node) -> Any:
    """Extract literal value from GraphQL AST node."""
    if hasattr(value_node, "value"):
        return value_node.value
    # Handle other types as needed
    return None