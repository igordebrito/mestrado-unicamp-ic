import paho.mqtt.client as mqtt
import datetime
import requests
import psutil
from gpiozero import CPUTemperature

API_WRITE_KEY = '[REPLACE WITH THINGSBOARD API WRITE KEY]'
ADDR = '[REPLACE WITH THINGSBOARD SERVER IP]'
PORT = '[REPLACE WITH THINGSBOARD PORT]'
SERVER_URL = f'http://{ADDR}:{PORT}/api/v1/{API_WRITE_KEY}/telemetry'
HEADERS = {
    'Content-Type':'application/json'
}

PC_IP = '[REPLACE WITH PC IP]'
cpu = CPUTemperature()
LOGFILE_BASE = f'scalability_log_{datetime.datetime.now().date()}_'
current_logfile = LOGFILE_BASE

def send_to_server(message):
    dp = {
        'topic': message.topic,
        'payload': message.payload
    }

    response = requests.post(SERVER_URL, headers=HEADERS, data=str(dp))

# Called when connects to MQTT server
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('test/#') # Subscribes to all "test" topics
    client.subscribe('control/#') # Subscribes to all "control" topics

# Called every time a message is received
def on_message(client, userdata, message):
    global current_logfile 
    if message.topic == 'control/start':
        current_logfile = LOGFILE_BASE + f'{message.payload}mps.csv'
        try:
            log = open(current_logfile, "x")
            print(f'Log file does not exist, creating {current_logfile}')
            log.write("RECEIVED,SENT,TOPIC,MESSAGE,CPU,RAM,TEMPERATURE\n")
            log.close()
        except FileExistsError:
            print(f'Log file {current_logfile} already exists')
    elif message.topic == 'control/stop':
        pass
    else:
        received = datetime.datetime.now()
        send_to_server(message)
        finished = datetime.datetime.now()
        
        print(f"{received}  Received message '{str(message.payload)}' on topic '{message.topic}'")
        log = open(current_logfile, "a")
        log.write(f"{received},{finished},{message.topic},{str(message.payload)},{psutil.cpu_percent()},{psutil.virtual_memory().used/1048576},{cpu.temperature}\n")
        log.close()

def main():
    psutil.cpu_percent() # Needs to be called a first time

    # Connects to the MQTT broker
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect('localhost', 1883, 60)  # MQTT broker is also running on the gateway
    mqtt_client.loop_forever()

if __name__ == '__main__':
    main()
 