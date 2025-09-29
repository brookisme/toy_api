"""

Port Utility Functions for Toy API

Handles port availability checking and automatic port selection.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import socket
from typing import Optional


#
# CONSTANTS
#
DEFAULT_PORT_RANGE_START: int = 8000
DEFAULT_PORT_RANGE_END: int = 9000


#
# PUBLIC
#
def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available for binding.

    Args:
        port: Port number to check.
        host: Host address to check on.

    Returns:
        True if port is available, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.bind((host, port))
            return True
    except (OSError, socket.error):
        return False


def find_available_port(start_port: int = DEFAULT_PORT_RANGE_START,
                       end_port: int = DEFAULT_PORT_RANGE_END,
                       host: str = "127.0.0.1") -> Optional[int]:
    """Find an available port in the specified range.

    Args:
        start_port: Starting port number to check.
        end_port: Ending port number to check.
        host: Host address to check on.

    Returns:
        Available port number, or None if no ports available in range.
    """
    for port in range(start_port, end_port + 1):
        if is_port_available(port, host):
            return port
    return None


def get_port_from_config_or_auto(config: dict,
                                specified_port: Optional[int] = None,
                                host: str = "127.0.0.1") -> tuple[int, str]:
    """Get port from config or automatically select one.

    Port selection priority:
    1. Use specified_port if provided and available
    2. Use port from config if available
    3. Auto-select an available port

    Args:
        config: Configuration dictionary that may contain 'port'.
        specified_port: Port specified via command line flag.
        host: Host address to check port availability on.

    Returns:
        Tuple of (port_number, status_message).
        status_message is empty string if successful, error message otherwise.
    """
    # Priority 1: Use specified port if provided
    if specified_port is not None:
        if is_port_available(specified_port, host):
            return specified_port, ""
        else:
            return 0, f"Port {specified_port} is already in use. Please choose a different port or remove the --port flag."

    # Priority 2: Use port from config if specified
    config_port = config.get("port")
    if config_port is not None:
        if is_port_available(config_port, host):
            return config_port, ""
        else:
            # Config port is taken, auto-select
            auto_port = find_available_port(host=host)
            if auto_port is not None:
                return auto_port, f"Config port {config_port} is in use. Auto-selected port {auto_port}."
            else:
                return 0, f"Config port {config_port} is in use and no available ports found in range {DEFAULT_PORT_RANGE_START}-{DEFAULT_PORT_RANGE_END}."

    # Priority 3: Auto-select an available port
    auto_port = find_available_port(host=host)
    if auto_port is not None:
        return auto_port, f"Auto-selected port {auto_port}."
    else:
        return 0, f"No available ports found in range {DEFAULT_PORT_RANGE_START}-{DEFAULT_PORT_RANGE_END}."