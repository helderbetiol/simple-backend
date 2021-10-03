from app import app
import flask
import socket

@app.route('/')
@app.route('/index')
def index():
    return f"Hello, World! My IP is {socket.gethostbyname(socket.gethostname())}"
