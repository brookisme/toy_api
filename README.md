# Toy API

A simple Flask-based REST API for testing API Box functionality. This API provides user management endpoints with configurable user data generation.

## Description

Toy API is a lightweight Flask application that generates random user data and provides REST endpoints for user management operations. It's designed specifically for testing API Box proxy functionality but can be used as a standalone development API.

## Features

- Random user data generation with configurable parameters
- RESTful endpoints for user CRUD operations
- User permissions management
- Configurable port and user count
- Built-in Flask development server

## Quick Start

### Installation

Requirements are managed through a [Pixi](https://pixi.sh/latest) project environment:

```bash
# Install dependencies (first time only)
pixi install

# Or run directly (will install dependencies automatically)
pixi run toy-api --help
```

### Basic Usage

```bash
# Start the API server with default settings (port 8000, 5 users)
pixi run toy-api

# Start with custom settings
pixi run toy-api --host 0.0.0.0 --port 8080 --nb_users 10

# Run in debug mode
pixi run toy-api --debug
```

### API Endpoints

Once running, the API provides the following endpoints:

- `GET /` - API metadata and endpoint list
- `GET /users/` - List all user IDs
- `GET /users/<user_id>` - Get user data by ID
- `POST /users/<user_id>` - Create or update user
- `POST /users/<user_id>/delete` - Delete user
- `GET /users/<user_id>/permissions` - Get user permissions
- `POST /users/<user_id>/permissions` - Update user permissions

### Example Usage

```bash
# Get API info
curl http://localhost:8000/

# List users
curl http://localhost:8000/users/

# Get specific user
curl http://localhost:8000/users/{user-id}

# Create a new user
curl -X POST http://localhost:8000/users/new-user-id \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "permissions": ["read", "write"]}'
```

## Development

The project follows Python best practices:

- Type hints throughout
- Comprehensive docstrings
- PEP 8 style compliance
- Modular structure with separate CLI and app modules

## License

CC-BY-4.0