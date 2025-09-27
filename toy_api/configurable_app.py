"""

Configurable Flask Application for Toy API v2

YAML-configurable API with dummy data for testing API Box route restrictions.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import os
import random
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from flask import Flask, jsonify, request


#
# CONSTANTS
#
DEFAULT_CONFIG_PATH: str = "configs/default.yaml"

# Dummy data generators
FIRST_NAMES: List[str] = [
    "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Helen",
    "Ian", "Julia", "Kevin", "Luna", "Mark", "Nina", "Oscar", "Paula"
]

LAST_NAMES: List[str] = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Foster", "Garcia", "Harris",
    "Jackson", "Kim", "Lopez", "Miller", "Nelson", "O'Connor", "Parker", "Quinn"
]

POST_TITLES: List[str] = [
    "Introduction to APIs", "Building Scalable Systems", "Database Design Patterns",
    "Security Best Practices", "Testing Strategies", "DevOps Fundamentals",
    "Code Review Guidelines", "Performance Optimization", "Documentation Standards"
]

DEFAULT_RESPONSES: Dict[str, Any] = {
    "users": {"type": "list", "generator": "user_list"},
    "users/{}": {"type": "object", "generator": "user_detail"},
    "users/{}/profile": {"type": "object", "generator": "user_profile"},
    "users/{}/permissions": {"type": "list", "generator": "user_permissions"},
    "users/{}/posts": {"type": "list", "generator": "user_posts"},
    "users/{}/settings": {"type": "object", "generator": "user_settings"},
    "users/{}/private": {"type": "object", "generator": "user_private"},
    "posts": {"type": "list", "generator": "post_list"},
    "posts/{}": {"type": "object", "generator": "post_detail"},
    "admin": {"type": "object", "generator": "admin_dashboard"},
    "admin/{}": {"type": "object", "generator": "admin_detail"},
    "admin/dashboard": {"type": "object", "generator": "admin_dashboard"},
    "admin/{}/dangerous": {"type": "object", "generator": "admin_dangerous"},
    "system/{}/config": {"type": "object", "generator": "system_config"},
    "health": {"type": "object", "generator": "health_check"},
}


#
# PUBLIC
#
def create_configurable_app(config_path: Optional[str] = None) -> Flask:
    """Create a Flask app configured from YAML file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)

    # Load configuration
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    try:
        config = _load_config(config_path)
    except FileNotFoundError:
        # Use default configuration if file not found
        config = _get_default_config()

    # Register routes from config
    _register_routes(app, config)

    return app


def _load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Configuration dictionary.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file) or {}


def _get_default_config() -> Dict[str, Any]:
    """Get default configuration with basic routes.

    Returns:
        Default configuration dictionary.
    """
    return {
        "name": "default-toy-api",
        "description": "Default toy API with basic routes",
        "port": 8000,
        "routes": [
            {"path": "/", "methods": ["GET"], "response": "api_info"},
            {"path": "/users", "methods": ["GET"], "response": "user_list"},
            {"path": "/users/<user_id>", "methods": ["GET"], "response": "user_detail"},
            {"path": "/health", "methods": ["GET"], "response": "health_check"},
        ]
    }


def _register_routes(app: Flask, config: Dict[str, Any]) -> None:
    """Register routes from configuration.

    Args:
        app: Flask application instance.
        config: Configuration dictionary.
    """
    # Register API info endpoint
    @app.route("/")
    def api_info():
        return jsonify({
            "name": config.get("name", "toy-api"),
            "description": config.get("description", "Configurable toy API"),
            "version": "2.0",
            "routes": [route["path"] for route in config.get("routes", [])]
        })

    # Register configured routes
    for route_config in config.get("routes", []):
        path = route_config["path"]
        methods = route_config.get("methods", ["GET"])
        response_type = route_config["response"]

        # Create handler function
        handler = _create_route_handler(response_type, path)

        # Register route
        app.add_url_rule(path, endpoint=f"route_{path.replace('/', '_').replace('<', '').replace('>', '')}",
                        view_func=handler, methods=methods)


def _create_route_handler(response_type: str, path: str):
    """Create a handler function for a route.

    Args:
        response_type: Type of response to generate.
        path: Route path for context.

    Returns:
        Handler function.
    """
    def handler(**kwargs):
        return jsonify(_generate_response(response_type, kwargs, path))

    return handler


