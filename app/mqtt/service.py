import json
import os
import random
import asyncio
from typing import Any

import paho.mqtt.client as mqtt

from app.mqtt import topics
from app.mqtt.handlers import MQTTMessageHandler


class MQTTService:

    def __init__(self):

        self.broker = os.getenv(
            "MQTT_BROKER",
            "broker.emqx.io"
        )

        self.port = int(
            os.getenv(
                "MQTT_PORT",
                "1883"
            )
        )

        self.username = os.getenv(
            "MQTT_USERNAME",
            "emqx"
        )

        self.password = os.getenv(
            "MQTT_PASSWORD"
        )

        self.client_id = (
            f"taiga-backend-"
            f"{random.randint(0, 100000)}"
        )

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        self.client.username_pw_set(
            self.username,
            self.password
        )
        self.client.tls_set()

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.connected = False
        self.pending_acks = {}
        self.message_handler = MQTTMessageHandler(
            mqtt_service=self
        )
        self.client.on_message = self._on_message


    def connect(self):

        print(
            f"Connecting to MQTT broker "
            f"{self.broker}:{self.port}"
        )

        self.client.connect(
            self.broker,
            self.port,
            keepalive=60
        )

        self.client.loop_start()


    def disconnect(self):

        print("Disconnecting from MQTT broker")

        self.client.loop_stop()
        self.client.disconnect()


    def publish(
        self,
        topic: str,
        payload: dict,
        qos: int = 1
    ):

        message = json.dumps(payload)

        result = self.client.publish(
            topic,
            message,
            qos=qos
        )

        print(
            f"MQTT publish → "
            f"{topic} | {message}"
        )

        return result


    def subscribe(
        self,
        topic: str,
        qos: int = 1
    ):

        result = self.client.subscribe(
            topic,
            qos=qos
        )

        print(
            f"MQTT subscribe → {topic}"
        )

        return result


    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):

        print(
            f"MQTT connected: {reason_code}"
        )

        if reason_code.is_failure:

            print(
                "MQTT connection failed"
            )
            self.connected = False
            return
        self.connected = True
        self._subscribe_to_topics()


    def _subscribe_to_topics(self):

        self.subscribe(
            topics.ALL_DEVICE_DATA
        )

        self.subscribe(
            topics.ALL_DEVICE_ACTIVATE_ACK
        )

        self.subscribe(
            topics.ALL_DEVICE_ACTIVATE_POD_ACK
        )

        self.subscribe(
            topics.ALL_DEVICE_COMMAND_ACK
        )

        self.subscribe(
            topics.ALL_POD_COMMAND_ACK
        )


    def _on_message(
        self,
        client,
        userdata,
        msg
    ):
        print(
        f"MQTT received ← {msg.topic}"
    )

        self.message_handler.handle(
            msg.topic,
            msg.payload
        )
  

    def _on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties
    ):

        print(
            f"MQTT disconnected: "
            f"{reason_code}"
        )
        self.connected = False

    async def publish_mqtt_topic(
                self, topic: str, payload: dict
        ) -> dict:
            loop = asyncio.get_running_loop()
            # future = loop.create_future()
            print("========== MQTT PUBLISH DEBUG ==========")
            print("Client:", self.client)
            print("Client connected:", self.client.is_connected())
            print("Topic:", topic)
            print("Payload:", json.dumps(payload))
            print("========================================")
            try:
                result = self.client.publish(
                    topic,
                    json.dumps(payload)
                )

                print("Publish result:", result)
                print("Publish rc:", result.rc)

                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    raise RuntimeError(
                        f"MQTT publish failed: {result.rc}"
                    )

                # Wait up to 10 seconds for Paho to complete the publish
                await asyncio.wait_for(
                    asyncio.to_thread(result.wait_for_publish),
                    timeout=10
                )

                if not result.is_published():
                    raise TimeoutError(
                        "MQTT publish did not complete within 10 seconds"
                    )

                print(f"MQTT publish → {topic} | {json.dumps(payload)}")

                return {
                    "status": "success",
                    "topic": topic
                }

            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"MQTT publish timed out after 10 seconds: {topic}"
                )

    async def publish_and_wait_ack(
            self, topic: str, payload: dict, ack_message_id: str, timeout: float = 10.0
    ) -> dict:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.pending_acks[ack_message_id] = future
        try:
            print("========== MQTT PUBLISH DEBUG ==========")
            print("Client:", self.client)
            print("Client connected:", self.client.is_connected())
            print("Topic:", topic)
            print("Payload:", json.dumps(payload))
            print("========================================")
            result = self.client.publish(topic, json.dumps(payload))
            print("Publish result:", result)
            print("Publish rc:", result.rc)

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT publish failed: {result.rc}")
            print(f"MQTT publish → {topic} | {json.dumps(payload)}")
            try:

                ack = await asyncio.wait_for(
                    future,
                    timeout=timeout
                )
                print(ack)

                return ack

            except asyncio.TimeoutError:

                raise TimeoutError(
                    f"Timeout waiting for ACK "
                    f"for message {ack_message_id}"
                )

        finally:

            self.pending_acks.pop(
                ack_message_id,
                None
            )

    def resolve_ack(self, payload: dict):

        message_id = payload.get("messageID")

        if not message_id:
            return

        future = self.pending_acks.get(message_id)

        if not future:
            print(
                f"No pending request for ACK: "
                f"{message_id}"
            )
            return

        if not future.done():

            loop = future.get_loop()

            loop.call_soon_threadsafe(
                future.set_result,
                payload
            )

mqttService = MQTTService()