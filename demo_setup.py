#!/usr/bin/env python3
"""

Demo setup script for toy API v2

Shows the available configurations and demonstrates the setup.

License: CC-BY-4.0

"""

#
# IMPORTS
#
from toy_api.app import _load_config


#
# PUBLIC
#
def show_configurations():
    """Show all available API configurations."""
    print("🚀 Toy API - Configurable Route Demo")
    print("=" * 60)
    print()

    configs = [
        "configs/port_4321.yaml",
        "configs/port_1234.yaml",
        "configs/port_8080.yaml",
        "configs/port_9090.yaml"
    ]

    for config_path in configs:
        try:
            config = _load_config(config_path)
            print(f"📁 {config_path}")
            print(f"   Name: {config['name']}")
            print(f"   Description: {config['description']}")
            print(f"   Port: {config['port']}")
            print(f"   Routes: {len(config['routes'])} endpoints")

            # Show some example routes
            example_routes = []
            for route in config['routes'][:5]:  # Show first 5 routes
                path = route['path']
                methods = '/'.join(route['methods'])
                example_routes.append(f"{methods} {path}")

            print(f"   Examples: {', '.join(example_routes[:3])}...")
            print()

        except Exception as e:
            print(f"❌ Error loading {config_path}: {e}")
            print()

    print("🧪 Test Project Route Mapping:")
    print("   remote_4321 → port_4321.yaml (Basic routes)")
    print("   another_name → port_1234.yaml (Custom mappings)")
    print("   restricted_remote → port_8080.yaml (Security testing)")
    print("   allowed_routes_remote → port_9090.yaml (Whitelist testing)")
    print()

    print("🚀 To start APIs:")
    print("   toy_api --config configs/port_4321.yaml")
    print("   toy_api --config configs/port_1234.yaml")
    print("   toy_api --config configs/port_8080.yaml")
    print("   toy_api --config configs/port_9090.yaml")
    print()

    print("🧪 To test route restrictions:")
    print("   cd ../test_project")
    print("   python test_route_restrictions.py")


if __name__ == "__main__":
    show_configurations()