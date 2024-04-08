import paho.mqtt.client as mqtt
import random
import datetime
import time

GATEWAY_IP = '[REPLACE WITH GATEWAY IP]'

def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.connect(GATEWAY_IP, 1883, 60)

def test_fixed_size(min_messages=45, max_messages=150, step=15, its_per_step=10, time_between_its=1.0, time_between_steps=10.0):
    for m in range(min_messages, max_messages+1, step):
        print(f'Testing for {m} messages')
        mqtt_client.publish('control/start', f'{m}')
        for it in range(its_per_step):
            for i in range(m):
                topic = f'test/{i}'
                message = str(random.randint(0, 9))
                ret = mqtt_client.publish(topic, message)
            print(f'Finished iteration {it+1}/{its_per_step} for {m} messages')
            time.sleep(time_between_its)
        print(f'Finished testing for {m} messages')
        mqtt_client.publish('control/stop', f'{m}')
        time.sleep(time_between_steps)

test_fixed_size()
