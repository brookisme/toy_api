"""

Constants for Toy API

Contains all constant values used throughout the application including dummy data
and configuration defaults.

License: CC-BY-4.0

"""

#
# IMPORTS
#
from typing import Any, Dict, List


#
# CONSTANTS
#
DEFAULT_CONFIG_PATH: str = "configs/toy_api_v1.yaml"
DEFAULT_HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 8000

# Dummy data for user generation
FIRST_NAMES: List[str] = [
    "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Helen",
    "Ian", "Julia", "Kevin", "Luna", "Mark", "Nina", "Oscar", "Paula"
]

LAST_NAMES: List[str] = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Foster", "Garcia", "Harris",
    "Jackson", "Kim", "Lopez", "Miller", "Nelson", "O'Connor", "Parker", "Quinn"
]

# Dummy data for post generation
POST_TITLES: List[str] = [
    "Introduction to APIs", "Building Scalable Systems", "Database Design Patterns",
    "Security Best Practices", "Testing Strategies", "DevOps Fundamentals",
    "Code Review Guidelines", "Performance Optimization", "Documentation Standards"
]

# Locations for user profiles
LOCATIONS: List[str] = [
    "San Francisco", "New York", "London", "Tokyo", "Berlin", "Toronto", "Sydney",
    "Amsterdam", "Barcelona", "Singapore", "Austin", "Seattle", "Portland"
]

# Permissions for user access control
PERMISSIONS: List[str] = [
    "read", "write", "delete", "admin", "create", "update", "execute", "manage"
]

# Themes for user settings
THEMES: List[str] = ["light", "dark", "auto"]

# Languages for user settings
LANGUAGES: List[str] = ["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"]

# Tags for posts
POST_TAGS: List[str] = [
    "tech", "api", "tutorial", "guide", "tips", "best-practices", "development",
    "programming", "web", "mobile", "database", "security", "performance"
]

# Recent activities for admin dashboard
ADMIN_ACTIVITIES: List[str] = [
    "User login", "Data backup", "System update", "Security scan",
    "Cache refresh", "Database maintenance", "Log rotation", "Config update"
]

# Default response type mappings
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