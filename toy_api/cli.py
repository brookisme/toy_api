#!/usr/bin/env python3
"""

CLI for Toy API

Launch configurable toy APIs from YAML configuration files.

License: CC-BY-4.0

"""
#
# IMPORTS
#
import argparse
import sys
from pathlib import Path

from toy_api.app import create_app, _load_config
from toy_api.constants import DEFAULT_HOST
from toy_api.port_utils import get_port_from_config_or_auto
from toy_api.config_discovery import find_config_path, get_available_configs, create_local_config_dir


#
# PUBLIC
#
def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Launch configurable toy API from YAML configuration"
    )

    parser.add_argument(
        "config",
        nargs="?",
        type=str,
        help="Config name or path (default: v1). Searches toy_api_config/ then package config/"
    )

    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help=f"Host to bind to (default: {DEFAULT_HOST})"
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="Port to bind to (overrides config file)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List available configuration files"
    )

    parser.add_argument(
        "--init-configs",
        action="store_true",
        help="Create toy_api_config/ directory in current project"
    )

    args = parser.parse_args()

    if args.list_configs:
        list_available_configs()
        return 0

    if args.init_configs:
        if create_local_config_dir():
            print(f"Created toy_api_config/ directory")
            print("You can now copy and customize config files:")
            print("  cp <package_config>/*.yaml toy_api_config/")
            return 0
        else:
            print("Error: Could not create toy_api_config/ directory", file=sys.stderr)
            return 1

    try:
        # Find config file using discovery system
        config_path, config_message = find_config_path(args.config)

        if not config_path:
            print(f"Error: {config_message}", file=sys.stderr)
            print("\nAvailable configs:")
            list_available_configs()
            return 1

        # Create Flask app from discovered config
        app = create_app(config_path)

        # Load config for port determination
        config = {}
        try:
            config = _load_config(config_path)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

        # Determine port using smart port logic
        port, port_message = get_port_from_config_or_auto(config, args.port, args.host)

        if port == 0:
            print(f"Error: {port_message}", file=sys.stderr)
            return 1

        print(f"Starting toy API...")
        print(f"Config: {config_message}")
        if port_message:
            print(f"Port: {port_message}")
        print(f"Server: http://{args.host}:{port}")
        print("Press Ctrl+C to stop")

        # Start the server
        app.run(host=args.host, port=port, debug=args.debug)

        return 0

    except FileNotFoundError as e:
        print(f"Error: Configuration file not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def list_available_configs() -> None:
    """List available configuration files."""
    print("Available configuration files:")
    print()

    configs = get_available_configs()

    # Show local configs first
    if configs["local"]:
        print("📁 Local configs (toy_api_config/):")
        for config_name in sorted(configs["local"]):
            try:
                config_path, _ = find_config_path(config_name)
                if config_path:
                    config = _load_config(config_path)
                    name = config.get("name", "Unknown")
                    description = config.get("description", "No description")
                    port = config.get("port", "Auto")
                    route_count = len(config.get("routes", []))

                    print(f"  {config_name}")
                    print(f"    Name: {name}")
                    print(f"    Description: {description}")
                    print(f"    Port: {port}")
                    print(f"    Routes: {route_count}")
                    print()
            except Exception as e:
                print(f"  {config_name} (Error loading: {e})")
                print()
    else:
        print("📁 Local configs (toy_api_config/): None")
        print()

    # Show package configs
    if configs["package"]:
        print("📦 Package configs:")
        for config_name in sorted(configs["package"]):
            try:
                config_path, _ = find_config_path(config_name)
                if config_path:
                    config = _load_config(config_path)
                    name = config.get("name", "Unknown")
                    description = config.get("description", "No description")
                    port = config.get("port", "Auto")
                    route_count = len(config.get("routes", []))

                    print(f"  {config_name}")
                    print(f"    Name: {name}")
                    print(f"    Description: {description}")
                    print(f"    Port: {port}")
                    print(f"    Routes: {route_count}")
                    print()
            except Exception as e:
                print(f"  {config_name} (Error loading: {e})")
                print()
    else:
        print("📦 Package configs: None found")
        print()

    print("Usage:")
    print(f"  toy_api                    # Use default (v1)")
    print(f"  toy_api <config_name>      # Use specific config")
    print(f"  toy_api --init-configs     # Create toy_api_config/ directory")


if __name__ == "__main__":
    sys.exit(main())