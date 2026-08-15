PROJECT_NAME = "taiga-tower"

def device_activate(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/activate"


def device_activate_pod(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/activatePod"


def device_command(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/command"


def pod_command(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/podCommand"

def pod_mode(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/mode"

def device_data(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/data"


# ACK topics

def device_activate_ack(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/ack/activate"


def device_activate_pod_ack(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/ack/activatePod"


def device_command_ack(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/ack/command"


def pod_command_ack(device_id: str, pod_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/{pod_id}/ack/command"


def device_data_ack(device_id: str) -> str:
    return f"{PROJECT_NAME}/devices/{device_id}/ack/data"


# Backend subscriptions

ALL_DEVICE_DATA = f"{PROJECT_NAME}/devices/+/data"

ALL_DEVICE_ACTIVATE_ACK = f"{PROJECT_NAME}/devices/+/ack/activate"

ALL_DEVICE_ACTIVATE_POD_ACK = f"{PROJECT_NAME}/devices/+/ack/activatePod"

ALL_DEVICE_COMMAND_ACK = f"{PROJECT_NAME}/devices/+/ack/command"

ALL_POD_COMMAND_ACK = f"{PROJECT_NAME}/devices/+/+/ack/command"