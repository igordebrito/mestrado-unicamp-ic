import paho.mqtt.client as mqtt
import requests
import datetime

API_WRITE_KEY = '[REPLACE WITH THINGSBOARD API WRITE KEY]'
ADDR = '[REPLACE WITH THINGSBOARD SERVER IP]'
PORT = '[REPLACE WITH THINGSBOARD PORT]'

BASE_URL = f'http://{ADDR}:{PORT}/api/v1/'

dp = { # Data Packet
    'red': '',
    'green': '',
    'yellow': '',
}

# Called when connects to MQTT server
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('/+/light/#') # Subscribes to all "light" topics

# Called every time a message is received
def on_message(client, userdata, message):
    print(f"{datetime.datetime.now()}  Received message '{str(message.payload)}' on topic '{message.topic}'")

    # Write to log
    log = open("gateway_log.csv", "a")
    log.write(f"{datetime.datetime.now()},{message.topic},{str(message.payload)}\n")
    log.close()

    color = message.topic[message.topic.rfind("/") + 1:]
    dp[color] = str(message.payload, 'UTF-8')
    dp[color] = dp[color].strip()
        
    # Sends all data at once
    if dp['red'] != '' and dp['green'] != '' and dp['yellow'] != '':
        url = BASE_URL + f'{API_WRITE_KEY}/telemetry'

        headers = {
            'Content-Type':'application/json'
        }
        
        response = requests.post(url, headers=headers, data=str(dp))
        print(f'{datetime.datetime.now()}  -----------------------')

        dp['red'] = ''
        dp['green'] = ''
        dp['yellow'] = ''

def main():
    try:
        log = open("gateway_log.csv", "x")
        print("Log file does not exist, creating gateway_log.csv")
        log.write("DATETIME,TOPIC,MESSAGE\n")
        log.close()
    except FileExistsError:
        print("Log file already exists")

    # Connects to the MQTT broker
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect('localhost', 1883, 60)  # MQTT broker is also running on the gateway
    mqtt_client.loop_forever()

if __name__ == '__main__':
    main()
