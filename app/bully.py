import os
import json
import app.mqtt as mqtt
from threading import Timer

PROCESS_ID = os.environ['MY_PID']

ELECTION_IN_PROGRESS = False 
LEADER = 0
LEADER_HEARTBEAT_COUNT = 0
ANSWER_COUNT = 0

def start_election():
    global ELECTION_IN_PROGRESS, ANSWER_COUNT
    print(f"Process {PROCESS_ID} started election")
    send_data = {'sender_id': PROCESS_ID, 'message': 'election'}
    mqtt.publish(json.dumps(send_data), mqtt.bully_topic)
    ELECTION_IN_PROGRESS = True # in progress
    ANSWER_COUNT = 0
    election_timer.start()

def bully_receive_event(string_data):
    global ANSWER_COUNT, LEADER, LEADER_HEARTBEAT_COUNT
    data = json.loads(string_data)
    if data['sender_id'] != PROCESS_ID: # not from myself
        if data['message'] == 'election':
            if data['sender_id'] < PROCESS_ID: # answer him
                send_data = {'sender_id': PROCESS_ID, 'destination_id': data['sender_id'], 'message': 'answer'}
                mqtt.publish(json.dumps(send_data), mqtt.bully_topic)
                if LEADER != PROCESS_ID and not ELECTION_IN_PROGRESS: # check if I should be leader
                    start_election()
            else:
                print(f"Process {data['sender_id']} started election and is higher than I am, not answering")
                if ELECTION_IN_PROGRESS:
                    election_timer.cancel()

        elif data['message'] == 'answer' and data['destination_id'] == PROCESS_ID: # answer for me
            print(f"Got election answer from {data['sender_id']}")
            ANSWER_COUNT += 1

        elif data['message'] == 'victory': # someone is the new leader
            print(f"Got victory message: new leader is {data['sender_id']}")
            if LEADER == PROCESS_ID: # I was the leader
                leader_timer.cancel()
            LEADER = data['sender_id']
            check_leader_timer.start()

        elif data['message'] == 'heartbeat':
            if LEADER == data['sender_id']:
                LEADER_HEARTBEAT_COUNT += 1
                print(f"Leader {LEADER} heartbeat received")

def election_timeout():
    global ELECTION_IN_PROGRESS, LEADER
    if ANSWER_COUNT == 0: # become leader
        print("I won the election!")
        send_data = {'sender_id': PROCESS_ID, 'message': 'victory'}
        mqtt.publish(json.dumps(send_data), mqtt.bully_topic)
        LEADER = PROCESS_ID
        ELECTION_IN_PROGRESS = False
        leader_timer.start()

def leader_heartbeat(): # called when I am the leader
    print(f"Leader {LEADER} heartbeat sent")
    send_data = {'sender_id': PROCESS_ID, 'message': 'heartbeat'}
    mqtt.publish(json.dumps(send_data), mqtt.bully_topic)
    leader_timer.start()

def check_leader(): # called when I am not the leader
    global LEADER_HEARTBEAT_COUNT
    if LEADER_HEARTBEAT_COUNT == 0:
        if LEADER != PROCESS_ID:
            print(f"Leader {LEADER} not responding, start election")
            check_leader_timer.cancel()
            start_election()
        else:
            LEADER_HEARTBEAT_COUNT = 0
    else: 
        LEADER_HEARTBEAT_COUNT = 0
        check_leader_timer.start()

# the class below is from: https://stackoverflow.com/questions/22433394/calling-thread-timer-more-than-once
class RepeatableTimer(object):
    def __init__(self, interval, function, args=[], kwargs={}):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def start(self):
        t = Timer(self._interval, self._function, *self._args, **self._kwargs)
        t.start()
        self.t = t
    def cancel(self):
        self.t.cancel()

leader_timer = RepeatableTimer(10, leader_heartbeat) # 10s timeout, only when is leader
check_leader_timer = RepeatableTimer(20, check_leader) # 20s timeout, only when not leader
election_timer = RepeatableTimer(10, election_timeout) # 10s timeout, only after election message
start_election()



