#!/usr/bin/env python3
"""

CLI for Toy API

Launch configurable toy APIs from YAML configuration files and generate dummy data tables.

License: CC-BY-4.0

"""
#
# IMPORTS
#
import sys
from pathlib import Path
from typing import Optional

import click

from toy_api.app import _load_config, create_app
from toy_api.config_discovery import find_config_path, get_available_configs, init_config_with_example
from toy_api.constants import DEFAULT_HOST
from toy_api.port_utils import get_port_from_config_or_auto


#
# MAIN CLI GROUP
#
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Toy API - Configurable test API servers and dummy data generation.

    Run without a command to list available configurations.
    """
    if ctx.invoked_subcommand is None:
        list_configs(apis=True, tables=True)


#
# COMMANDS
#
@cli.command()
def init() -> None:
    """Initialize toy_api_config directory with example configuration."""
    if init_config_with_example():
        click.echo("✓ Created toy_api_config/ directory")
        click.echo("✓ Copied v1.yaml to toy_api_config/example.yaml")
        click.echo()
        click.echo("You can now customize example.yaml or add more configs:")
        click.echo("  toy_api start example    # Use the example config")
        click.echo("  cp <other_configs> toy_api_config/")
    else:
        click.echo("Error: Could not initialize toy_api_config/ directory", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config", required=False, default="v1", type=str)
@click.option("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
@click.option("-p", "--port", type=int, help="Port to bind to (overrides config file)")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def start(config: str, host: str, port: Optional[int], debug: bool) -> None:
    """Start toy API server with specified configuration.

    CONFIG: Config name or path (default: v1)

    Examples:
      toy_api start
      toy_api start v2
      toy_api start custom_config --port 5000
    """
    try:
        # Find config file using discovery system
        config_path, config_message = find_config_path(config)

        if not config_path:
            click.echo(f"Error: {config_message}", err=True)
            click.echo("\nAvailable configs:")
            list_configs(apis=True, tables=False)
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


@cli.command(name="list")
@click.option("--apis", is_flag=True, help="List only API configurations")
@click.option("--tables", is_flag=True, help="List only table configurations")
def list_configs(apis: bool, tables: bool) -> None:
    """List available API and table configurations."""
    # If neither flag specified, show both
    if not apis and not tables:
        apis = True
        tables = True

    if apis:
        _list_api_configs()

    if tables:
        _list_database_configs()


@cli.command()
@click.argument("database_config", type=str)
@click.option("--tables", type=str, help="Comma-separated list of tables to generate (default: all)")
@click.option("--dest", "-d", type=str, help="Destination directory (default: tables/)")
@click.option("--type", "-t", type=click.Choice(['parquet', 'csv', 'json', 'ld-json']),
              default='parquet', help="Output file format")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--partition", multiple=True, help="Partition columns (parquet only)")
def database(database_config: str, tables: Optional[str], dest: Optional[str],
             type: str, force: bool, partition: tuple) -> None:
    """Generate tables from database configuration file.

    DATABASE_CONFIG: Database config name or path (e.g., test_db or config/databases/test_db.yaml)

    Examples:
      toy_api database test_db
      toy_api database test_db --tables posts
      toy_api database test_db --tables posts,users
      toy_api database test_db --dest output/ --type csv --force
    """
    from toy_api.table_generator import create_table

    try:
        # Find database config file
        config_path = _find_database_config(database_config)

        if not config_path:
            click.echo(f"Error: Database config '{database_config}' not found", err=True)
            click.echo("\nAvailable database configs:")
            _list_database_configs()
            sys.exit(1)

        # Determine destination
        if dest is None:
            dest = "tables"

        dest_dir = Path(dest)
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Convert partition tuple to list
        partition_cols = list(partition) if partition else None

        # Parse tables filter
        tables_filter = None
        if tables:
            tables_filter = [t.strip() for t in tables.split(',')]

        # Generate table(s)
        click.echo(f"Generating tables from {config_path}...")
        create_table(
            table_config=config_path,
            dest=str(dest_dir),
            file_type=type,
            partition_cols=partition_cols,
            tables_filter=tables_filter,
            force=force
        )

        click.echo(f"✓ Tables written to {dest_dir}/")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


#
# INTERNAL HELPERS
#
def _list_api_configs() -> None:
    """List available API configuration files."""
    click.echo("API Configurations:")
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
    click.echo("  toy_api start              # Use default (v1)")
    click.echo("  toy_api start <config>     # Use specific config")
    click.echo("  toy_api init               # Create toy_api_config/")


def _list_database_configs() -> None:
    """List available database configuration files."""
    click.echo("Database Configurations:")
    click.echo()

    # Check local configs
    local_dir = Path("toy_api_config/databases")
    local_configs = []
    if local_dir.exists():
        local_configs = list(local_dir.glob("*.yaml"))

    # Check package configs
    try:
        import importlib.resources as pkg_resources
        package_dir = Path(pkg_resources.files("toy_api") / "config" / "databases")
        package_configs = list(package_dir.glob("*.yaml")) if package_dir.exists() else []
    except Exception:
        package_configs = []

    if local_configs:
        click.echo("📁 Local configs (toy_api_config/databases/):")
        for config_file in sorted(local_configs):
            click.echo(f"  {config_file.stem}")
        click.echo()
    else:
        click.echo("📁 Local configs (toy_api_config/databases/): None")
        click.echo()

    if package_configs:
        click.echo("📦 Package configs:")
        for config_file in sorted(package_configs):
            click.echo(f"  {config_file.stem}")
        click.echo()
    else:
        click.echo("📦 Package configs: None found")
        click.echo()

    click.echo("Usage:")
    click.echo("  toy_api database <config>              # Generate all tables")
    click.echo("  toy_api database <config> --tables <t> # Generate specific tables")


def _find_database_config(config_name: str) -> Optional[str]:
    """Find database configuration file by name.

    Args:
        config_name: Config name or path.

    Returns:
        Path to config file or None if not found.
    """
    # Remove .yaml extension if provided
    if config_name.endswith('.yaml'):
        config_name = config_name[:-5]

    # Check if it's a direct path
    config_path = Path(config_name)
    if config_path.exists():
        return str(config_path)

    # Add .yaml if needed
    if not str(config_path).endswith('.yaml'):
        config_path = Path(f"{config_name}.yaml")
        if config_path.exists():
            return str(config_path)

    # Check local config directory
    local_config = Path(f"toy_api_config/databases/{config_name}.yaml")
    if local_config.exists():
        return str(local_config)

    # Check package config directory
    try:
        import importlib.resources as pkg_resources
        package_config = Path(pkg_resources.files("toy_api") / "config" / "databases" / f"{config_name}.yaml")
        if package_config.exists():
            return str(package_config)
    except Exception:
        pass

    return None


#
# ENTRY POINT
#
def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
