# Toy API - Configurable Routes

A YAML-configurable Flask API for testing API Box route restrictions and allowed routes functionality.

## Overview

Toy API allows you to define API routes and responses through YAML configuration files. This makes it perfect for testing different route restriction scenarios in API Box without having to modify code.

## Features

- **YAML-Configurable Routes**: Define endpoints, HTTP methods, and response types in YAML
- **Dummy Data Generation**: Automatic generation of realistic test data
- **Multiple Configurations**: Support for different API configurations on different ports
- **Simple Responses**: JSON responses with configurable data types

## Quick Start

### 1. List Available Configurations

```bash
toy_api --list-configs
```

### 2. Start an API with a Specific Configuration

```bash
# Start the API for port 4321 (basic routes)
toy_api --config configs/port_4321.yaml

# Start the API for port 1234 (custom mapping routes)
toy_api --config configs/port_1234.yaml --port 1234

# Start with debug mode
toy_api --config configs/port_8080.yaml --debug
```

### 3. Test the API

```bash
curl http://127.0.0.1:4321/
curl http://127.0.0.1:4321/users
curl http://127.0.0.1:4321/users/123/profile
```

## Configuration Files

### Available Configurations

1. **`port_4321.yaml`** - Basic API with all route types for comprehensive testing
2. **`port_1234.yaml`** - Custom endpoint structure for testing route mapping
3. **`port_8080.yaml`** - Security-focused API for testing restrictions
4. **`port_9090.yaml`** - Limited endpoints for testing allowed routes whitelist

### Configuration Format

```yaml
name: "my-toy-api"
description: "Description of this API configuration"
port: 8000

routes:
  - path: "/users"
    methods: ["GET"]
    response: "user_list"

  - path: "/users/<user_id>"
    methods: ["GET", "POST"]
    response: "user_detail"

  - path: "/admin/<admin_id>/dangerous"
    methods: ["GET", "POST"]
    response: "admin_dangerous"
```

### Response Types

- `user_list` - List of users
- `user_detail` - Individual user data
- `user_profile` - User profile information
- `user_permissions` - User permission data
- `user_posts` - User's posts
- `user_settings` - User settings
- `user_private` - Private user data (sensitive)
- `post_list` - List of posts
- `post_detail` - Individual post data
- `admin_dashboard` - Admin dashboard data
- `admin_detail` - Admin user data
- `admin_dangerous` - Dangerous admin operation (should be restricted!)
- `system_config` - System configuration (sensitive)
- `health_check` - Health status

## Testing with API Box

These configurations are designed to work with the route restrictions test in the test_project:

### 1. Start the Toy APIs

```bash
# Terminal 1: Basic API (port 4321)
toy_api --config configs/port_4321.yaml

# Terminal 2: Custom mapping API (port 1234)
toy_api --config configs/port_1234.yaml

# Terminal 3: Restricted API (port 8080)
toy_api --config configs/port_8080.yaml

# Terminal 4: Whitelist API (port 9090)
toy_api --config configs/port_9090.yaml
```

### 2. Test Route Restrictions

```bash
cd ../test_project
python test_route_restrictions.py
```

### 3. Manual Testing

```bash
# These should work (allowed routes)
curl http://localhost:8000/remote_4321/latest/users
curl http://localhost:8000/remote_4321/latest/users/123/profile

# These should be blocked (restricted routes)
curl http://localhost:8000/remote_4321/latest/users/123/delete
curl http://localhost:8000/restricted_remote/latest/admin/dashboard
```

## Route Mapping Examples

The different configurations demonstrate:

- **Global restrictions** (`users/{{}}/delete` blocked everywhere)
- **Remote-specific restrictions** (different per API)
- **Allowed routes whitelist** (only specific routes allowed)
- **Custom route mapping** (different API signatures)

## Development

### Adding New Response Types

1. Add the response type to `_generate_response()` in `configurable_app.py`
2. Create YAML configurations that use the new response type
3. Test with the toy API and API Box

### Adding New Route Patterns

Simply add them to your YAML configuration file:

```yaml
routes:
  - path: "/my/custom/<param>/route"
    methods: ["GET", "POST"]
    response: "my_custom_response"
```

## License

CC-BY-4.0