import RPi.GPIO as GPIO
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import os,sys
import json

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
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

#set GPIO Pins

GPIO_TRIGGER = 23

GPIO_ECHO = 24

count = 0

#set GPIO direction (IN / OUT)

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)

GPIO.setup(GPIO_ECHO, GPIO.IN)

init_dist = 0.0

TOGGLED = 0

TOGGLED_ULTRA = False

path_to_ultra = "/home/pi/Documents/backend/mqtt_client/data/status.txt"

def distance():

    # set Trigger to HIGH

    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW

    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime

    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance

with open(path_to_ultra, "r") as f:
    PREV_SWITCH = f.read()

SWITCH = ""

def calc_payload(dist):
    status = "NO"
    global PREV_SWITCH, SWITCH, TOGGLED, TOGGLED_ULTRA

    if (init_dist*0.2 < dist < init_dist*0.8 or TOGGLED == 1):
        if (TOGGLED == 0):
            if (SWITCH=="OFF"):
                status = "ON"
                SWITCH = "ON"
            else:
                status = "OFF"
                SWITCH = "OFF"
            TOGGLED_ULTRA = True
        else:
            TOGGLED = 0
            status = SWITCH
    x = { "status": status }
    payload = json.dumps(x)
    return x, payload

if __name__ == '__main__':

    try:
        print ("Stablising Sensor, wait 5 seconds!")
        time.sleep(5)
        init_dist = distance()

        while True:

            dist = distance()

            with open(path_to_ultra, "r") as f:
                SWITCH = f.read()

            if (SWITCH != PREV_SWITCH and not TOGGLED_ULTRA):
                TOGGLED = 1
            elif (TOGGLED_ULTRA):
                TOGGLED_ULTRA = False

            print ("Measured Distance = %.1f cm" % dist)
            print (count)
            count+=1

            dict1, payload = calc_payload(dist)
            
            if (dict1["status"] != "NO"):
                myMQTTClient.publish("sensors/ultrasonic", payload, 1)
                print ("Toggled State!, Now wait 5 seconds!")
                time.sleep(5)
            else:
                pass
                
            PREV_SWITCH = SWITCH
            time.sleep(1)
            
        # Reset by pressing CTRL + C

    except KeyboardInterrupt:

        print("Measurement stopped by User")

        GPIO.cleanup()
