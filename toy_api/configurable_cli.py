#!/usr/bin/env python3
"""

CLI for Configurable Toy API v2

Launch configurable toy APIs from YAML configuration files.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import argparse
import sys
from pathlib import Path

from toy_api.configurable_app import create_configurable_app, _load_config


#
# CONSTANTS
#
DEFAULT_HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 8000


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
        "--config",
        "-c",
        type=str,
        help="Path to YAML configuration file (default: configs/default.yaml)"
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

    args = parser.parse_args()

    if args.list_configs:
        list_available_configs()
        return 0

    try:
        # Create Flask app from config
        app = create_configurable_app(args.config)

        # Determine port
        port = args.port
        if port is None and args.config:
            try:
                config = _load_config(args.config)
                port = config.get("port", DEFAULT_PORT)
            except Exception:
                port = DEFAULT_PORT
        elif port is None:
            port = DEFAULT_PORT

        print(f"Starting configurable toy API...")
        if args.config:
            print(f"Config file: {args.config}")
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

    configs_dir = Path("configs")
    if not configs_dir.exists():
        print("  No configs directory found")
        return

    yaml_files = list(configs_dir.glob("*.yaml")) + list(configs_dir.glob("*.yml"))

    if not yaml_files:
        print("  No YAML configuration files found in configs/")
        return

    for config_file in sorted(yaml_files):
        try:
            config = _load_config(str(config_file))
            name = config.get("name", "Unknown")
            description = config.get("description", "No description")
            port = config.get("port", "Unknown")
            route_count = len(config.get("routes", []))

            print(f"  {config_file.name}")
            print(f"    Name: {name}")
            print(f"    Description: {description}")
            print(f"    Port: {port}")
            print(f"    Routes: {route_count}")
            print()
        except Exception as e:
            print(f"  {config_file.name} (Error loading: {e})")
            print()


if __name__ == "__main__":
    sys.exit(main())