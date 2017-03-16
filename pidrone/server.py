import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template
from pyMultuiWii import MultiWii

from pyMultiwii import MultiWii
from sys import stdout



sio = socketio.Server()
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')

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

if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)
    board = MultiWii("/dev/ttyUSB0")
    try:
        board.getData(MultiWii.ATTITUDE)
        print board.attitude
    except Exception,error:
        print("Error on Main: "+str(error))
    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
