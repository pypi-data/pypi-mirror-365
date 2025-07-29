from ...base import RequesterBase, ResponderBase
import zmq

class ZmqRequester(RequesterBase):
    def __init__(self):
        pass

    def send(self, message):
        pass

class ZmqResponder(ResponderBase):
    def __init__(self):
        pass

    def listen(self, callback):
        pass