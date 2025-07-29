from abc import ABC, abstractmethod
from typing import Callable, Any, Union


# ===== Pub/Sub Interface =====

class PublisherBase(ABC):
    @abstractmethod
    def publish(self, message: Any) -> None:
        """Send a message to subscribers."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the publisher."""
        raise NotImplementedError


class SubscriberBase(ABC):
    @abstractmethod
    def receive(self, ignore_timeout: bool = True) -> Union[str, bytes, dict, list, None]:
        """Receive a message from the publisher."""
        raise NotImplementedError

    @abstractmethod
    def listen(self, **kwargs) -> None:
        """Start listening for messages."""
        raise NotImplementedError

    @abstractmethod
    def get(self) -> Any:
        """Get the last received message."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the subscriber."""
        raise NotImplementedError

class PairingPubSubBase(ABC):
    @abstractmethod
    def publish(self, message: Any) -> None:
        """Send a message to the peer."""
        raise NotImplementedError

    @abstractmethod
    def receive(self, ignore_timeout: bool = True) -> Any:
        """Receive a message from the peer."""
        raise NotImplementedError

    @abstractmethod
    def listen(self, **kwargs) -> None:
        """Start listening for messages."""
        raise NotImplementedError

    @abstractmethod
    def get(self) -> Any:
        """Get the last received message."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the pairing pub/sub."""
        raise NotImplementedError


# ===== Req/Res Interface =====

class RequesterBase(ABC):
    @abstractmethod
    def send(self, message: Any) -> Any:
        """Send a request and return the response."""
        raise NotImplementedError

    @abstractmethod
    def receive(self) -> None:
        """Receive a response from the server."""
        raise NotImplementedError


class ResponderBase(ABC):
    @abstractmethod
    def receive(self) -> None:
        """"""
        raise NotImplementedError

    @abstractmethod
    def send(self, message):
        raise NotImplementedError

