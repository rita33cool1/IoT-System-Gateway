import os
import sys
import cv2
import wget
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("iot/iscc19/image/yolo5/image")

def on_message(client, userdata, msg):
    f = open('yolo5.jpg','w')
    f.write(msg.payload)
    f.close()
    print 'img received'
    yolo()
    time.sleep(2)

if __name__ == '__main__':
    # Debug and See the output
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(os.environ['BROKER'], 1883, 60)
    client.loop_forever()
