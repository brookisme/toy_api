"""

Flask Application for Toy API

Simple API with user management endpoints for testing API Box.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import random
import uuid
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request


#
# CONSTANTS
#
DEFAULT_PERMISSIONS: List[str] = ["read", "write", "execute"]
FIRST_NAMES: List[str] = [
    "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Helen",
    "Ian", "Julia", "Kevin", "Luna", "Mark", "Nina", "Oscar", "Paula"
]
LAST_NAMES: List[str] = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Foster", "Garcia", "Harris",
    "Jackson", "Kim", "Lopez", "Miller", "Nelson", "Parker", "Quinn", "Rodriguez"
]


#
# PUBLIC
#
def create_app(port: int = 8000, nb_users: int = 5) -> Flask:
    """Create and configure the Flask application.

    Args:
        port: Port number to include in usernames.
        nb_users: Number of users to create.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)

    # Initialize users data
    users_data = _generate_users(port, nb_users)
    app.config['USERS_DATA'] = users_data

    # Add routes
    _add_routes(app)

    return app


#
# INTERNAL
#
def _generate_users(port: int, nb_users: int) -> Dict[str, Dict[str, Any]]:
    """Generate random users data.

    Args:
        port: Port number to include in usernames.
        nb_users: Number of users to generate.

    Returns:
        Dictionary mapping user_id to user data.
    """
    users = {}

    for _ in range(nb_users):
        user_id = str(uuid.uuid4())
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}--{port}"

        users[user_id] = {
            "user_id": user_id,
            "name": name,
            "permissions": DEFAULT_PERMISSIONS.copy()
        }

    return users


def _add_routes(app: Flask) -> None:
    """Add API routes to the Flask app.

    Args:
        app: Flask application instance.
    """

    @app.route("/users", methods=["GET"])
    @app.route("/users/", methods=["GET"])
    def list_users() -> List[str]:
        """List all user IDs."""
        users_data = app.config['USERS_DATA']
        return list(users_data.keys())

    @app.route("/users/<user_id>", methods=["GET"])
    def get_user(user_id: str) -> Dict[str, Any]:
        """Get user data by ID."""
        users_data = app.config['USERS_DATA']

        if user_id not in users_data:
            return {"error": f"User {user_id} not found"}, 404

        return users_data[user_id]

    @app.route("/users/<user_id>", methods=["POST"])
    def create_user(user_id: str) -> Dict[str, Any]:
        """Create or update user from posted data."""
        users_data = app.config['USERS_DATA']

        try:
            user_data = request.get_json()
            if not user_data:
                return {"error": "No JSON data provided"}, 400

            # Validate required fields
            if "name" not in user_data:
                return {"error": "Name is required"}, 400

            # Set defaults
            new_user = {
                "user_id": user_id,
                "name": user_data["name"],
                "permissions": user_data.get("permissions", DEFAULT_PERMISSIONS.copy())
            }

            users_data[user_id] = new_user
            app.config['USERS_DATA'] = users_data

            return new_user

        except Exception as e:
            return {"error": f"Invalid request: {str(e)}"}, 400

    @app.route("/users/<user_id>/delete", methods=["POST"])
    def delete_user(user_id: str) -> Dict[str, Any]:
        """Delete user by ID."""
        users_data = app.config['USERS_DATA']

        if user_id not in users_data:
            return {"error": f"User {user_id} not found"}, 404

        deleted_user = users_data.pop(user_id)
        app.config['USERS_DATA'] = users_data

        return {"message": f"User {user_id} deleted", "deleted_user": deleted_user}

    @app.route("/users/<user_id>/permissions", methods=["GET"])
    def get_user_permissions(user_id: str) -> List[str]:
        """Get user permissions by ID."""
        users_data = app.config['USERS_DATA']

        if user_id not in users_data:
            return {"error": f"User {user_id} not found"}, 404

        return users_data[user_id]["permissions"]

    @app.route("/users/<user_id>/permissions", methods=["POST"])
    def update_user_permissions(user_id: str) -> Dict[str, Any]:
        """Update user permissions from posted data."""
        users_data = app.config['USERS_DATA']

        if user_id not in users_data:
            return {"error": f"User {user_id} not found"}, 404

        try:
            data = request.get_json()
            if not data or "permissions" not in data:
                return {"error": "Permissions list is required"}, 400

            permissions = data["permissions"]
            if not isinstance(permissions, list):
                return {"error": "Permissions must be a list"}, 400

            users_data[user_id]["permissions"] = permissions
            app.config['USERS_DATA'] = users_data

            return {
                "user_id": user_id,
                "permissions": permissions,
                "message": "Permissions updated successfully"
            }

        except Exception as e:
            return {"error": f"Invalid request: {str(e)}"}, 400

    @app.route("/", methods=["GET"])
    def root() -> Dict[str, Any]:
        """Return API description."""
        users_data = app.config['USERS_DATA']
        return {
            "name": "Toy API",
            "description": "Simple API for testing API Box",
            "total_users": len(users_data),
            "endpoints": [
                "GET /users/ - List user IDs",
                "GET /users/<user_id> - Get user data",
                "POST /users/<user_id> - Create/update user",
                "POST /users/<user_id>/delete - Delete user",
                "GET /users/<user_id>/permissions - Get user permissions",
                "POST /users/<user_id>/permissions - Update user permissions"
            ]
        }