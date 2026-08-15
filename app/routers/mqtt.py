from fastapi import APIRouter, Request


router = APIRouter()

@router.get("/status")
def get_mqtt_status(request: Request):
    client = request.app.state.mqtt_client
    return {"status": "connected"}