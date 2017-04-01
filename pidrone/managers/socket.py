import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template
from sys import stdout

mgr = socketio.RedisManager('redis://')
sio = socketio.Server(client_manager=mgr)
app = Flask(__name__)
board = MultiWii("/dev/ttyUSB0")

@sio.on('connect', namespace='/chat')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('chat message', namespace='/chat')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', room=sid)

@sio.on('disconnect', namespace='/chat')
def disconnect(sid):
    print('disconnect ', sid)


def run():
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)


class SocketManager(Manager):
    """docstring for SocketManager."""
    def __init__(self, arg):
        super(SocketManager, self).__init__()
        self.arg = arg
    def start():
        # wrap Flask application with engineio's middleware
