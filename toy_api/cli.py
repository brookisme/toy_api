"""

CLI Module for Toy API

Command-line interface for launching the toy Flask API.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import argparse
import sys

from .app import create_app


#
# CONSTANTS
#
DEFAULT_HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 8000
DEFAULT_NB_USERS: int = 5


#
# PUBLIC
#
def main() -> None:
    """Main CLI entry point for Toy API."""
    parser = _create_parser()
    args = parser.parse_args()

    try:
        app = create_app(port=args.port, nb_users=args.nb_users)
        print(f"Starting Toy API server on {args.host}:{args.port} with {args.nb_users} users")

        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except Exception as e:
        print(f"Error starting Toy API: {e}", file=sys.stderr)
        sys.exit(1)


#
# INTERNAL
#
def _create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Toy API - Simple Flask API for testing API Box",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help="Host to bind the server to"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port to bind the server to"
    )

    parser.add_argument(
        "-n", "--nb_users",
        type=int,
        default=DEFAULT_NB_USERS,
        help="Number of users to generate"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )

    return parser


if __name__ == "__main__":
    main()