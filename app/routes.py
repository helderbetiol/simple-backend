from app import app
import flask
import socket
from dotenv import load_dotenv
import os
import json
from app.mqtt import publish

load_dotenv()
PROCESS_ID = int(os.environ['MY_PID'])
MAX_PID = int(os.environ['MAX_PID'])
PROCESS_CLOCK = 0
print(f"-> Process {PROCESS_ID} started with clock {PROCESS_CLOCK}")

# mutual exclusion
ACCESS_STATE = 0 # 0 = no access, 1 = has access, 2 = wants access
ACCESS_QUEUE = []
ACCESS_GRANT_COUNT = 0 # must be MAX_PID to get access

@app.route('/')
@app.route('/index')
def index():
    return f"Hello, World! My IP is {socket.gethostbyname(socket.gethostname())}"

# Regular Lamport clock

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

@app.route('/lamport/status', methods=['GET'])
def lamport_get_status():
    return flask.jsonify({'PID': PROCESS_ID, 'CLOCK': PROCESS_CLOCK, 'ACCESS_STATE': ACCESS_STATE}), 200

# Receive event, callback from mqtt subscribe
def lamport_receive_event(string_data):
    global PROCESS_CLOCK
    data = json.loads(string_data)

    if data['resource'] == 'critical':
        manage_critical_response(data)
        msg = f"Critical message received"
    elif data['destination_id'] == PROCESS_ID:
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

# Mutual Exclusion

@app.route('/lamport/critical', methods=['POST'])
def lamport_critical_access():
    global PROCESS_CLOCK
    global ACCESS_STATE
    # get expected json body
    data = flask.request.get_json()
    if not data['destination_id']:
        return "Invalid data", 400

    # update clock
    PROCESS_CLOCK += 1 

    if ACCESS_STATE == 0: # no access, request permission to all to access 
        send_data = {'sender_id': PROCESS_ID, 'resource': 'critical', 'clock': PROCESS_CLOCK , 'status': 'request'}
        publish(json.dumps(send_data))
        msg = f"Critial access REQUESTED. Local clock is now {PROCESS_CLOCK}"
        ACCESS_STATE = 2 # wants access
    else: # wants or has access, switch to no access 
        unqueue_access()
        ACCESS_STATE = 0
        msg = f"Switched critical state to NO ACCESS. Local clock is now {PROCESS_CLOCK}"
    msg = f"[EVENT {PROCESS_ID}.{PROCESS_CLOCK}] " + msg
    print(msg)
    return msg

def manage_critical_response(data):
    global ACCESS_STATE
    global ACCESS_QUEUE
    global ACCESS_GRANT_COUNT
    if data['status'] == 'OK': # received a response
        if data['destination_id'] == PROCESS_ID: # and it is for me
            print(f"Got OK to access from {data['sender_id']}")
            ACCESS_GRANT_COUNT +=1
            if ACCESS_GRANT_COUNT == MAX_PID: # got the access
                ACCESS_STATE = 1 # has access
                print(f"Got the access!")

    else: # received a request
        send_ok = {'sender_id': PROCESS_ID, 'destination_id': data['sender_id'], 'resource': 'critical', 'status': 'OK'}
        if ACCESS_STATE == 0: # no access
            publish(json.dumps(send_ok)) # send OK
            print(f"Sent OK to access to {data['sender_id']}")

        elif ACCESS_STATE == 1: # has access
            ACCESS_QUEUE.append(data['sender_id']) #queue
            print(f"Queued access request from {data['sender_id']}")

        else: # wants access
            if PROCESS_ID == data['sender_id']: # myself
                ACCESS_GRANT_COUNT +=1
                print(f"Received access request from myself. Granted")
                if ACCESS_GRANT_COUNT == MAX_PID: # got the access
                    ACCESS_STATE = 1 # has access
                    print(f"Got the access!")
            elif PROCESS_CLOCK > data['clock']: # lost, let the other process access first
                publish(json.dumps(send_ok))
                print(f"Sent OK to access to {data['sender_id']}")
            else: # won, queue the other one
                ACCESS_QUEUE.append(data['sender_id'])
                print(f"Queued access request from {data['sender_id']}")

def unqueue_access():
    global ACCESS_QUEUE
    for access_req_pid in ACCESS_QUEUE:
        send_ok = {'sender_id': PROCESS_ID, 'destination_id': access_req_pid, 'resource': 'critical', 'status': 'OK'}
        publish(json.dumps(send_ok))
        print(f"OK message to PID {access_req_pid} unqueued")
    ACCESS_QUEUE = []
