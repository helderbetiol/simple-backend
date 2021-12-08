from paho.mqtt import client as mqtt_client

import random
import time
import os

import app.routes as routes
import app.bully as bully

broker = 'broker.emqx.io'
port = 1883
topic = "distribuidos/#"
lamport_topic = "distribuidos/lamport"
bully_topic = "distribuidos/bully"
PROCESS_ID = os.environ['MY_PID']
client_id = f'distribuidos-client-{PROCESS_ID}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    global client
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(msg, topic=lamport_topic):
    global client
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic}")

def subscribe():
    global client
    def on_lamport_message(client, userdata, msg):
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        routes.lamport_receive_event(msg.payload.decode())
    def on_bully_message(client, userdata, msg):
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        bully.bully_receive_event(msg.payload.decode())
    client.message_callback_add(lamport_topic, on_lamport_message)
    client.message_callback_add(bully_topic, on_bully_message)
    client.subscribe(topic)

client = connect_mqtt()
subscribe()
client.loop_start()