import paho.mqtt.client as mqtt
import datetime

# Called when connects to MQTT server
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('/+/light/#') # Subscribes to all "light" topics

# Called every time a message is received
def on_message(client, userdata, message):
    print(f"{datetime.datetime.now()}  Received message '{str(message.payload)}' on topic '{message.topic}'")

    log = open("gateway_log.csv", "a")
    log.write(f"{datetime.datetime.now()},{message.topic},{str(message.payload)}\n")
    log.close()

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