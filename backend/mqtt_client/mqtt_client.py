from __future__ import print_function
import sys
import ssl
import time
import datetime
import logging, traceback
import paho.mqtt.client as mqtt
import json
import sys
from PIL import Image
import numpy as np

class MQTT_Client:

    def __init__(self,topic,header, message, file_name):
        self.IoT_protocol_name = "x-amzn-mqtt-ca"
        self.aws_iot_endpoint = "a2vsckvuvvwwc1-ats.iot.us-east-1.amazonaws.com" # <random>.iot.<region>.amazonaws.com
        self.url = "https://{}".format(self.aws_iot_endpoint)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.StreamHandler(sys.stdout)
        self.log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.log_format)
        self.logger.addHandler(self.handler)

        self.flag = 0
        self.topic = topic
        self.header = header
        self.message = message
        self.file_name = file_name
        self.faces = []

    def ssl_alpn(self):
        try:
            ca = "certs/root-ca.pem"
            cert = "certs/sensor_ultrasonic-certificate.pem.crt"
            private = "certs/sensor_ultrasonic-private.pem.key"
            #debug print opnessl version
            self.logger.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.set_alpn_protocols([self.IoT_protocol_name])
            self.ssl_context.load_verify_locations(cafile=ca)
            self.ssl_context.load_cert_chain(certfile=cert, keyfile=private)

            return  self.ssl_context
        except Exception as e:
            print("exception ssl_alpn()")
            raise e
    
    def on_message_rec(self, client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
        #print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
        self.flag = json.loads(msg.payload.decode('utf-8'))[self.header]

    def main(self):
        if __name__ == '__main__':
            try:
                mqttc = mqtt.Client()
                self.ssl_context= self.ssl_alpn()
                mqttc.tls_set_context(context=self.ssl_context)
                self.logger.info("start connect")
                mqttc.connect(self.aws_iot_endpoint, port=443)
                self.logger.info("connect success")
                mqttc.loop_start()
                mqttc.subscribe(self.topic,0)
                mqttc.on_message = self.on_message_rec
                while True:
                    if (self.flag):
                        print (self.message)
                        print (self.flag)
                        with open("data/" + self.file_name, "w") as f:
                            f.write("{flag}".format(flag=self.flag))
                        self.flag = 0
                    else:
                        pass
                        time.sleep(1)
            except Exception as e:
                self.logger.error("exception main()")
                self.logger.error("e obj:{}".format(vars(e)))
                traceback.print_exc(file=sys.stdout)
                mqttc.unsubscribe(self.topic)


if (sys.argv[1] == "ultrasonic"):
    ultrasonic_client = MQTT_Client("sensors/ultrasonic", "status", "LED Toggled", "status.txt")
    ultrasonic_client.main()
elif (sys.argv[1] == "cam"):
    cam_client = MQTT_Client("sensors/cam", "detected", "Intruder Detected!", "cam.txt")
    cam_client.main()
elif (sys.argv[1] == "ldr"):
    ldr_client = MQTT_Client("sensors/ldr", "status", "Light Changed", "ldr.txt")
    ldr_client.main()
