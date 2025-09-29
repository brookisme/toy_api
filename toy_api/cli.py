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
        app = create_app(args.config)

        # Load config for port determination
        config = {}
        if args.config:
            try:
                config = _load_config(args.config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")

        # Determine port using smart port logic
        port, port_message = get_port_from_config_or_auto(config, args.port, args.host)

        if port == 0:
            print(f"Error: {port_message}", file=sys.stderr)
            return 1

        print(f"Starting toy API...")
        if args.config:
            print(f"Config file: {args.config}")
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