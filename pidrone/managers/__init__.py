class EventManager(object):
    """docstring for EventManager."""
    def __init__(self, pipe):
        super(EventManager, self).__init__()
        self.pipe = pipe
    def dispatch(self, event):
        self.pipe.send(event)
    def start():
        pass
    def sendToSocket():
        external_sio = socketio.KombuManager('redis://', write_only=True)
        external_sio.emit("some event", data = {}, romm="")

from .camera import CameraManager
from .socket import SocketManager
from .drone import DroneManager
