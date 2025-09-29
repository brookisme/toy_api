#!/usr/bin/env python3
"""

CLI for Toy API

Launch configurable toy APIs from YAML configuration files.

License: CC-BY-4.0

"""
#
# IMPORTS
#
import sys
import click
from pathlib import Path

from toy_api.app import create_app, _load_config
from toy_api.constants import DEFAULT_HOST
from toy_api.port_utils import get_port_from_config_or_auto
from toy_api.config_discovery import find_config_path, get_available_configs, init_config_with_example


#
# CLICK COMMANDS
#
@click.command()
@click.argument("config", required=False, type=str)
@click.option("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
@click.option("-p", "--port", type=int, help="Port to bind to (overrides config file)")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--list-configs", is_flag=True, help="List available configuration files")
@click.option("--init-config", is_flag=True, help="Create toy_api_config/ directory and copy v1.yaml as example.yaml")
def main(config, host, port, debug, list_configs, init_config):
    """Launch configurable toy API from YAML configuration.

    CONFIG: Config name or path (default: v1). Searches toy_api_config/ then package config/
    """
    if list_configs:
        list_available_configs()
        return

    if init_config:
        if init_config_with_example():
            click.echo("Created toy_api_config/ directory")
            click.echo("Copied v1.yaml to toy_api_config/example.yaml")
            click.echo()
            click.echo("You can now customize example.yaml or add more configs:")
            click.echo("  toy_api example    # Use the example config")
            click.echo("  cp <other_configs> toy_api_config/")
        else:
            click.echo("Error: Could not initialize toy_api_config/ directory", err=True)
            sys.exit(1)
        return

    try:
        # Find config file using discovery system
        config_path, config_message = find_config_path(config)

        if not config_path:
            click.echo(f"Error: {config_message}", err=True)
            click.echo("\nAvailable configs:")
            list_available_configs()
            sys.exit(1)

        # Create Flask app from discovered config
        app = create_app(config_path)

        # Load config for port determination
        app_config = {}
        try:
            app_config = _load_config(config_path)
        except Exception as e:
            click.echo(f"Warning: Could not load config file: {e}")

        # Determine port using smart port logic
        final_port, port_message = get_port_from_config_or_auto(app_config, port, host)

        if final_port == 0:
            click.echo(f"Error: {port_message}", err=True)
            sys.exit(1)

        click.echo("Starting toy API...")
        click.echo(f"Config: {config_message}")
        if port_message:
            click.echo(f"Port: {port_message}")
        click.echo(f"Server: http://{host}:{final_port}")
        click.echo("Press Ctrl+C to stop")

        # Start the server
        app.run(host=host, port=final_port, debug=debug)

    except FileNotFoundError as e:
        click.echo(f"Error: Configuration file not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def list_available_configs() -> None:
    """List available configuration files."""
    click.echo("Available configuration files:")
    click.echo()

    configs = get_available_configs()

    # Show local configs first
    if configs["local"]:
        click.echo("📁 Local configs (toy_api_config/):")
        for config_name in sorted(configs["local"]):
            try:
                config_path, _ = find_config_path(config_name)
                if config_path:
                    config = _load_config(config_path)
                    name = config.get("name", "Unknown")
                    description = config.get("description", "No description")
                    config_port = config.get("port", "Auto")
                    route_count = len(config.get("routes", []))

                    click.echo(f"  {config_name}")
                    click.echo(f"    Name: {name}")
                    click.echo(f"    Description: {description}")
                    click.echo(f"    Port: {config_port}")
                    click.echo(f"    Routes: {route_count}")
                    click.echo()
            except Exception as e:
                click.echo(f"  {config_name} (Error loading: {e})")
                click.echo()
    else:
        click.echo("📁 Local configs (toy_api_config/): None")
        click.echo()

    # Show package configs
    if configs["package"]:
        click.echo("📦 Package configs:")
        for config_name in sorted(configs["package"]):
            try:
                config_path, _ = find_config_path(config_name)
                if config_path:
                    config = _load_config(config_path)
                    name = config.get("name", "Unknown")
                    description = config.get("description", "No description")
                    config_port = config.get("port", "Auto")
                    route_count = len(config.get("routes", []))

                    click.echo(f"  {config_name}")
                    click.echo(f"    Name: {name}")
                    click.echo(f"    Description: {description}")
                    click.echo(f"    Port: {config_port}")
                    click.echo(f"    Routes: {route_count}")
                    click.echo()
            except Exception as e:
                click.echo(f"  {config_name} (Error loading: {e})")
                click.echo()
    else:
        click.echo("📦 Package configs: None found")
        click.echo()

    click.echo("Usage:")
    click.echo("  toy_api                    # Use default (v1)")
    click.echo("  toy_api <config_name>      # Use specific config")
    click.echo("  toy_api --init-config      # Create toy_api_config/ with example.yaml")


if __name__ == "__main__":
    main()