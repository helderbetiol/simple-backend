import os
import json
import app.mqtt as mqtt
from threading import Timer

PROCESS_ID = os.environ['MY_PID']

ELECTION_IN_PROGRESS = False 
LEADER = 0
ANSWER_COUNT = 0

def start_election(election_timer):
    global ELECTION_IN_PROGRESS, ANSWER_COUNT
    print(f"Process {PROCESS_ID} started election")
    send_data = {'sender_id': PROCESS_ID, 'message': 'election'}
    mqtt.publish(json.dumps(send_data), mqtt.bully_topic)
    ELECTION_IN_PROGRESS = True # in progress
    ANSWER_COUNT = 0
    election_timer.start()

def bully_receive_event(string_data):
    global ANSWER_COUNT, LEADER
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

        elif data['message'] == 'answer' and data['destination_id'] == PROCESS_ID: # answer for me
            print(f"Got election answer from {data['sender_id']}")
            ANSWER_COUNT += 1

        elif data['message'] == 'victory': # someone is the new leader
            print(f"Got victory message: new leader is {data['sender_id']}")
            LEADER = data['sender_id']

def election_timeout():
    global ELECTION_IN_PROGRESS
    if ANSWER_COUNT == 0: # become leader
        print("I won the election!")
        send_data = {'sender_id': PROCESS_ID, 'message': 'victory'}
        mqtt.publish(json.dumps(send_data), mqtt.bully_topic)
        LEADER = PROCESS_ID
        ELECTION_IN_PROGRESS = False

election_timer = Timer(10, election_timeout) # 10s timeout
start_election(election_timer)



