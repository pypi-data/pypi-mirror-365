import os
import socket


def is_running_in_container():
    """
    Check if the code is running inside a container (e.g., Docker, Kubernetes).

    Returns:
        bool: True if running in a container, False otherwise.
    """
    try:
        if os.path.exists('/.dockerenv'):
            return True
        if os.path.exists('/run/.containerenv'):
            return True
        with open('/proc/1/cgroup', 'r') as f:
            if any("docker" in line or "kubepods" in line for line in f):
                return True
        return False
    except Exception:
        return False


def is_port_in_use(port: int, host: str = 'localhost') -> bool:
    """
    Check if a specific port is in use on the given host.

    Args:
        port (int): The port number to check.
        host (str): The host address (default is 'localhost').

    Returns:
        bool: True if the port is in use, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((host, port))
        return result == 0


