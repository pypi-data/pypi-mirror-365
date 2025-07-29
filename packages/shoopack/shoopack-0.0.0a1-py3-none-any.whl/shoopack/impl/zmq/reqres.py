from ...base import RequesterBase, ResponderBase
from ...validator import network_validation
import zmq
import json

from typing import Any, Callable

class ZmqRequester(RequesterBase):
    def __init__(
        self,
        address: str,
        port: int = 5555,
        protocol: str = "tcp",
        connect: bool = True,
        timeout: int = 5000 # in milliseconds
    ):
        self.socket_addr = f"{protocol}://{address}:{port}"
        self.connect = connect
        self.timeout = timeout

        network_validation(address, port, protocol)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        if self.connect:
            self.socket.connect(self.socket_addr)
        else:
            self.socket.bind(self.socket_addr)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)

    def send(self, message):
        try:
            self.socket.send_json(message)
            reply = self.socket.recv_json()
            return reply
        except zmq.Again:
            raise TimeoutError("Request timed out. ({}ms)".format(self.timeout))

class ZmqResponder(ResponderBase):
    def __init__(
        self,
        address: str,
        port: int = 5555,
        protocol: str = "tcp",
        connect: bool = False,
    ):
        self.socket_addr = f"{protocol}://{address}:{port}"
        self.connect = connect

        network_validation(address, port, protocol)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        if self.connect:
            self.socket.connect(self.socket_addr)
        else:
            self.socket.bind(self.socket_addr)

        self._thread = None
        self._listen_loop = False


    def receive(self):
        """

        :return:
        """
        return self.socket.recv_json()

    def send(self, message):
        self.socket.send_json(message)