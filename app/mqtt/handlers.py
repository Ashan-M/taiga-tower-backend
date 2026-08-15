import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Pod, Device, Plant, PodLog, PodDataLog, SystemLog
from fastapi import Depends
from app.database import SessionLocal, get_db

from app.mqtt.schemas import DeviceDataMessage, DeviceCommandMessage
from app.mqtt.topics import PROJECT_NAME

def create_pod_data_log(
    db: Session,
    # deviceID: str,
    podID: str,
    moistureLevel: float | None,
    lightIntensity: float | None
) -> PodDataLog:

    pod = (
        db.query(Pod)
        .filter(
            Pod.podID == podID,
            # Pod.deviceID == deviceID
        )
        .first()
    )

    if not pod:
        raise ValueError(
            f"Pod {podID} not found "
            # f"for device {deviceID}"
        )

    data_log = PodDataLog(
        podID=podID,
        moistureLevel=moistureLevel,
        lightIntensity=lightIntensity
    )

    db.add(data_log)

    return data_log

class MQTTMessageHandler:

    def __init__(self, mqtt_service):
        self.mqtt_service = mqtt_service
        
    def handle(self, topic: str, payload: bytes):
        try:
            data = json.loads(
                payload.decode("utf-8"))
        except json.JSONDecodeError:
            print(
                f"Invalid MQTT JSON payload "
                f"on topic: {topic}")
            return
        print(
            f"Processing MQTT message: "
            f"{topic}"
        )
        if (topic.startswith(f"{PROJECT_NAME}/devices/")
            and topic.endswith("/data")):

            self.handle_device_data(
                topic,
                data
            )

            return

        # ========================================================
        # DEVICE ACTIVATE ACK
        # ========================================================

        if (
            topic.startswith(
                f"{PROJECT_NAME}/devices/"
            )
            and topic.endswith("/ack/activate")
        ):

            self.handle_ack(
                topic,
                data,
                "activate")
            return

        # ========================================================
        # POD ACTIVATE ACK
        # ========================================================

        if (
            topic.startswith(
                f"{PROJECT_NAME}/devices/"
            )
            and topic.endswith("/ack/activatePod")
        ):

            self.handle_ack(
                topic,
                data,
                "activatePod"
            )

            return

        # ========================================================
        # DEVICE COMMAND ACK
        # ========================================================

        if (
            topic.startswith(
                f"{PROJECT_NAME}/devices/"
            )
            and topic.endswith("/ack/command")
        ):

            self.handle_ack(
                topic,
                data,
                "device command"
            )

            return

        # ========================================================
        # POD COMMAND ACK
        # ========================================================

        if (
            topic.startswith(
                f"{PROJECT_NAME}/devices/"
            )
            and topic.endswith("/ack/command")
        ):

            self.handle_ack(
                topic,
                data,
                "pod command"
            )

            return

        # ========================================================
        # UNKNOWN TOPIC
        # ========================================================

        print(
            f"Unhandled MQTT topic: "
            f"{topic}"
        )


    def handle_device_data(
        self,
        topic: str,
        data: dict):

        try:
            message = DeviceDataMessage.model_validate(data)
        except Exception as e:
            print(f"Invalid device data: {e}")
            return
        
        print(
            f"Device data received: "
            f"{message.deviceID}"
        )

        for pod in message.pods:

            print(
                f"Pod {pod.podID}: "
                f"moisture={pod.moistureLevel}, "
                f"light={pod.lightIntensity}")
        db = SessionLocal()

        try:
            for pod in message.pods:
                create_pod_data_log(
                    db=db,
                    podID=pod.podID,
                    moistureLevel=pod.moistureLevel,
                    lightIntensity=pod.lightIntensity)
            db.commit()
            print(
                f"Saved data for device "
                f"{message.deviceID}")

        except Exception as e:

            db.rollback()

            print(
                f"Failed to save MQTT data: {e}"
            )

        finally:
            db.close()


    def handle_ack(
        self,
        topic: str,
        data: dict,
        ack_type: str
    ):

        print(
            f"MQTT {ack_type} ACK received"
        )

        message_id = data.get(
            "messageID"
        )

        if not message_id:

            print(
                f"ACK received without "
                f"messageID: {data}"
            )

            return

        print(
            f"ACK messageID: {message_id}"
        )

        print(
            f"ACK status: "
            f"{data.get('status')}"
        )

        # --------------------------------------------------------
        # Resolve the Future waiting for this ACK
        # --------------------------------------------------------

        self.mqtt_service.resolve_ack(
            data
        )