import zmq
import time
import json
import re

from typing import Any, Union
from pydantic import BaseModel

class ZMQPublisher:

    def __init__(
        self,
        socket_addr: str = "localhost",
        socket_port: int = 5555,
        protocol: str = "tcp",
        topic: str = "default_topic",
        connect: bool = True,
        chunk_size: int = 1024
    ):
        """
        Initialize the ZMQPublisher.
        :param socket_addr:
        :param topic:
        :param connect:
        :param chunk_size:
        """
        self.socket_addr = f"{protocol}://{socket_addr}:{socket_port}"
        # check addr is correct:
        if not re.match(r'^[a-zA-Z0-9_.-]+$', socket_addr):
            raise ValueError("Invalid socket address. Only alphanumeric characters, underscores, and hyphens are allowed.")
        if not (1 <= socket_port <= 65535):
            raise ValueError("Socket port must be between 1 and 65535.")
        if protocol not in ["tcp", "ipc", "inproc"]:
            raise ValueError("Invalid protocol. Supported protocols are 'tcp', 'ipc', and 'inproc'.")

        self.socket_type = zmq.PUB  # Use zmq.PUB for publishing messages
        self.topic = topic

        self.context = zmq.Context()

        self.socket = self.context.socket(self.socket_type)
        
        if connect:
            self.socket.connect(self.socket_addr)
        else:
            self.socket.bind(self.socket_addr)

        self.chunk_size = chunk_size


    def _pub_str(self, message: str) -> None:
        """
        Publish a string message with the topic prefix.
        """
        self.socket.send_string(f"{self.topic} {message}")

    def _pub_json(self, message: Any) -> None:
        """
        Publish a JSON-serializable message with the topic prefix.
        """

        self.socket.send_string(f"{self.topic} {json.dumps(message)}")

    def _pub_audio_chunk(self, audio_chunk: bytes) -> None:
        """
        Publish an audio chunk with the topic prefix.
        """
        if not isinstance(audio_chunk, bytes):
            raise TypeError("Audio chunk must be bytes.")
        chunks = []
        for i in range(0, len(audio_chunk), self.chunk_size):
            chunk = audio_chunk[i:i + self.chunk_size]
            chunks.append(chunk)

        # Send multipart message with topic prefix
        multipart_message = [self.topic.encode('utf-8')] + chunks
        self.socket.send_multipart(multipart_message)

    def publish(self, message: Any) -> None:
        """
        Publish a message which can be a string, dict, list, or audio chunk.
        """
        if isinstance(message, str):
            self._pub_str(message)
        elif isinstance(message, (dict, list)):
            self._pub_json(message)
        elif isinstance(message, bytes):
            self._pub_audio_chunk(message)
        else:
            raise TypeError("Unsupported message type. Must be str, dict, list, or bytes.")


class ZMQSubscriber:

    def __init__(
        self,
        socket_addr: str = "tcp://localhost:5555",
        socket_type: int = zmq.SUB,
        topic: str = "default_topic",
        connect: bool = True,
        chunk_size: int = 1024,
        message_type: type(str | bytes | dict | list) = str
    ):
        self.socket_addr = socket_addr
        self.socket_type = socket_type
        self.topic = topic
        self.context = zmq.Context()
        self.socket = self.context.socket(self.socket_type)
        if connect:
            self.socket.connect(self.socket_addr)
        else:
            self.socket.bind(self.socket_addr)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.chunk_size = chunk_size
        self.message_type = message_type



    def receive(self) -> Any:
        """
        Receive a message from the ZMQ socket.
        """
        if self.message_type == str:
            message = self.socket.recv_string()
            return message[len(self.topic) + 1:]

        elif self.message_type == bytes:
            # multipart messages
            message = self.socket.recv_multipart()
            return b''.join(message[1:])

        elif self.message_type in (dict, list):
            message = self.socket.recv_string()
            return json.loads(message[len(self.topic) + 1:])