def _generate_response(response_type: str, params: Dict[str, str], path: str) -> Dict[str, Any]:
    """Generate dummy response data.

    Args:
        response_type: Type of response to generate.
        params: URL parameters.
        path: Route path for context.

    Returns:
        Response data.
    """
    if response_type == "api_info":
        return {"message": "Configurable Toy API v2", "status": "running"}

    elif response_type == "user_list":
        return {
            "users": [_generate_user(i) for i in range(1, 6)],
            "total": 5,
            "page": 1
        }

    elif response_type == "user_detail":
        user_id = params.get("user_id", "1")
        return _generate_user(user_id)

    elif response_type == "user_profile":
        user_id = params.get("user_id", "1")
        user = _generate_user(user_id)
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "bio": f"Software engineer with {random.randint(1, 10)} years of experience",
            "location": random.choice(["San Francisco", "New York", "London", "Tokyo", "Berlin"]),
            "joined": "2020-01-15"
        }

    elif response_type == "user_permissions":
        return {
            "user_id": params.get("user_id", "1"),
            "permissions": random.sample(["read", "write", "delete", "admin", "create"], k=3)
        }

    elif response_type == "user_posts":
        user_id = params.get("user_id", "1")
        return {
            "user_id": user_id,
            "posts": [_generate_post(i) for i in range(1, 4)]
        }

    elif response_type == "user_settings":
        return {
            "user_id": params.get("user_id", "1"),
            "theme": random.choice(["light", "dark"]),
            "notifications": random.choice([True, False]),
            "language": random.choice(["en", "es", "fr", "de"])
        }

    elif response_type == "user_private":
        return {
            "user_id": params.get("user_id", "1"),
            "ssn": "***-**-****",
            "bank_account": "****1234",
            "private_key": "REDACTED"
        }

    elif response_type == "post_list":
        return {
            "posts": [_generate_post(i) for i in range(1, 11)],
            "total": 10
        }

    elif response_type == "post_detail":
        post_id = params.get("post_id", "1")
        return _generate_post(post_id)

    elif response_type == "admin_dashboard":
        return {
            "stats": {
                "total_users": random.randint(100, 1000),
                "active_sessions": random.randint(10, 100),
                "server_load": f"{random.randint(10, 90)}%"
            },
            "recent_activity": ["User login", "Data backup", "System update"]
        }

    elif response_type == "admin_detail":
        admin_id = params.get("admin_id", "1")
        return {
            "admin_id": admin_id,
            "name": f"Admin {admin_id}",
            "role": "administrator",
            "last_login": "2024-01-15T10:30:00Z"
        }

    elif response_type == "admin_dangerous":
        return {
            "operation": "dangerous_admin_operation",
            "warning": "This endpoint should be restricted!",
            "admin_id": params.get("admin_id", "1"),
            "status": "executed"
        }

    elif response_type == "system_config":
        system_id = params.get("system_id", "prod")
        return {
            "system_id": system_id,
            "config": {
                "database_url": "REDACTED",
                "api_keys": "REDACTED",
                "debug_mode": False
            },
            "warning": "Sensitive system configuration"
        }

    elif response_type == "health_check":
        return {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "version": "2.0",
            "uptime": f"{random.randint(1, 100)} hours"
        }

    else:
        return {
            "message": f"Response for {response_type}",
            "path": path,
            "params": params,
            "data": "dummy_data"
        }


#
# INTERNAL
#
def _generate_user(user_id: Any) -> Dict[str, Any]:
    """Generate dummy user data.

    Args:
        user_id: User ID.

    Returns:
        User data dictionary.
    """
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    return {
        "id": str(user_id),
        "name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
        "username": f"{first_name.lower()}{user_id}",
        "active": random.choice([True, False])
    }


def _generate_post(post_id: Any) -> Dict[str, Any]:
    """Generate dummy post data.

    Args:
        post_id: Post ID.

    Returns:
        Post data dictionary.
    """
    return {
        "id": str(post_id),
        "title": random.choice(POST_TITLES),
        "author": f"user_{random.randint(1, 10)}",
        "content": f"This is the content of post {post_id}. It contains valuable information.",
        "tags": random.sample(["tech", "api", "tutorial", "guide", "tips"], k=2),
        "published": random.choice([True, False])
    }