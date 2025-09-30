"""

Response Generator for Toy API

Generates dummy response data for various API endpoints to enable realistic testing
of API Box route restrictions and functionality.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import random
from typing import Any, Dict

from toy_api.constants import (
    FIRST_NAMES,
    LAST_NAMES,
    POST_TITLES,
    LOCATIONS,
    PERMISSIONS,
    THEMES,
    LANGUAGES,
    POST_TAGS,
    ADMIN_ACTIVITIES,
    JOBS
)


#
# PUBLIC
#
def generate_response(response_type: str, params: Dict[str, str], path: str) -> Dict[str, Any]:
    """Generate dummy response data based on response type.

    Args:
        response_type: Type of response to generate.
        params: URL parameters extracted from the route.
        path: Route path for additional context.

    Returns:
        Dictionary containing the generated response data.
    """
    if response_type == "api_info":
        return _generate_api_info()

    elif response_type == "user_list":
        return _generate_user_list()

    elif response_type == "user_detail":
        user_id = params.get("user_id", "1")
        return generate_user(user_id)

    elif response_type == "user_profile":
        user_id = params.get("user_id", "1")
        return _generate_user_profile(user_id)

    elif response_type == "user_permissions":
        user_id = params.get("user_id", "1")
        return _generate_user_permissions(user_id)

    elif response_type == "user_posts":
        user_id = params.get("user_id", "1")
        return _generate_user_posts(user_id)

    elif response_type == "user_settings":
        user_id = params.get("user_id", "1")
        return _generate_user_settings(user_id)

    elif response_type == "user_private":
        user_id = params.get("user_id", "1")
        return _generate_user_private(user_id)

    elif response_type == "post_list":
        return _generate_post_list()

    elif response_type == "post_detail":
        post_id = params.get("post_id", "1")
        return generate_post(post_id)

    elif response_type == "admin_dashboard":
        return _generate_admin_dashboard()

    elif response_type == "admin_detail":
        admin_id = params.get("admin_id", "1")
        return _generate_admin_detail(admin_id)

    elif response_type == "admin_dangerous":
        admin_id = params.get("admin_id", "1")
        return _generate_admin_dangerous(admin_id)

    elif response_type == "system_config":
        system_id = params.get("system_id", "prod")
        return _generate_system_config(system_id)

    elif response_type == "health_check":
        return _generate_health_check()

    else:
        return _generate_generic_response(response_type, params, path)


def generate_user(user_id: Any) -> Dict[str, Any]:
    """Generate dummy user data.

    Args:
        user_id: User identifier.

    Returns:
        Dictionary containing user data.
    """
    # Use user_id as seed for consistent data per user
    random.seed(hash(str(user_id)) % 1000)

    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    user_data = {
        "id": str(user_id),
        "name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
        "username": f"{first_name.lower()}{user_id}",
        "active": random.choice([True, False])
    }

    # Reset random seed
    random.seed()
    return user_data


def generate_post(post_id: Any) -> Dict[str, Any]:
    """Generate dummy post data.

    Args:
        post_id: Post identifier.

    Returns:
        Dictionary containing post data.
    """
    # Use post_id as seed for consistent data per post
    random.seed(hash(str(post_id)) % 1000)

    post_data = {
        "id": str(post_id),
        "title": random.choice(POST_TITLES),
        "author": f"user_{random.randint(1, 10)}",
        "content": f"This is the content of post {post_id}. It contains valuable information about the topic.",
        "tags": random.sample(POST_TAGS, k=min(3, len(POST_TAGS))),
        "published": random.choice([True, False])
    }

    # Reset random seed
    random.seed()
    return post_data


#
# INTERNAL
#
def _generate_api_info() -> Dict[str, Any]:
    """Generate API information response."""
    return {
        "message": "Toy API - YAML Configurable",
        "status": "running",
        "version": "2.0"
    }


def _generate_user_list() -> Dict[str, Any]:
    """Generate list of users."""
    return {
        "users": [generate_user(i) for i in range(1, 6)],
        "total": 5,
        "page": 1,
        "per_page": 10
    }


def _generate_user_profile(user_id: str) -> Dict[str, Any]:
    """Generate user profile data."""
    user = generate_user(user_id)

    # Use user_id for consistent profile data
    random.seed(hash(str(user_id)) % 1000)

    profile = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "bio": f"{random.choice(JOBS)} with {random.randint(1, 10)} years of experience",
        "location": random.choice(LOCATIONS),
        "joined": "2020-01-15",
        "followers": random.randint(10, 1000),
        "following": random.randint(5, 500)
    }

    # Reset random seed
    random.seed()
    return profile


def _generate_user_permissions(user_id: str) -> Dict[str, Any]:
    """Generate user permissions data."""
    random.seed(hash(str(user_id)) % 1000)

    permissions_data = {
        "user_id": user_id,
        "permissions": random.sample(PERMISSIONS, k=min(4, len(PERMISSIONS))),
        "role": random.choice(["user", "moderator", "admin"]),
        "last_updated": "2024-01-15T10:30:00Z"
    }

    random.seed()
    return permissions_data


def _generate_user_posts(user_id: str) -> Dict[str, Any]:
    """Generate user posts data."""
    return {
        "user_id": user_id,
        "posts": [generate_post(f"{user_id}-{i}") for i in range(1, 4)],
        "total": 3
    }


def _generate_user_settings(user_id: str) -> Dict[str, Any]:
    """Generate user settings data."""
    random.seed(hash(str(user_id)) % 1000)

    settings = {
        "user_id": user_id,
        "theme": random.choice(THEMES),
        "notifications": random.choice([True, False]),
        "language": random.choice(LANGUAGES),
        "privacy": {
            "profile_public": random.choice([True, False]),
            "show_email": random.choice([True, False])
        }
    }

    random.seed()
    return settings


def _generate_user_private(user_id: str) -> Dict[str, Any]:
    """Generate user private data (sensitive information)."""
    return {
        "user_id": user_id,
        "ssn": "***-**-****",
        "bank_account": "****1234",
        "private_key": "REDACTED",
        "api_tokens": ["token_***", "key_***"],
        "warning": "This endpoint contains sensitive data and should be restricted!"
    }


def _generate_post_list() -> Dict[str, Any]:
    """Generate list of posts."""
    return {
        "posts": [generate_post(i) for i in range(1, 11)],
        "total": 10,
        "page": 1,
        "per_page": 10
    }


def _generate_admin_dashboard() -> Dict[str, Any]:
    """Generate admin dashboard data."""
    return {
        "stats": {
            "total_users": random.randint(100, 1000),
            "active_sessions": random.randint(10, 100),
            "server_load": f"{random.randint(10, 90)}%",
            "disk_usage": f"{random.randint(30, 85)}%"
        },
        "recent_activity": random.sample(ADMIN_ACTIVITIES, k=min(5, len(ADMIN_ACTIVITIES))),
        "alerts": random.randint(0, 3)
    }


def _generate_admin_detail(admin_id: str) -> Dict[str, Any]:
    """Generate admin user detail data."""
    random.seed(hash(str(admin_id)) % 1000)

    admin_data = {
        "admin_id": admin_id,
        "name": f"Admin {admin_id}",
        "role": random.choice(["administrator", "super_admin", "moderator"]),
        "permissions": random.sample(PERMISSIONS, k=len(PERMISSIONS)),
        "last_login": "2024-01-15T10:30:00Z",
        "login_count": random.randint(100, 1000)
    }

    random.seed()
    return admin_data


def _generate_admin_dangerous(admin_id: str) -> Dict[str, Any]:
    """Generate dangerous admin operation response."""
    return {
        "operation": "dangerous_admin_operation",
        "warning": "This endpoint performs dangerous operations and should be restricted!",
        "admin_id": admin_id,
        "action": "system_reset",
        "status": "executed",
        "timestamp": "2024-01-15T10:30:00Z",
        "confirmation_required": True
    }


def _generate_system_config(system_id: str) -> Dict[str, Any]:
    """Generate system configuration data."""
    return {
        "system_id": system_id,
        "environment": system_id,
        "config": {
            "database_url": "REDACTED",
            "api_keys": "REDACTED",
            "secret_tokens": "REDACTED",
            "debug_mode": system_id != "prod"
        },
        "warning": "Sensitive system configuration - access should be restricted!",
        "last_updated": "2024-01-15T10:30:00Z"
    }


def _generate_health_check() -> Dict[str, Any]:
    """Generate health check response."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "2.0",
        "uptime": f"{random.randint(1, 100)} hours",
        "dependencies": {
            "database": "healthy",
            "cache": "healthy",
            "storage": "healthy"
        }
    }


def _generate_generic_response(response_type: str, params: Dict[str, str], path: str) -> Dict[str, Any]:
    """Generate a generic response for unknown response types."""
    return {
        "message": f"Generic response for {response_type}",
        "path": path,
        "params": params,
        "data": "dummy_data",
        "timestamp": "2024-01-15T10:30:00Z"
    }