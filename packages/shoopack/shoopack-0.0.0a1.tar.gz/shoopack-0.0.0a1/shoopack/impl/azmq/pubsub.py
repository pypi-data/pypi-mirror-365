from ...base import PublisherBase, SubscriberBase
import zmq


class ZmqPublisher(PublisherBase):
    def __init__(self, topic: str = ""):
        pass

    def publish(self, message):
        pass


class ZmqSubscriber(SubscriberBase):
    def __init__(self, topic: str = ""):
        pass

    def listen(self, callback):
        pass

