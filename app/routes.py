from app import app
import flask
import socket
from dotenv import load_dotenv
import os
import json
from app.mqtt import publish

load_dotenv()
PROCESS_ID = int(os.environ['MY_PID'])
PROCESS_CLOCK = 0
print(f"-> Process {PROCESS_ID} started with clock {PROCESS_CLOCK}")

@app.route('/')
@app.route('/index')
def index():
    return f"Hello, World! My IP is {socket.gethostbyname(socket.gethostname())}"

@app.route('/lamport/send', methods=['POST'])
def lamport_send_event():
    global PROCESS_CLOCK
    # get expected json body
    data = flask.request.get_json()
    if not data['destination_id']:
        return "Invalid data", 400

    # update clock
    PROCESS_CLOCK += 1

    # check if it is local event
    if data['destination_id'] == PROCESS_ID:
        msg = f"Local event. Local clock is now {PROCESS_CLOCK}"
    else:
        # send data
        send_data = {'sender_id': PROCESS_ID, 'destination_id': data['destination_id'], 'clock': PROCESS_CLOCK}
        publish(json.dumps(send_data))
        msg = f"Message SENT. Local clock is now {PROCESS_CLOCK}"
    msg = f"[EVENT {PROCESS_ID}.{PROCESS_CLOCK}] " + msg
    print(msg)
    return msg

def lamport_receive_event(string_data):
    global PROCESS_CLOCK
    data = json.loads(string_data)
    if data['destination_id'] == PROCESS_ID:
        # update clock
        if data['clock'] > PROCESS_CLOCK:
            PROCESS_CLOCK = data['clock']
        PROCESS_CLOCK += 1
        msg = f"Message ACCEPTED from {data['sender_id']} with EVENT {data['sender_id']}.{data['clock']}. Local clock is now {PROCESS_CLOCK}"
    else:
        msg = f"Message IGNORED from {data['sender_id']} to {data['destination_id']}. Local clock is still {PROCESS_CLOCK}"
    msg = f"[EVENT {PROCESS_ID}.{PROCESS_CLOCK}] " + msg
    print(msg)
    return msg

@app.route('/lamport/status', methods=['GET'])
def lamport_get_status():
    return flask.jsonify({'PID': PROCESS_ID, 'CLOCK': PROCESS_CLOCK}), 200
