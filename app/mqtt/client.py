import random
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER= os.getenv("MQTT_BROKER")
MQTT_PORT= int(os.getenv("MQTT_PORT"))
MQTT_USERNAME= os.getenv("MQTT_USERNAME")
MQTT_PASSWORD= os.getenv("MQTT_PASSWORD")

class MQTTClient:

    def __init__(self):
        self.broker = MQTT_BROKER
        self.port = MQTT_PORT

        self.username = MQTT_USERNAME
        self.password = MQTT_PASSWORD

        self.topic = "python/mqtt"

        self.client_id = f"taiga-backend-{random.randint(0, 1000)}"

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        self.client.username_pw_set(
            self.username,
            self.password
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):
        print("Connected to EMQX!")
        print("Reason code:", reason_code)

        client.subscribe(self.topic)

        print(f"Subscribed to: {self.topic}")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()

        print(
            f"MQTT Message | "
            f"Topic: {msg.topic} | "
            f"Message: {message}"
        )

    def connect(self):
        self.client.connect(
            self.broker,
            self.port,
            keepalive=60
        )

        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, message):
        self.client.publish(
            topic,
            message
        )