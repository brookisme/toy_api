"""

Config Discovery for Toy API

Handles finding configuration files in project-local directories or package defaults.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import os
from pathlib import Path
from typing import Optional


#
# CONSTANTS
#
LOCAL_CONFIG_DIR: str = "toy_api_configs"
PACKAGE_CONFIG_DIR: str = "configs"
DEFAULT_CONFIG_NAME: str = "toy_api_v1"


#
# PUBLIC
#
def find_config_path(config_name: Optional[str] = None) -> tuple[str, str]:
    """Find the full path to a configuration file.

    Config discovery priority:
    1. If no config_name provided, use default (toy_api_v1)
    2. Check local project directory: ./toy_api_configs/config_name[.yaml]
    3. Check package configs directory: configs/config_name[.yaml]
    4. Error if not found

    Args:
        config_name: Name of config file (with or without .yaml extension).

    Returns:
        Tuple of (config_path, status_message).
        config_path is empty string if not found.
        status_message explains where config was found or error.
    """
    # Use default if no config specified
    if config_name is None:
        config_name = DEFAULT_CONFIG_NAME

    # Normalize config name (ensure .yaml extension)
    config_name = _normalize_config_name(config_name)

    # Priority 1: Check local project directory
    local_path = _check_local_config(config_name)
    if local_path:
        return local_path, f"Using local config: {local_path}"

    # Priority 2: Check package configs directory
    package_path = _check_package_config(config_name)
    if package_path:
        return package_path, f"Using package config: {config_name}"

    # Not found anywhere
    return "", f"Config '{config_name}' not found in {LOCAL_CONFIG_DIR}/ or package configs/"


def get_available_configs() -> dict[str, list[str]]:
    """Get lists of available configuration files.

    Returns:
        Dictionary with 'local' and 'package' keys containing lists of config names.
    """
    configs = {"local": [], "package": []}

    # Check local configs
    local_dir = Path(LOCAL_CONFIG_DIR)
    if local_dir.exists() and local_dir.is_dir():
        for config_file in local_dir.glob("*.yaml"):
            configs["local"].append(config_file.stem)
        for config_file in local_dir.glob("*.yml"):
            configs["local"].append(config_file.stem)

    # Check package configs
    package_dir = _get_package_config_dir()
    if package_dir and package_dir.exists():
        for config_file in package_dir.glob("*.yaml"):
            configs["package"].append(config_file.stem)
        for config_file in package_dir.glob("*.yml"):
            configs["package"].append(config_file.stem)

    return configs


def create_local_config_dir() -> bool:
    """Create local config directory if it doesn't exist.

    Returns:
        True if directory was created or already exists, False on error.
    """
    try:
        Path(LOCAL_CONFIG_DIR).mkdir(exist_ok=True)
        return True
    except Exception:
        return False


#
# INTERNAL
#
def _normalize_config_name(config_name: str) -> str:
    """Normalize config name to include .yaml extension.

    Args:
        config_name: Config name with or without extension.

    Returns:
        Config name with .yaml extension.
    """
    if not config_name.endswith(('.yaml', '.yml')):
        return f"{config_name}.yaml"
    return config_name


def _check_local_config(config_name: str) -> Optional[str]:
    """Check if config exists in local project directory.

    Args:
        config_name: Config filename with extension.

    Returns:
        Full path if found, None otherwise.
    """
    local_path = Path(LOCAL_CONFIG_DIR) / config_name
    if local_path.exists() and local_path.is_file():
        return str(local_path)

    # Also try .yml extension if .yaml was requested
    if config_name.endswith('.yaml'):
        yml_path = Path(LOCAL_CONFIG_DIR) / config_name.replace('.yaml', '.yml')
        if yml_path.exists() and yml_path.is_file():
            return str(yml_path)

    return None


def _check_package_config(config_name: str) -> Optional[str]:
    """Check if config exists in package configs directory.

    Args:
        config_name: Config filename with extension.

    Returns:
        Full path if found, None otherwise.
    """
    package_dir = _get_package_config_dir()
    if not package_dir:
        return None

    package_path = package_dir / config_name
    if package_path.exists() and package_path.is_file():
        return str(package_path)

    # Also try .yml extension if .yaml was requested
    if config_name.endswith('.yaml'):
        yml_path = package_dir / config_name.replace('.yaml', '.yml')
        if yml_path.exists() and yml_path.is_file():
            return str(yml_path)

    return None


def _get_package_config_dir() -> Optional[Path]:
    """Get path to package configs directory.

    Returns:
        Path to package configs directory, or None if not found.
    """
    try:
        # Get the directory where this module is located
        current_dir = Path(__file__).parent
        # Go up one level to the toy_api package root, then to configs
        package_root = current_dir.parent
        config_dir = package_root / PACKAGE_CONFIG_DIR

        if config_dir.exists() and config_dir.is_dir():
            return config_dir
    except Exception:
        pass

    return None