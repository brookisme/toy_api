#!/usr/bin/env python3
"""

Test script for configurable toy APIs

Tests that the YAML-configured APIs work correctly and return expected data.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import requests
import time
from typing import Dict, List


#
# CONSTANTS
#
API_CONFIGS = [
    {"name": "toy-api-v2", "port": 4321, "config": "configs/toy_api_v2.yaml"},
    {"name": "toy-api-v1", "port": 1234, "config": "configs/toy_api_v1.yaml"},
    {"name": "toy-api-v3", "port": 8080, "config": "configs/toy_api_v3.yaml"},
    {"name": "toy-api-v4", "port": 9090, "config": "configs/toy_api_v4.yaml"},
]


#
# PUBLIC
#
def test_api_endpoints() -> None:
    """Test API endpoints for each configured API."""
    print("Testing configurable toy APIs...")
    print("=" * 60)

    for api_config in API_CONFIGS:
        test_single_api(api_config)


def test_single_api(api_config: Dict[str, any]) -> None:
    """Test a single API configuration.

    Args:
        api_config: API configuration dictionary.
    """
    name = api_config["name"]
    port = api_config["port"]
    base_url = f"http://127.0.0.1:{port}"

    print(f"\nTesting {name} on port {port}")
    print("-" * 40)

    # Test basic endpoints
    test_cases = [
        "/",
        "/users",
        "/users/123",
        "/users/123/profile",
        "/users/123/permissions",
        "/users/123/settings",
        "/admin",
        "/admin/dashboard",
        "/health",
    ]

    for endpoint in test_cases:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {endpoint}: {response.status_code} - {list(data.keys())[:3]}...")
            else:
                print(f"✗ {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ {endpoint}: Connection failed ({e})")


def main() -> None:
    """Main test function."""
    print("Configurable Toy API Test Suite")
    print("\nMake sure to start the APIs first:")
    print("  toy_api --config configs/toy_api_v2.yaml")
    print("  toy_api --config configs/toy_api_v1.yaml")
    print("  toy_api --config configs/toy_api_v3.yaml")
    print("  toy_api --config configs/toy_api_v4.yaml")
    print()

    input("Press Enter when APIs are running...")

    test_api_endpoints()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nThese APIs are now ready for testing with API Box route restrictions.")


if __name__ == "__main__":
    main()