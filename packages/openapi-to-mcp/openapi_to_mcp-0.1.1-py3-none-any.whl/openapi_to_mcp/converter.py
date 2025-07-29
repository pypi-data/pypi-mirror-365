"""
This module handles the conversion of a parsed OpenAPI specification into an
MCP-compliant format.
"""

from typing import Callable, Optional, Dict, Any
from .resolver import resolve_ref

def _resolve_schema(spec: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively resolves $ref pointers in a schema object.
    """
    if isinstance(schema, dict) and "$ref" in schema:
        # Resolve the reference and recursively call on the result
        return _resolve_schema(spec, resolve_ref(spec, schema["$ref"]))
    
    if isinstance(schema, dict) and "properties" in schema:
        # Resolve refs in properties
        schema["properties"] = {
            k: _resolve_schema(spec, v) for k, v in schema["properties"].items()
        }

    if isinstance(schema, dict) and "items" in schema:
        # Resolve refs in array items
        schema["items"] = _resolve_schema(spec, schema["items"])
        
    return schema

def convert_to_mcp(
    parsed_spec: dict,
    api_base_url: str,
    auth_header: Optional[str] = None,
    path_filter: Optional[Callable[[str, str], bool]] = None
) -> dict:
    """
    Converts a parsed OpenAPI specification into an MCP-compliant dictionary.
    """
    mcp_tools = []
    for path, path_item in parsed_spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch", "head", "options"]:
                continue

            if path_filter and not path_filter(path, method):
                continue

            tool_spec = {
                "function": {
                    "name": operation.get("operationId", f"{method.upper()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"),
                    "description": operation.get("summary", operation.get("description", "No description available.")),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                "url": f"{api_base_url.rstrip('/')}{path}",
                "method": method.upper(),
                "auth": {}
            }

            if auth_header:
                header_name, *value_prefix = auth_header.split(':', 1)
                tool_spec["auth"] = {
                    "type": "apiKey",
                    "in": "header",
                    "name": header_name,
                    "valuePrefix": f"{value_prefix[0]} " if value_prefix else ""
                }

            # Add parameters
            if "parameters" in operation:
                for param in operation["parameters"]:
                    param_name = param.get("in")
                    param_schema = _resolve_schema(parsed_spec, param.get("schema", {}))

                    if param_name == "query":
                        tool_spec["function"]["parameters"]["properties"][param["name"]] = {
                            "type": param_schema.get("type", "string"),
                            "description": param.get("description", ""),
                        }
                        if param.get("required"):
                            tool_spec["function"]["parameters"]["required"].append(param["name"])
                    elif param_name == "path":
                        tool_spec["function"]["parameters"]["properties"][param["name"]] = {
                            "type": param_schema.get("type", "string"),
                            "description": f"(in path) {param.get('description', '')}",
                        }
                        if param.get("required"):
                            tool_spec["function"]["parameters"]["required"].append(param["name"])
            
            if "requestBody" in operation:
                content = operation["requestBody"].get("content", {})
                if "application/json" in content:
                    json_schema = content["application/json"].get("schema", {})
                    resolved_schema = _resolve_schema(parsed_spec, json_schema)

                    # Filter out read-only properties from the schema
                    if 'properties' in resolved_schema:
                        for prop_name, prop_details in list(resolved_schema['properties'].items()):
                            if isinstance(prop_details, dict) and prop_details.get('readOnly'):
                                del resolved_schema['properties'][prop_name]

                    tool_spec["function"]["parameters"]["properties"]["requestBody"] = {
                        "type": "object",
                        "description": operation["requestBody"].get("description") or "JSON request body",
                        "properties": resolved_schema.get("properties", {})
                    }
                    
                    # If the entire request body is required, add it to the list
                    if operation["requestBody"].get("required"):
                        tool_spec["function"]["parameters"]["required"].append("requestBody")


            mcp_tools.append(tool_spec)

    return {"tools": mcp_tools}
