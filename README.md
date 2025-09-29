# Toy API - Configurable Routes

A YAML-configurable Flask API for testing API Box route restrictions and allowed routes functionality.

## Overview

Toy API allows you to define API routes and responses through YAML configuration files. This makes it perfect for testing different route restriction scenarios in API Box without having to modify code.

## Features

- **YAML-Configurable Routes**: Define endpoints, HTTP methods, and response types in YAML
- **Smart Port Management**: Automatic port selection with availability checking
- **Dummy Data Generation**: Automatic generation of realistic test data
- **Multiple Configurations**: Support for different API configurations
- **Simple Responses**: JSON responses with configurable data types

## Quick Start

### 1. List Available Configurations

```bash
toy_api --list-configs
```

### 2. Start an API with a Specific Configuration

```bash
# Start the API with config-specified port (4321)
toy_api --config configs/toy_api_v2.yaml

# Start with custom port override
toy_api --config configs/toy_api_v1.yaml --port 5000

# Start with debug mode (uses config port 8080)
toy_api --config configs/toy_api_v3.yaml --debug

# Start without config (auto-selects available port)
toy_api
```

### 3. Test the API

```bash
curl http://127.0.0.1:4321/
curl http://127.0.0.1:4321/users
curl http://127.0.0.1:4321/users/123/profile
```

## Port Management

The toy API includes smart port management:

### Port Selection Priority

1. **Command Line Flag**: `--port/-p` takes highest priority
2. **Config File**: Uses `port` value from YAML config if specified
3. **Auto-Selection**: Automatically finds available port (8000-9000 range)

### Port Availability Checking

- **Port Taken**: If specified port is unavailable, shows helpful error message
- **Auto-Fallback**: If config port is taken, auto-selects alternative with notification
- **Range Scanning**: Searches 8000-9000 range for available ports

### Examples

```bash
# Use config-specified port (4321) if available
toy_api --config configs/toy_api_v2.yaml

# Force specific port (error if taken)
toy_api --config configs/toy_api_v2.yaml --port 5000

# Auto-select port when no config specified
toy_api

# See helpful error if port is taken
toy_api --port 80  # Likely shows "Port 80 is already in use..."
```

## Configuration Files

### Available Configurations

1. **`toy_api_v2.yaml`** - Basic API with all route types for comprehensive testing (port 4321)
2. **`toy_api_v1.yaml`** - Custom endpoint structure for testing route mapping (port 1234)
3. **`toy_api_v3.yaml`** - Security-focused API for testing restrictions (port 8080)
4. **`toy_api_v4.yaml`** - Limited endpoints for testing allowed routes whitelist (port 9090)

### Configuration Format

```yaml
name: "my-toy-api"
description: "Description of this API configuration"
port: 8000  # Optional: if not specified, auto-selects available port

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
toy_api --config configs/toy_api_v2.yaml

# Terminal 2: Custom mapping API (port 1234)
toy_api --config configs/toy_api_v1.yaml

# Terminal 3: Restricted API (port 8080)
toy_api --config configs/toy_api_v3.yaml

# Terminal 4: Whitelist API (port 9090)
toy_api --config configs/toy_api_v4.yaml
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