#socketio imports
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template
from pyMultuiWii import MultiWii

#picamera imports
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

#misc
from sys import stdout
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import time

# register classes for sharing between processes
# toherwise stuff may go south...
BaseManager.register('SocketioServer', socketio.Server)
BaseManager.register("MultiWii", MultiWii)
manager = BaseManager()
manager.start()

sio = manager.SocketioServer()
board = manager.MultiWii("/dev/ttyUSB0")

drone_config = board.getData(board.MISC)

print("Drone config : ")
print("==================")
print(drone_config)


PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def start_camera_server():
    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            address = ('', 6060)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()

app = Flask(__name__)

camera_handle = None
board_handle = None

board_history = []

@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')
# TODO: rename this
def f(board, sio):
    board.getData(MultiWii.ATTITUDE)
    sio.emit(board.attitude)
    time.sleep(1) # just wait a bit, don't overload everything
# when a client connects we want to:
# - start the multiwii
# - arm it
# - create a process to periodically retrive it's status and stuff
@sio.on('connect', namespace='/')
def connect(sid, environ):
    if board_handle is None:
        # first actually arm the board
        board.arm()
        board_handle = Process(target=f,args=(board, sio))
        board_handle.start()
@sio.on('disconnect', namespace='/')
def disconnect(sid):
    print('disconnect ', sid)

#################################
# drone stuff
###############################
#allow the clients to manually ask for data
@sio.on("info", namespace="/drone")
def m_(*a, **kw):
    f(board, sio)

@sio.on("set_direction", namespace = "/drone")
def set_speed(sid, data):

####################################################
# Camera stuff
################################################
# we have a special event for camera management, becuase we don't want
# to start it if there is no need

@sio.on('start', namespace='/camera')
def message(sid, data):
    camera_handle = Process(target=start_camera_server,args=()) #handle camera stuff
    camera_handle.start()
    sio.emit('started', room=sid)

@sio.on("start", namespace = "/camera")
def m_(sid, data):
    if camera_handle is not None:
        camera_handle.join() # if this doesn't work, we're f*cked
        sio.emit("stopped", room=sid)



if __name__ == '__main__':

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
