import RPi.GPIO as GPIO
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import json
import os
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

myMQTTClient = AWSIoTMQTTClient("myClientID")

myMQTTClient.configureEndpoint("a2vsckvuvvwwc1-ats.iot.us-east-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/Documents/sensor_iot/certs/root-ca.pem", 
                                  "/home/pi/Documents/sensor_iot/certs/sensor_ultrasonic-private.pem.key", 
                                  "/home/pi/Documents/sensor_iot/certs/sensor_ultrasonic-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1) #Infinite Offline Publishing
myMQTTClient.configureDrainingFrequency(2) #Draining: 2Hz
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

#connect and publish
myMQTTClient.connect()

path_to_ldr = "/home/pi/Documents/backend/mqtt_client/data/ldr.txt"

delayt = 0.1
value = 0 # ldr value

ldr = 7

threshold = 10000

prev_flag = 0

def rc_time(ldr):
    count = 0

    GPIO.setup(ldr, GPIO.OUT)
    GPIO.output(ldr,False)
    time.sleep(delayt)

    GPIO.setup(ldr,GPIO.IN)

    while (GPIO.input(ldr)==0):
        count+=1
    
    return count

with open(path_to_ldr, "r") as f:
    PREV_SWITCH = f.read()

def calc_payload(value):
    global PREV_SWITCH
    if (value <= threshold):
        print ("Lights are ON")
        SWITCH = "ON"
    elif (value > threshold):
        print ("Lights are OFF")
        SWITCH = "OFF"
    
    if SWITCH != PREV_SWITCH:
        x = { "status": SWITCH }
        PREV_SWITCH = SWITCH
        payload = json.dumps(x)
        return x, payload
    else:
        x = { "status": "LITE"}
        PREV_SWITCH = SWITCH
        return x, None

try:
    while True:
        print ("LDR Value")
        value = rc_time(ldr)
        print (value)
        dict1, payload = calc_payload(value)

        if (payload != None):
            myMQTTClient.publish("sensors/ldr", payload, 1)
            print ("Toggled State!, Now wait 5 seconds!")
            time.sleep(5)
        else:
            pass
        time.sleep(2)
    
except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
