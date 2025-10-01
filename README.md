# Toy API

Easily configurable test API servers and dummy data generation for testing and development.

## Quick Example

### Toy APIs

Consider the Following config file

```yaml toy_api_config/example.yaml
name: my-api
description: Simple test API
port: 1234

routes:
  - path: "/"
    methods: ["GET"]
    response: "api_info"

  - path: "/users"
    methods: ["GET"]
    response: "user_list"

  - path: "/users/{{user_id}}"
    methods: ["GET"]
    response: "user_detail"
```

Running 

```bash
# launch a toy-api
toy_api start example
```

will launch a flask api filled with dummy data. See [this]() for more information about "response-types" and how the data is generate. This can be configured to return different kinds of data and handle different methods.

### Toy Data

Similarly, an entire database can be created with a simple file

```yaml toy_api_config/databases/example_db.yaml
config:
  NB_USERS: 10

shared:
  user_id[[NB_USERS]]: UNIQUE[int]
  region_name: CHOOSE[[Atlanta, San Francisco, New York]][[1]]

tables:
  users[[NB_USERS]]:
    user_id: [[user_id]]
    age: CHOOSE[[21-89]]
    name: NAME
    job: JOB
    nice: bool
    region_name: [[region_name]]

  permissions:
    user_id: [[user_id]]
    permissions: PERMISSIONS[n]

  regions:
    region_name: [[region_name]]
    area: CHOOSE[[1000-9000]]
```

and running

```bash
# generate files
toy_api database example_db
```

The syntax is described in detail [here](TODO).

--- 

# CLI

## CLI Reference

### Commands

```bash
# Configuration and Info
toy_api                 # List all configs
toy_api init            # Create toy_api_config/ directory
toy_api list            # List all configs
toy_api list --apis     # List only API configs
toy_api list --tables   # List only table configs

# Start/Stop Servers
toy_api start [config]                      # Start API server (foreground)
toy_api start --all                         # Start all servers in toy_api_config/
toy_api start --all versioned_remote        # Start all servers in versioned_remote/
toy_api start --all versioned_remote --out versioned_remote/0.1  # Print output for specific server
toy_api stop <config>                       # Stop specific server
toy_api stop --all                          # Stop all running servers
toy_api stop --all versioned_remote         # Stop all versioned_remote servers
toy_api ps                                  # List running servers

# Generate Data
toy_api database <config>  # Generate tables from database config
```

### Options

**Start command:**
- `--host <host>` - Bind host (default: 127.0.0.1)
- `--port <port>` - Override config port
- `--debug` - Enable debug mode
- `--all` - Start all servers in directory (runs in background)
- `--out <config>` - With --all, print output for specific config (default: last)

**Stop command:**
- `--all` - Stop all servers (or all matching a prefix)

**Database command:**
- `--tables <list>` - Comma-separated list of tables (default: all)
- `--dest <path>` - Output directory (default: tables/)
- `--type <format>` - Format: parquet, csv, json, ld-json (default: parquet)
- `--force` - Overwrite existing files
- `--partition <col>` - Partition column (parquet only, repeatable)

--- 

# TOY-APIs

## Response Types

Available response generators:
- `api_info` - API metadata
- `user_list` - List of users
- `user_detail` - Single user details
- `user_profile` - User profile
- `user_permissions` - User permissions
- `post_list` - List of posts
- `post_detail` - Single post
- `health_check` - Health status

## Configuration

### Port Management

```yaml
port: 8000              # Fixed port
# OR omit for auto-selection (8000-9000 range)
```

### Multiple Methods

```yaml
- path: "/users/<user_id>"
  methods: ["GET", "POST", "PUT"]
  response: "user_detail"
```

### Priority Order

1. **Local configs** - `toy_api_config/*.yaml`
2. **Package configs** - Built-in configurations

--- 

# DUMMY-DB


## Syntax

### Data Types

- `str` - Random string
- `int` - Random integer (0-1000)
- `float` - Random float (0-1000)
- `bool` - Random boolean

### Verbs

**UNIQUE** - Generate unique values

```yaml
id: UNIQUE[int]      # 1000, 1001, 1002, ...
code: UNIQUE[str]    # unique_0000, unique_0001, ...
```

**CHOOSE** - Select from list or range

```yaml
city: CHOOSE[[NYC, LA, SF]]              # Random city
age: CHOOSE[[21-89]]                     # Random age 21-89
tags: CHOOSE[[a, b, c, d]][[2]]         # Exactly 2 tags
items: CHOOSE[[1-100]][[5]]             # 5 random numbers
random: CHOOSE[[x, y, z]][[n]]          # 1-3 items
```

### Constants

**Singular** (single value):
- `FIRST_NAME`, `LAST_NAME`, `LOCATION`, `PERMISSION`
- `THEME`, `LANGUAGE`, `POST_TAG`, `JOB`

**Plural** (list of values):
- `FIRST_NAMES`, `LAST_NAMES`, `LOCATIONS`, `PERMISSIONS`
- `THEMES`, `LANGUAGES`, `POST_TAGS`, `JOBS`

**With count**:

```yaml
tags: POST_TAGS[3]          # Exactly 3 tags
perms: PERMISSIONS[n]       # 1 to all permissions
```

**Special**:

```yaml
name: NAME                  # Full name (first + last)
names: NAMES                # List of full names
```

### Shared Data

Share columns across tables:

```yaml
shared:
  user_id[10]: UNIQUE[int]          # Create 10 unique IDs
  regions: CHOOSE[[A, B, C]][[1]]   # Create region list

tables:
  users[10]:
    user_id: [[user_id]]            # Reference shared IDs
    region: [[regions]]             # Reference regions
```

### Config Variables

Define reusable values:

```yaml
config:
  NB_USERS: 20
  NB_POSTS: 100

shared:
  user_id[[NB_USERS]]: UNIQUE[int]

tables:
  users[[NB_USERS]]:
    user_id: [[user_id]]

  posts[[NB_POSTS]]:
    user_id: [[user_id]]
```

## License

CC-BY-4.0
