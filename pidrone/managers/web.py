import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, render_template
from pyMultuiWii import MultiWii

from pyMultiwii import MultiWii
from sys import stdout

class WebManager(Manager):
    """docstring for WebManager."""
    def __init__(self, arg):
        super(WebManager, self).__init__()
        self.arg = arg
    def start():
        eventlet.wsgi.server(eventlet.listen(('', 80)), app)

sio = socketio.Server()
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the client-side application."""
    return render_template('index.html')
