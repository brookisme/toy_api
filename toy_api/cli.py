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
        _list_table_configs()


@cli.command()
@click.argument("table_config", type=str)
@click.option("--dest", "-d", type=str, help="Destination path (default: tables/<config_name>.parquet)")
@click.option("--type", "-t", type=click.Choice(['parquet', 'csv', 'json', 'ld-json']),
              default='parquet', help="Output file format")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--partition", multiple=True, help="Partition columns (parquet only)")
def table(table_config: str, dest: Optional[str], type: str, force: bool, partition: tuple) -> None:
    """Generate table from configuration file.

    TABLE_CONFIG: Table config name or path (e.g., db1 or config/tables/db1.yaml)

    Examples:
      toy_api table db1
      toy_api table my_table --dest output.parquet
      toy_api table complex --type csv --force
    """
    from toy_api.table_generator import create_table

    try:
        # Find table config file
        config_path = _find_table_config(table_config)

        if not config_path:
            click.echo(f"Error: Table config '{table_config}' not found", err=True)
            click.echo("\nAvailable table configs:")
            _list_table_configs()
            sys.exit(1)

        # Determine destination
        if dest is None:
            # Default: tables/<config_name>.<type>
            config_name = Path(config_path).stem
            dest = f"tables/{config_name}.{type}"

        dest_path = Path(dest)

        # Check if file exists
        if dest_path.exists() and not force:
            click.echo(f"Error: File '{dest}' already exists. Use --force/-f to overwrite.", err=True)
            sys.exit(1)

        # Convert partition tuple to list
        partition_cols = list(partition) if partition else None

        # Generate table(s)
        click.echo(f"Generating table(s) from {config_path}...")
        create_table(
            table_config=config_path,
            dest=dest,
            file_type=type,
            partition_cols=partition_cols
        )

        click.echo(f"✓ Table(s) written to {dest}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--dest", "-d", type=str, help="Destination directory (default: tables/)")
@click.option("--type", "-t", type=click.Choice(['parquet', 'csv', 'json', 'ld-json']),
              default='parquet', help="Output file format")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
def tables(dest: Optional[str], type: str, force: bool) -> None:
    """Generate all tables from toy_api_config/tables/*.yaml.

    Examples:
      toy_api tables
      toy_api tables --dest output/ --type csv
      toy_api tables --force
    """
    from toy_api.table_generator import create_table

    # Find all table configs in toy_api_config/tables/
    config_dir = Path("toy_api_config/tables")

    if not config_dir.exists():
        click.echo("Error: toy_api_config/tables/ directory not found", err=True)
        click.echo("Run 'toy_api init' to create configuration directory")
        sys.exit(1)

    config_files = list(config_dir.glob("*.yaml"))

    if not config_files:
        click.echo("No table configurations found in toy_api_config/tables/", err=True)
        sys.exit(1)

    # Determine destination directory
    if dest is None:
        dest = "tables"

    dest_dir = Path(dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Generating {len(config_files)} table(s)...")

    for config_file in config_files:
        config_name = config_file.stem
        output_path = dest_dir / f"{config_name}.{type}"

        # Check if file exists
        if output_path.exists() and not force:
            click.echo(f"⊗ Skipped {config_name} (file exists, use --force to overwrite)")
            continue

        try:
            create_table(
                table_config=str(config_file),
                dest=str(output_path),
                file_type=type
            )
            click.echo(f"✓ Generated {config_name} → {output_path}")

        except Exception as e:
            click.echo(f"✗ Failed {config_name}: {e}", err=True)

    click.echo(f"\n✓ Complete! Tables written to {dest}/")


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


def _list_table_configs() -> None:
    """List available table configuration files."""
    click.echo("Table Configurations:")
    click.echo()

    # Check local configs
    local_dir = Path("toy_api_config/tables")
    local_configs = []
    if local_dir.exists():
        local_configs = list(local_dir.glob("*.yaml"))

    # Check package configs
    try:
        import importlib.resources as pkg_resources
        package_dir = Path(pkg_resources.files("toy_api") / "config" / "tables")
        package_configs = list(package_dir.glob("*.yaml")) if package_dir.exists() else []
    except Exception:
        package_configs = []

    if local_configs:
        click.echo("📁 Local configs (toy_api_config/tables/):")
        for config_file in sorted(local_configs):
            click.echo(f"  {config_file.stem}")
        click.echo()
    else:
        click.echo("📁 Local configs (toy_api_config/tables/): None")
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
    click.echo("  toy_api table <config>     # Generate single table")
    click.echo("  toy_api tables             # Generate all local tables")


def _find_table_config(config_name: str) -> Optional[str]:
    """Find table configuration file by name.

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
    local_config = Path(f"toy_api_config/tables/{config_name}.yaml")
    if local_config.exists():
        return str(local_config)

    # Check package config directory
    try:
        import importlib.resources as pkg_resources
        package_config = Path(pkg_resources.files("toy_api") / "config" / "tables" / f"{config_name}.yaml")
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
