# Object Notation and Bracket Syntax Reference

Complete guide to Toy API's data generation notation system.

## Bracket Notation Rules

Toy API uses two types of brackets with distinct purposes:

### Single Brackets `[param]` - Parameters and Literal Values

Single brackets denote **parameters** and **literal values**:

```yaml
# Count parameters
tags: CHOOSE[[a, b, c]][2]           # Exactly 2 tags
items: CHOOSE[[1-100]][5]            # 5 random numbers
random: CHOOSE[[x, y, z]][n]         # Random count (1-3)

# Constant with count
permissions: PERMISSIONS[3]          # Exactly 3 permissions
tags: POST_TAGS[n]                   # Random count

# Table row counts (literal)
users[10]:                           # Create 10 rows
  user_id: UNIQUE[int]

# Shared data with literal count
shared:
  user_id[10]: UNIQUE[int]           # Generate 10 IDs

# Object lists
users: [[object.core.user]][5]       # List of 5 user objects
posts: [[object.core.post]][n]       # Random count of posts
```

### Double Brackets `[[VAR]]` - Config Variable References

Double brackets ONLY reference **config variables** defined in the config section:

```yaml
config:
  NB_USERS: 20
  NB_POSTS: 100

shared:
  user_id[[NB_USERS]]: UNIQUE[int]   # Uses NB_USERS from config

tables:
  users[[NB_USERS]]:                 # Creates 20 rows
    user_id: [[user_id]]             # References shared column
    name: NAME

  posts[[NB_POSTS]]:                 # Creates 100 rows
    post_id: UNIQUE[int]
    author: [[user_id]]              # References shared data
```

**Key Rule**: `[[...]]` is ONLY for config variable substitution and shared data references. For everything else, use single brackets `[...]`.

## Object-Based Data Generation

### Basic Syntax

Objects are reusable data structure templates defined in YAML files:

```yaml
# Defining objects in config/objects/my_objects.yaml
user:
  user_id: UNIQUE[int]
  name: NAME
  email: str
  active: bool

post:
  post_id: UNIQUE[int]
  title: POST_TITLE
  content: str
  tags: POST_TAGS[3]
```

### Using Objects

#### In Database Tables

```yaml
tables:
  # Basic object reference
  users[10]:
    object: "my_objects.user"

  # Object with field override
  users_custom[10]:
    object: "my_objects.user"
    user_id: [[shared_user_id]]      # Override field

  # Object with field extension
  users_extended[10]:
    object: "my_objects.user"
    region: LOCATION                 # Add new field
    verified: bool                   # Add another field
```

#### In API Responses

```yaml
routes:
  - route: "/users/{{user_id}}"
    methods: ["GET"]
    response: "core.user"            # Use built-in object

  - route: "/users"
    methods: ["GET"]
    response: "my_objects.user_list" # Use custom object
```

### Self-Referential Objects

Objects can reference other objects to create complex structures:

```yaml
# Define nested objects
user:
  user_id: UNIQUE[int]
  name: NAME
  email: str

user_list:
  users: [[object.core.user]][5]     # List of user objects
  total: 5
  page: 1
  per_page: 10

admin_dashboard:
  stats: [[object.core.stats]]       # Single nested object
  users: [[object.core.user]][3]     # List of nested objects
  alerts: [[0-5]]                    # Random count
```

**Syntax for object references**:
- `[[object.NAMESPACE.NAME]]` - Single object instance
- `[[object.NAMESPACE.NAME]][5]` - List of exactly 5 objects
- `[[object.NAMESPACE.NAME]][n]` - List of random count (1-5)

## Built-in Core Objects

Toy API includes ready-to-use objects in `config/objects/core.yaml`:

| Object | Description |
|--------|-------------|
| `core.user` | Basic user (id, name, email, username, active) |
| `core.user_profile` | Extended profile (bio, location, followers) |
| `core.user_permissions` | User permissions and role |
| `core.user_settings` | User preferences (theme, language, privacy) |
| `core.user_private` | Sensitive data (for security testing) |
| `core.post` | Blog post (title, content, tags) |
| `core.admin` | Admin user with elevated permissions |
| `core.health_check` | Health check response |
| `core.api_info` | API metadata |
| `core.stats` | Dashboard statistics |
| `core.user_list` | Paginated user list |
| `core.post_list` | Paginated post list |
| `core.user_posts` | User with their posts |
| `core.admin_dashboard` | Admin dashboard with stats |
| `core.admin_dangerous` | Dangerous admin operation |
| `core.system_config` | System configuration (sensitive) |

