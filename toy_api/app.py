"""

Flask Application for Toy API

YAML-configurable API with dummy data for testing API Box route restrictions.

License: CC-BY-4.0

"""

#
# IMPORTS
#
from typing import Any, Dict, Optional

import yaml
from flask import Flask, jsonify

from toy_api.constants import DEFAULT_CONFIG_PATH
from toy_api.response_generator import generate_response


#
# PUBLIC
#
def create_app(config_path: Optional[str] = None) -> Flask:
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


#
# INTERNAL
#
def _load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        yaml.YAMLError: If config file is invalid YAML.
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
        # Create metadata response excluding port and other sensitive info
        metadata = {
            "name": config.get("name", "Toy API"),
            "description": config.get("description", "Configurable toy API server"),
            "routes": []
        }

        # Add route information (paths and methods only, not implementation details)
        for route_config in config.get("routes", []):
            route_info = {
                "path": route_config.get("path", "/"),
                "methods": route_config.get("methods", ["GET"])
            }
            metadata["routes"].append(route_info)

        return jsonify(metadata)

    # Register configured routes
    for route_config in config.get("routes", []):
        path = route_config["path"]
        methods = route_config.get("methods", ["GET"])
        response_type = route_config["response"]

        # Create handler function
        handler = _create_route_handler(response_type, path)

        # Register route with unique endpoint name
        endpoint_name = f"route_{path.replace('/', '_').replace('<', '').replace('>', '')}"
        app.add_url_rule(path, endpoint=endpoint_name, view_func=handler, methods=methods)


def _create_route_handler(response_type: str, path: str):
    """Create a handler function for a route.

    Args:
        response_type: Type of response to generate.
        path: Route path for context.

    Returns:
        Handler function that returns JSON response.
    """
    def handler(**kwargs):
        response_data = generate_response(response_type, kwargs, path)
        return jsonify(response_data)

    return handler