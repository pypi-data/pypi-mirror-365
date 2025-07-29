from ...base import PublisherBase, SubscriberBase, PairingPubSubBase
from ...validator import network_validation
import zmq
import json

from typing import Any, Union, Callable, Optional


def _typed_multipart_message(message: Union[str, bytes, dict, list], topic_name: str, chunk_size=1024) -> list:
    """
    Create a multipart message with the topic prefix.
    :param message: The message to be sent.
    :param topic_name: The topic name to prefix the message.
    :param chunk_size: The size of each chunk for audio data.
    :return: A list representing the multipart message.
    """
    parts = [topic_name.encode('utf-8')]
    if isinstance(message, str):
        parts.append("type=str".encode('utf-8'))
        b_msg = message.encode('utf-8')
    elif isinstance(message, bytes):
        parts.append("type=bytes".encode('utf-8'))
        b_msg = message
    elif isinstance(message, (dict, list)):
        parts.append("type=json".encode('utf-8'))
        b_msg = json.dumps(message).encode('utf-8')
    else:
        raise TypeError("Unsupported message type. Must be str, bytes, dict, or list.")

    for i in range(0, len(b_msg), chunk_size):
        chunk = b_msg[i:i + chunk_size]
        parts.append(chunk)
    return parts


def _read_typed_multipart_message(message: list, topic_name: str) -> Union[str, bytes, dict, list]:
    """
    Read a multipart message and return the original message type.
    :param message: The multipart message received.
    :param topic_name: The topic name to check against the message.
    :return: The original message in its respective type.
    """
    if not isinstance(message, list) or len(message) < 2:
        raise ValueError("Invalid multipart message format.")

    if message[0].decode('utf-8') != topic_name:
        raise ValueError(f"Topic name mismatch: expected '{topic_name}', got '{message[0].decode('utf-8')}'.")

    header = message[1].decode('utf-8')
    if not header.startswith("type="):
        raise ValueError("Invalid message header. Expected 'type=' prefix, got: {}".format(header))

    msg_type = message[1].decode('utf-8').split('=')[1]

    b_msgs = message[2:]
    if msg_type == "str":
        return b''.join(b_msgs).decode('utf-8')
    elif msg_type == "bytes":
        return b''.join(b_msgs)
    elif msg_type == "json":
        return json.loads(b''.join(b_msgs).decode('utf-8'))


class ZmqPublisher(PublisherBase):

    def __init__(
        self,
        address: str,
        port: int = 5555,
        protocol: str = "tcp",
        topic_name: str = "default_topic",
        connect: bool = False,
        chunk_size: int = 1024,
    ):
        """
        Initialize a ZeroMQ publisher.
        This publisher can either connect to a subscriber or bind to a socket.

        :param address: The address to connect to or bind the publisher socket.
        :param port: The port to connect to or bind the publisher socket.
        :param protocol: The protocol to use (default is "tcp").
        :param topic_name: The topic name to publish messages under (default is "default_topic").
        :param connect: Whether to connect to the subscriber (default is False, which means bind).
        :param chunk_size: The size of each chunk for audio data (default is 1024).
        """
        self.socket_addr = f"{protocol}://{address}:{port}"
        self.topic_name = topic_name
        self.chunk_size = chunk_size

        self.connect = connect

        # Validate address and port
        network_validation(address, port, protocol)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)

        if connect:
            self.socket.connect(self.socket_addr)
        else:
            self.socket.bind(self.socket_addr)


    def __repr__(self):
        s = "ZmqPublisher(socket_addr={}, topic_name={}, connect={}, chunk_size={})".format(
           self.socket_addr,  self.topic_name, self.connect, self.chunk_size
        )
        return s

    def __str__(self):
        return str(self.__repr__())


    def publish(self, message: Any):
        """
        Publish a message with the appropriate method based on its type.
        """
        b_msg = _typed_multipart_message(message, self.topic_name, self.chunk_size)
        self.socket.send_multipart(b_msg)

    def close(self):
        """
        Close the publisher socket.
        """
        self.socket.close()
        self.context.term()


