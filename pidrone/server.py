#socketio imports
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template
from pyMultuiWii import MultiWii

#picamera imports
from .camera import start_camera_server
#misc
from sys import stdout
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import time
from .helpers import *
#from flight_controller import FlightController
# register classes for sharing between processes
# toherwise stuff may go south...
# BaseManager.register('SocketioServer', socketio.Server)
# BaseManager.register("MultiWii", MultiWii)
# manager = BaseManager()
# manager.start()

sio = manager.SocketioServer()
board = manager.MultiWii("/dev/ttyUSB0")

drone_config = board.getData(board.MISC)

print("Drone config : ")
print("==================")
print(drone_config)
print(board.getData(board.IDENT))

app = Flask(__name__)

camera_handle = None
board_handle = None

board_history = []

#store the last rc channel commands
last_rc = board.rcChannels

##################################
# Background processes
# theses will be launched when the "start" command is emitted
#################################
def update_drone_info(board):
    while True:
        sio.emit("info", data = board.getData(board.ATTITUDE), namespace="/drone")
        sio.sleep(.5)

def update_rc_command(board, last_rc):
    while True:
        sendRc(last_rc)
        sio.emit("rc_raw_data", data = board.rcChannels, namespace="/drone")
        sio.emit("info", data = board.getData(board.ATTITUDE), namespace="/drone")
        time.sleep(.5)

###############################
# Flask routes
#############################
@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')

#############################
# Socket bootstraping
############################

@sio.on('connect', namespace='/')
def connect(sid, environ):
    print("connected: ",sid)

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

@sio.on("start", namespace="/drone")
def m_(*arg,**kwars):
    board.arm()
    time.sleep(2)
    thread = sio.start_background_task(update_drone_info, args = (board))
    thread_rc = sio.background_task(update_rc_command, args = (board, last_rc))
    sio.emit("ready", data={}, namespace = "/drone")

@sio.on("set_rc", namespace="/drone")
def set_rc(sid, data):
    rcIn = {"yaw":data["yaw"], "pitch":data["pitch"], "roll":data["roll"], "throttle" : data["throttle"]}
    last_rc = {**last_rc, ** rcIn}
    sendRc(last_rc)
@sio.on("set_direction", namespace = "/drone")
def set_dir(sid, data):
    rcIn = {"yaw":data["yaw"], "pitch":data["pitch"], "roll":data["roll"]}
    last_rc = {**last_rc, ** rcIn}
    sendRc(last_rc)

@sio.on("set_yaw", namespace="/drone")
def set_yaw(sid, data):
    rcIn = {"yaw":data["yaw"]}
    last_rc = {**last_rc, ** rcIn}
    sendRc(last_rc)

@sio.on("set_pitch", namespace="/drone")
def set_pitch(sid, data):
    rcIn = {"pitch":data["pitch"]}
    last_rc = {**last_rc, ** rcIn}
    sendRc(last_rc)

@sio.on("set_roll", namespace="/drone")
def set_roll(sid, data):
    rcIn = {"roll":data["roll"]}
    last_rc = {**last_rc, ** rcIn}
    sendRc(last_rc)

@sio.on("set_throttle", namespace="/drone")
def set_throttle(sid, data):
    rcIn = {"throttle":data["throttle"]}
    last_rc = {**last_rc, ** rcIn}
    sendRc(last_rc)

@sio.on("status", namespace="/drone")
def get_status(sid,data):
    pass

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
