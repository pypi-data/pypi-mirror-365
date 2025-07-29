import os
import sys
import socket
import re
import urllib.parse

from .utils import is_port_in_use
from typing import Any, Union

def backend_validation(backend: str) -> None:
    """
    Validate the backend type.

    Args:
        backend (str): The backend type to validate.

    Raises:
        ValueError: If the backend is not supported.
    """
    supported_backends = ["zmq", "redis", "kafka"]
    if backend not in supported_backends:
        raise ValueError(f"Unsupported backend: {backend}. Supported backends are {supported_backends}.")


def network_validation(address, port, protocol):
    """
    Validate the network address, port, and protocol.

    Args:
        address (str): The network address.
        port (int): The port number.
        protocol (str): The protocol to use ('tcp', 'ipc', 'inproc').

    Raises:
        ValueError: If the address, port, or protocol is invalid.
    """
    if not re.match(r'^[a-zA-Z0-9_.-.*]+$', address):
        raise ValueError("Invalid socket address. Only alphanumeric characters, underscores, hyphens and asterisk are allowed.")
    if not (1 <= port <= 65535):
        raise ValueError("Socket port must be between 1 and 65535.")
    if protocol not in ["tcp", "ipc", "inproc"]:
        raise ValueError("Invalid protocol. Supported protocols are 'tcp', 'ipc', and 'inproc'.")

    if protocol == "ipc":
        if sys.platform.startswith("win"):
            raise RuntimeError("IPC is not supported on Windows. Use TCP instead.")
        if not os.path.exists(address):
            raise ValueError(f"IPC address {address} does not exist. Ensure the path is correct.")
        if not os.access(address, os.W_OK):
            raise ValueError(f"IPC address {address} is not writable. Check permissions.")