class ZmqSubscriber(SubscriberBase):

    def __init__(
        self,
        address: str,
        port: int = 5555,
        protocol: str = "tcp",
        topic_name: str = "default_topic",
        connect: bool = True,
        chunk_size: int = 1024,
        timeout: int = 500,  # in milliseconds
    ):
        """
        Initialize a ZeroMQ subscriber.
        This subscriber connects to a publisher and subscribes to a specific topic.

        :param address: The address to connect to or bind the subscriber socket.
        :param port: The port to connect to or bind the subscriber socket.
        :param protocol: The protocol to use (default is "tcp").
        :param topic_name: The topic name to subscribe to (default is "default_topic").
        :param connect: Whether to connect to the publisher (default is True).
        :param chunk_size: The size of each chunk for audio data (default is 1024).
        :param timeout: The timeout for receiving messages in milliseconds (default is 500).
        """
        self.socket_addr = f"{protocol}://{address}:{port}"
        self.topic_name = topic_name
        self.chunk_size = chunk_size
        self.connect = connect
        self.timeout = timeout

        # Validate address and port
        network_validation(address, port, protocol)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        if connect:
            self.socket.connect(self.socket_addr)
        else:
            self.socket.bind(self.socket_addr)

        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, f"{self.topic_name}")

        import queue
        self._listen_thread = None
        self._listen_loop = False
        self._listen_queue = queue.Queue()


    def __repr__(self):
        s = "ZmqSubscriber(socket_addr={}, topic_name={}, connect={}, chunk_size={})".format(
           self.socket_addr,  self.topic_name, self.connect, self.chunk_size
        )
        return s

    def __str__(self):
        return str(self.__repr__())


    def receive(self, ignore_timeout: bool = True) -> Union[str, bytes, dict, list, None]:
        """
        Receive a message from the socket.
        It will be BLOCKING until a message is received or the timeout is reached.

        :param ignore_timeout: If True, will return None instead of raising a TimeoutError.

        Returns:
            str, bytes, dict, or list: The received message.
        """
        try:
            message = self.socket.recv_multipart()
            return _read_typed_multipart_message(message, self.topic_name)
        except zmq.Again:
            if ignore_timeout:
                return None
            else:
                raise TimeoutError("No message received within the timeout period.")
        except ValueError as e:
            raise ValueError(f"Failed to read message: {e}")

    def _listen_loop_with_callback(self, callback: Callable, ignore_timeout: bool = True) -> None:
        """
        Listen for messages and call the provided callback with each received message.
        This method runs in a separate thread.

        :param callback: Callable function to process received messages.
                         It will be called with each received message.
        :param ignore_timeout: If True, will ignore timeout errors and return None instead of raising an exception.
        """
        while self._listen_loop:
            try:
                message = self.receive(ignore_timeout=ignore_timeout)
                if message is not None:
                    callback(message)
            except TimeoutError:
                if not ignore_timeout:
                    raise
            except Exception as e:
                print(f"Error in listen loop with callback: {e}")

    def _listen_loop_queue(self, ignore_timeout: bool = True) -> None:
        """
        Listen for messages and put them into the listen queue.
        This method runs in a separate thread.

        :param ignore_timeout: If True, will ignore timeout errors and return None instead of raising an exception.
        """
        while self._listen_loop:
            try:
                message = self.receive(ignore_timeout=ignore_timeout)
                if message is not None:
                    self._listen_queue.put(message)
            except TimeoutError:
                if not ignore_timeout:
                    raise
            except Exception as e:
                print(f"Error in listen loop: {e}")

    def listen(self, callback: Optional[Callable] = None,
               ignore_timeout: bool = True) -> None:

        """
        Start listening for messages and put them into a queue.
        If a callback is provided, it will be called with each received message.
        else, messages will be put into the listen queue, listen thread will be started.
        and you can retrieve messages from the queue.


        :param callback: Callable function to process received messages.
                        If provided, it will be called with each received message.
                        (e.g., callback(message))
        :param ignore_timeout: If True, will ignore timeout errors and return None instead of raising an exception.

        """
        import threading
        if callback:
            self._listen_loop = True
            self._listen_thread = threading.Thread(
                target=self._listen_loop_with_callback, args=(callback, ignore_timeout)
            )
            self._listen_thread.start()
        else:
            self._listen_loop = True
            self._listen_thread = threading.Thread(target=self._listen_loop_queue, args=(ignore_timeout,))
            self._listen_thread.start()

    def get(self):
        """
        Get a message from the listen queue.
        This method will block until a message is available.

        :return: The next message from the listen queue.
        """
        if not self._listen_loop:
            raise RuntimeError("Listen loop is not running. Call listen() first.")
        if not self._listen_queue.empty():
            return self._listen_queue.get()
        else:
            return None

    def close(self):
        """
        Close the subscriber socket.
        """
        self._listen_loop = False
        if self._listen_thread:
            self._listen_thread.join()
        self.socket.close()
        self.context.term()


