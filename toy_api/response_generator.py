"""

Response Generator for Toy API

Generates dummy response data for various API endpoints to enable realistic testing
of API Box route restrictions and functionality.

License: CC-BY-4.0

"""

#
# IMPORTS
#
from typing import Any, Dict

from toy_api import dummy_data_generator


#
# PUBLIC
#
def generate_response(response_type: str, params: Dict[str, str], path: str) -> Dict[str, Any]:
    """Generate dummy response data based on response type.

    All responses now use object-based generation from config/objects/*.yaml files.
    Legacy response type names (without dots) are mapped to core.* objects.

    Args:
        response_type: Type of response to generate or object reference.
        params: URL parameters extracted from the route.
        path: Route path for additional context.

    Returns:
        Dictionary containing the generated response data.
    """
    # Use hash of params for consistent generation
    row_idx = hash(str(sorted(params.items()))) % 1000 if params else 0

    # Try object-based generation (e.g., 'core.user', 'core.post', 'core.user_list')
    if '.' in response_type:
        try:
            return dummy_data_generator.generate_object(
                response_type,
                params=params,
                row_idx=row_idx
            )
        except ValueError:
            # Object not found, fall through to legacy mapping
            pass

    # Legacy response type mapping (for backward compatibility)
    # Maps old names without dots to new core.* objects
    legacy_mapping = {
        "api_info": "core.api_info",
        "user_list": "core.user_list",
        "user_detail": "core.user",
        "user_profile": "core.user_profile",
        "user_permissions": "core.user_permissions",
        "user_posts": "core.user_posts",
        "user_settings": "core.user_settings",
        "user_private": "core.user_private",
        "post_list": "core.post_list",
        "post_detail": "core.post",
        "admin_dashboard": "core.admin_dashboard",
        "admin_detail": "core.admin",
        "admin_dangerous": "core.admin_dangerous",
        "system_config": "core.system_config",
        "health_check": "core.health_check",
    }

    if response_type in legacy_mapping:
        try:
            return dummy_data_generator.generate_object(
                legacy_mapping[response_type],
                params=params,
                row_idx=row_idx
            )
        except ValueError:
            pass

    # Fallback: generate generic response
    return _generate_generic_response(response_type, params, path)


#
# INTERNAL
#
def _generate_generic_response(response_type: str, params: Dict[str, str], path: str) -> Dict[str, Any]:
    """Generate a generic response for unknown response types."""
    return {
        "message": f"Generic response for {response_type}",
        "path": path,
        "params": params,
        "data": "dummy_data",
        "timestamp": "2024-01-15T10:30:00Z"
    }