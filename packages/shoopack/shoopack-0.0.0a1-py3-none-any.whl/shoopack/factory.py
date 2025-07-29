from .base import *

def create_publisher(backend: str, **kwargs) -> PublisherBase:
    """
    Create a publisher instance based on the specified backend.

    Parameters:
        backend (str): The backend type to use (e.g., 'zmq').

    Keyword Args (**kwargs):
        address (str): The address to bind the publisher socket.
        port (int): The port to bind the publisher socket.
        protocol (str): Protocol to use (default: "tcp").
        topic_name (str): Topic name to publish messages under (default: "default_topic").
        connect (bool): Whether to connect to a subscriber (default: False, which means bind).
        chunk_size (int): Size of each chunk for audio data (default: 1024).

    Returns:
        PublisherBase: An initialized publisher instance.
    """
    if backend == "zmq":
        from .impl.zmq.pubsub import ZmqPublisher
        return ZmqPublisher(**kwargs)
    else:
        raise ValueError(f"Unsupported publisher backend: {backend}")

def create_subscriber(backend: str, **kwargs) -> SubscriberBase:
    """
    Create a subscriber instance based on the specified backend.

    Parameters:
        backend (str): The backend type to use (e.g., 'zmq').

    Keyword Args (**kwargs):
        address (str): The address to connect the subscriber socket.
        port (int): The port to connect the subscriber socket.
        protocol (str): Protocol to use (default: "tcp").
        topic_name (str): Topic name to subscribe to (default: "default_topic").
        connect (bool): Whether to connect to a publisher (default: True).
        chunk_size (int): Size of each chunk for audio data (default: 1024).
        timeout (int): Timeout for subscriber socket in milliseconds (default: 500).

    Returns:
        SubscriberBase: An initialized subscriber instance.
    """
    if backend == "zmq":
        from .impl.zmq.pubsub import ZmqSubscriber
        return ZmqSubscriber(**kwargs)
    else:
        raise ValueError(f"Unsupported subscriber backend: {backend}")

def create_pairing_pubsub(backend: str, **kwargs) -> PairingPubSubBase:
    """
    Create a pairing pub/sub instance based on the specified backend.

    Parameters:
        backend (str): The backend type to use (e.g., 'zmq').

    Keyword Args (**kwargs):
        target_address (str): The address to bind the publisher socket.
        target_port (int): The port to bind the publisher socket.
        source_address (str): The address to connect the subscriber socket.
        source_port (int): The port to connect the subscriber socket.
        source_timeout (int): Timeout for subscriber socket in milliseconds (default: 500).
        protocol (str): Protocol to use (default: "tcp").
        topic_name (str): Topic name to subscribe/publish (default: "default_topic").

    Returns:
        PairingPubSubBase: An initialized pairing pub/sub instance.
    """
    if backend == "zmq":
        from .impl.zmq.pubsub import ZmqPairingPubSub
        return ZmqPairingPubSub(**kwargs)
    else:
        raise ValueError(f"Unsupported pairing pub/sub backend: {backend}")

def create_requester(backend: str, **kwargs) -> RequesterBase:
    if backend == "zmq":
        from .impl.zmq.reqres import ZmqRequester
        return ZmqRequester(**kwargs)
    else:
        raise ValueError(f"Unsupported requester backend: {backend}")

def create_responder(backend: str, **kwargs) -> ResponderBase:
    if backend == "zmq":
        from .impl.zmq.reqres import ZmqResponder
        return ZmqResponder(**kwargs)
    else:
        raise ValueError(f"Unsupported responder backend: {backend}")

def create_client(backend: str, **kwargs):
    return create_requester(backend, **kwargs)

def create_server(backend: str, **kwargs):
    return create_responder(backend, **kwargs)