class ZmqPairingPubSub(PairingPubSubBase):

    def __init__(
        self,
        target_address: str,
        target_port: int = 5555,
        source_address: str = "localhost",
        source_port: int = 5556,
        source_timeout: int = 500,  # in milliseconds
        protocol: str = "tcp",
        topic_name: str = "default_topic",
        chunk_size: int = 1024,

    ):
        """
        Initialize a ZeroMQ PUB/SUB pairing for communication.

        :param target_address: The address to bind the publisher socket.
        :param target_port: The port to bind the publisher socket.
        :param source_address: The address to connect the subscriber socket.
        :param source_port: The port to connect the subscriber socket.
        :param source_timeout: The timeout for the subscriber socket (default is 500 ms).
        :param protocol: The protocol to use (default is "tcp").
        :param topic_name: The topic name to connection (default is "default_topic").
        """
        self.target_socket_addr = f"{protocol}://{target_address}:{target_port}"
        self.source_socket_addr = f"{protocol}://{source_address}:{source_port}"
        self.topic_name = topic_name

        # Validate addresses and ports
        network_validation(target_address, target_port, protocol)
        network_validation(source_address, source_port, protocol)

        self.context = zmq.Context()
        self.target_socket = self.context.socket(zmq.PUB)
        self.source_socket = self.context.socket(zmq.SUB)

        self.target_socket.bind(self.target_socket_addr)

        self.source_socket.connect(self.source_socket_addr)
        self.source_socket.setsockopt(zmq.RCVTIMEO, source_timeout)
        self.source_socket.setsockopt_string(zmq.SUBSCRIBE, f"{self.topic_name}")
        self.chunk_size = chunk_size

        # Listen for incoming messages
        import queue
        self._listen_thread = None
        self._listen_loop = False
        self._listen_queue = queue.Queue()


    def __repr__(self):
        s = "ZmqPairingPubSub(target_socket_addr={}, source_socket_addr={}, topic_name={})".format(
            self.target_socket_addr, self.source_socket_addr, self.topic_name
        )
        return s

    def __str__(self):
        return str(self.__repr__())


    def publish(self, message: Any) -> None:
        """
        Publish a message to the target socket with the topic prefix.

        :param message: The message to publish.
        """
        b_msg = _typed_multipart_message(message, self.topic_name, self.chunk_size)
        self.target_socket.send_multipart(b_msg)

    def receive(self, ignore_timeout: bool = True) -> Union[str, bytes, dict, list, None]:
        """
        Receive a message from the source socket.
        It will be BLOCKING until a message is received or the timeout is reached.

        :param ignore_timeout: If True, will return None instead of raising a TimeoutError.
        :return:
        """
        try:
            message = self.source_socket.recv_multipart()
            return _read_typed_multipart_message(message, self.topic_name)
        except zmq.Again:
            if ignore_timeout:
                return None
            else:
                raise TimeoutError("No message received within the timeout period.")
        except ValueError as e:
            raise ValueError(f"Failed to read message: {e}")

    def _listen_loop_with_callback(self, callback: Callable, ignore_timeout: bool = True) -> None:
        """
        Listen for messages and call the provided callback with each received message.
        This method runs in a separate thread.

        :param callback: Callable function to process received messages.
                         It will be called with each received message.
        :param ignore_timeout: If True, will ignore timeout errors and return None instead of raising an exception.
        """
        while self._listen_loop:
            try:
                message = self.receive(ignore_timeout=ignore_timeout)
                if message is not None:
                    callback(message)
            except TimeoutError:
                if not ignore_timeout:
                    raise
            except Exception as e:
                print(f"Error in listen loop with callback: {e}")

    def _listen_loop_queue(self, ignore_timeout: bool = True) -> None:
        """
        Listen for messages and put them into the listen queue.
        This method runs in a separate thread.

        :param ignore_timeout: If True, will ignore timeout errors and return None instead of raising an exception.
        """
        while self._listen_loop:
            try:
                message = self.receive(ignore_timeout=ignore_timeout)
                if message is not None:
                    self._listen_queue.put(message)
            except TimeoutError:
                if not ignore_timeout:
                    raise
            except Exception as e:
                print(f"Error in listen loop: {e}")


    def listen(self, callback: Optional[Callable] = None,
               ignore_timeout: bool = True) -> None:

        """
        Start listening for messages and put them into a queue.
        If a callback is provided, it will be called with each received message.
        else, messages will be put into the listen queue, listen thread will be started.
        and you can retrieve messages from the queue.


        :param callback: Callable function to process received messages.
                        If provided, it will be called with each received message.
                        (e.g., callback(message))
        :param ignore_timeout: If True, will ignore timeout errors and return None instead of raising an exception.

        """
        import threading
        if callback:
            self._listen_loop = True
            self._listen_thread = threading.Thread(
                target=self._listen_loop_with_callback, args=(callback, ignore_timeout)
            )
            self._listen_thread.start()
        else:
            self._listen_loop = True
            self._listen_thread = threading.Thread(
                target=self._listen_loop_queue, args=(ignore_timeout,),
            )
            self._listen_thread.start()

    def get(self):
        """
        Get a message from the listen queue.
        This method will block until a message is available.

        :return: The next message from the listen queue.
        """
        if not self._listen_loop:
            raise RuntimeError("Listen loop is not running. Call listen() first.")
        if not self._listen_queue.empty():
            return self._listen_queue.get()
        else:
            return None

    def close(self):
        """
        Close the publisher and subscriber sockets.
        """
        self._listen_loop = False
        if self._listen_thread:
            self._listen_thread.join()
        self.target_socket.close()
        self.source_socket.close()
        self.context.term()