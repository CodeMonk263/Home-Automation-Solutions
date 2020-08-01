## LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3
## use ^ if not able to import cv2
import numpy as np
import cv2
import matplotlib.pyplot as plt
import base64
import requests
from pprint import pprint
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import json
from PIL import Image
import io
import sys

myMQTTClient = AWSIoTMQTTClient("myClientID")

myMQTTClient.configureEndpoint("a2vsckvuvvwwc1-ats.iot.us-east-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/Documents/face_detector/certs/root-ca.pem", 
                                  "/home/pi/Documents/face_detector/certs/sensor_ultrasonic-private.pem.key", 
                                  "/home/pi/Documents/face_detector/certs/sensor_ultrasonic-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1) #Infinite Offline Publishing
myMQTTClient.configureDrainingFrequency(2) #Draining: 2Hz
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

#connect and publish
myMQTTClient.connect()

xmin,ymin,xmax,ymax = 0,0,0,0
count = 0
response={}

face_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
face_side_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')

def calc_payload(arr):
    count = 1
    for img in arr:
        print (img.shape)
        photo = Image.fromarray(img, "RGB")
        photo.save("/home/pi/Documents/sensor-nodes/src/images/face{num}.png".format(num=count))
        count+=1
    payload = json.dumps({ "detected" : "YES" })
    return payload

def detect_face(img):
    
    face_img = img.copy()
    faces = []
    face_rects = face_cascade.detectMultiScale(face_img)
    face_rects2 = face_side_cascade.detectMultiScale(face_img)
   
    if (len(face_rects)):
        for (x,y,w,h) in face_rects:
            cv2.rectangle(face_img, (x,y), (x+w,y+h), (255,255,255), 10)
            face = face_img[y:y+h, x:x+w]
            faces.append(face)
    

    if (len(face_rects2)):
        for (x,y,w,h) in face_rects2:
            cv2.rectangle(face_img, (x,y), (x+w,y+h), (255,255,255), 10)
            face = face_img[y:y+h, x:x+w]
            faces.append(face)
    
    return faces, face_img
    

cap = cv2.VideoCapture(0)
cap.set(3,300)
cap.set(4,300)

faces_arr = []

flag = False

payload = json.dumps({})

while True:

    if (flag):
        flag = False
        myMQTTClient.publish("sensors/cam", payload, 1)
        time.sleep(15)
        myMQTTClient.publish("sensors/cam", json.dumps({"detected":"NO"}), 1)

    ret, frame = cap.read(0)

    cv2.imwrite(filename='saved_img.jpg', img=frame)

    faces, frame = detect_face(frame)
    
    faces_arr.extend(faces)

    if (len(faces_arr) > 3):
        payload = calc_payload(faces_arr)
        frame[:,:,:] = 0
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame,text='Intruder!',org=(200,200), fontFace=font,fontScale= 2,color=(255,255,255),thickness=2,lineType=cv2.LINE_AA)
        flag = True
        faces_arr.clear()

    cv2.imshow('Face Detection', frame)

    c = cv2.waitKey(1)
    if c == 27:
        break
        
cv2.destroyAllWindows()
cap.release()