## Data Generation Verbs

### UNIQUE - Generate Unique Values

```yaml
id: UNIQUE[int]         # 1000, 1001, 1002, ...
code: UNIQUE[str]       # unique_0000, unique_0001, ...
```

### CHOOSE - Select from List or Range

```yaml
# Basic selection
city: CHOOSE[[NYC, LA, SF]]           # Random city
age: CHOOSE[[21-89]]                  # Random age 21-89

# With count parameter (single bracket!)
tags: CHOOSE[[a, b, c, d]][2]        # Exactly 2 tags
items: CHOOSE[[1-100]][5]            # 5 random numbers
random: CHOOSE[[x, y, z]][n]         # Random count 1-3

# Reference shared data
region: CHOOSE[[region_name]]         # From shared column
```

### DATE - Generate Dates

```yaml
created: DATE                         # Default format
updated: DATE[%Y-%m-%d]              # Custom format
timestamp: DATE[%Y-%m-%dT%H:%M:%SZ]  # ISO format
```

### Constants

```yaml
# Singular (single value)
name: NAME                            # Full name
first: FIRST_NAME                     # First name only
job: JOB                              # Job title
location: LOCATION                    # City/location

# Plural (list of values)
names: NAMES                          # List of full names
jobs: JOBS                            # List of job titles

# With count (single bracket!)
tags: POST_TAGS[3]                    # Exactly 3 tags
perms: PERMISSIONS[n]                 # Random count
```

## Complete Example

```yaml
config:
  NB_USERS: 20
  NB_POSTS: 50

shared:
  user_id[[NB_USERS]]: UNIQUE[int]
  region_name: CHOOSE[[East, West, North]][1]

tables:
  # Using built-in object with overrides
  users[[NB_USERS]]:
    object: "core.user"
    user_id: [[user_id]]              # Override with shared ID
    region: [[region_name]]           # Add region field
    age: CHOOSE[[21-89]]              # Add age field

  # Using built-in object for permissions
  permissions[[NB_USERS]]:
    object: "core.user_permissions"
    user_id: [[user_id]]              # Link to users

  # Custom table definition (no object)
  posts[[NB_POSTS]]:
    post_id: UNIQUE[int]
    title: POST_TITLE
    author_id: CHOOSE[[user_id]]      # Reference user
    tags: POST_TAGS[n]                # Random tag count
    published: bool

  # Custom table for regions
  regions[3]:
    region_name: [[region_name]]
    population: [[100000-1000000]]
    timezone: CHOOSE[[EST, PST, MST]]
```

## Benefits of Object Notation

1. **DRY Principle** - Define data structures once, use everywhere
2. **Consistency** - Same structure across tables and APIs
3. **Maintainability** - Update definition, all usages update
4. **Flexibility** - Override or extend fields as needed
5. **Composability** - Nest objects to create complex structures
6. **Backward Compatible** - Custom table definitions still work

## Migration from Old Syntax

The notation was standardized to improve clarity:

### Before (old notation - no longer supported)
```yaml
tags: CHOOSE[[a, b, c]][[2]]         # Double brackets for count
users[[10]]:                         # Literal count with double brackets
  user_id[[10]]: UNIQUE[int]         # Shared data with double brackets
```

### After (current notation)
```yaml
tags: CHOOSE[[a, b, c]][2]           # Single bracket for count parameter
users[10]:                           # Single bracket for literal count
  user_id[10]: UNIQUE[int]           # Single bracket for literal count

# Double brackets ONLY for config variables:
users[[NB_USERS]]:                   # Config variable reference
  user_id[[shared_id]]:              # Shared data reference
```

**Remember**: Single brackets `[param]` for parameters and literals. Double brackets `[[VAR]]` ONLY for config/shared variable references.
