from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import func

from app.database import get_db
from app.models import Pod, Device, Plant, PodLog, PodDataLog, SystemLog
from app.schemas.pod import CreatePodSchema, PodDataLogs, PodControlUpdate
from app.schemas.plant import CreatePlantSchema

from app.models import Device
from app.schemas.device import CreateDeviceSchema, DeviceMasterControl
from app.schemas.log import CreatePodDataLog, CreateSystemLog
from app.logger import logger

router = APIRouter(tags=["Dashboard"])
router = APIRouter(tags=["Pods"])
router = APIRouter(tags=["Devices"])

def generate_next_device_id(db: Session) -> str:
    # Get the last created device ordered by deviceID descending
    last_device = db.query(Device).order_by(Device.deviceID.desc()).first()
    
    if not last_device or not last_device.deviceID.isdigit():
        # Base starting ID if table is empty
        return "001001"

    next_id = int(last_device.deviceID) + 1
    return f"{next_id:06d}"

def generate_next_plant_id(db: Session) -> str:
    # Get the last created plant ordered by plantID descending
    last_plant = db.query(Plant).order_by(Plant.plantID.desc()).first()
    
    if not last_plant or not last_plant.plantID.isdigit():
        # Base starting ID if table is empty
        return "001001"

    next_id = int(last_plant.plantID) + 1
    return f"{next_id:06d}"

def generate_next_pod_id(db: Session) -> str:
    # Get the last created pod ordered by podID descending
    last_pod = db.query(Pod).order_by(Pod.podID.desc()).first()

    if not last_pod or not last_pod.podID.isdigit():
        # Base starting ID if table is empty
        return "001001"

    next_id = int(last_pod.podID) + 1
    return f"{next_id:06d}"


class MasterControlUpdate(BaseModel):
    master_light: Optional[bool] = None
    master_pump: Optional[bool] = None

class CreatePodRequest(BaseModel):
    pod_id: str
    plant_name: str
    mode: str = Field(default="AUTO", pattern="^(AUTO|MANUAL)$")



class ModeUpdate(BaseModel):
    mode: str = Field(..., pattern="^(AUTO|MANUAL)$")


@router.get("/devices/{device_id}/device-data")
def get_device_data(
    device_id: str,
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(Device.deviceID == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    pods = db.query(Pod).filter(Pod.deviceID == device_id).all()
    pod_data_list = []

    for pod in pods:
        pod_data = {
            "podID": pod.podID,
            "podName": pod.podName,
            "plantName": pod.plant.plantName if pod.plant else None,
            "mode": pod.mode,
            "defaultMoistureLevel": pod.defaultMoistureLevel,
            "defaultLightIntensity": pod.defaultLightIntensity,
            "manualMoistureLevel": pod.manualMoistureLevel,
            "manualLightIntensity": pod.manualLightIntensity,
            "podPump": pod.podPump,
            "podLight": pod.podLight
        }
        pod_data_list.append(pod_data)

    print(pod_data_list)

    return {
        "deviceID": device.deviceID,
        "deviceType": device.deviceType,
        "masterLight": device.masterLight,
        "masterPump": device.masterPump,
        "floater": device.floater,
        "pods": pod_data_list
    }
    

@router.post("/devices", status_code=status.HTTP_201_CREATED)
def create_device(
    payload: CreateDeviceSchema, 
    db: Session = Depends(get_db)
):
    # Auto-generate incremental device ID
    try:
        logger.info("Attempting to create a new device...")

        new_device_id = generate_next_device_id(db)

        # Create new device with default OFF master controls
        new_device = Device(
            deviceID=new_device_id,
            deviceType=payload.device_type.value,
            created_at=datetime.utcnow(),
            masterLight=False,  # OFF by default
            masterPump=False,   # OFF by default
            floater=False
        )

        new_system_log = SystemLog(
            deviceID=new_device_id,
            message="Device created successfully"
        )

        db.add(new_device)
        db.add(new_system_log)
        db.commit()
        db.refresh(new_device)
        db.refresh(new_system_log)

        logger.info(f"Device created successfully with ID: {new_device.deviceID}")
        return {
            "message": "Device created successfully",
            "device": {
                "deviceID": new_device.deviceID,
                "deviceType": new_device.deviceType,
                "masterLight": new_device.masterLight,
                "masterPump": new_device.masterPump,
                "floater": new_device.floater
            }
        }
    except Exception as e:
        logger.error(f"Failed to create device: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.post("/create-plant", status_code=status.HTTP_201_CREATED)
def create_plant(
    payload: CreatePlantSchema,
    db: Session = Depends(get_db)
):
    print(payload)
    try:
        logger.info("Attempting to create a new plant.")
    # Auto-generate incremental plant ID
        new_plant_id = generate_next_plant_id(db)

        # Create new plant
        new_plant = Plant(
            plantID=new_plant_id,
            plantName=payload.plantName,
            maxGrowthPeriod=payload.maxGrowthPeriod,
            moistureLevel=payload.moistureLevel,
            lightIntensity=payload.lightIntensity,
            created_at=datetime.utcnow()
        )

        db.add(new_plant)
        db.commit()
        db.refresh(new_plant)
        logger.info(f"Plant created successfully with ID: {new_plant.plantID}")

        return {
            "message": "Plant created successfully",
            "plant": {
                "plantID": new_plant.plantID,
                "plantName": new_plant.plantName,
                "maxGrowthPeriod": new_plant.maxGrowthPeriod,
                "moistureLevel": new_plant.moistureLevel,
                "lightIntensity": new_plant.lightIntensity
            }
        }
    except Exception as e:
            logger.error(f"Failed to create plant: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/plants", status_code=status.HTTP_200_OK)
def get_all_plants(db: Session = Depends(get_db)):
    try:
        plants = db.query(Plant).all()
        return {"plants": plants}
    except Exception as e:
        logger.error(f"Failed to retrieve plants: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/devices/{device_id}/master-controls")
def update_master_controls(
    device_id: str, 
    payload: DeviceMasterControl, 
    db: Session = Depends(get_db)
):
    print(payload)
    device = db.query(Device).filter(Device.deviceID == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    changes = []
    if payload.masterLight is not None and payload.masterLight != device.masterLight:
        device.masterLight = payload.masterLight
        changes.append(f"Updated master Light to {payload.masterLight}")
        # logger.info(f"Updated masterLight for device {device_id} to {payload.masterLight}")

    if payload.masterPump is not None and payload.masterPump != device.masterPump:
        device.masterPump = payload.masterPump
        changes.append(f"Updated master Pump to {payload.masterPump}")
        # logger.info(f"Updated masterPump for device {device_id} to {payload.masterPump}")

    if changes:
        new_system_log = SystemLog(
                                deviceID=device_id,
                                message=", ".join(changes)
                            )
        db.add(new_system_log)  
        # logger.info(f"Updated master controls for device {device_id}: {', '.join(changes)}")

    
    db.commit()
    # db.refresh(new_system_log)
    logger.info(f"Master controls updated successfully for device {device_id}: {', '.join(changes)}")
    return {"masterLight": device.masterLight,
            "masterPump": device.masterPump
            }


# 2. Add a new Pod
@router.post("/devices/{device_id}/create-pod", status_code=status.HTTP_201_CREATED)
def create_pod(
    device_id: str, 
    payload: CreatePodSchema, 
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Attempting to create a new pod for device '{device_id}'.")
    # 1. Check if Device exists
        device = db.query(Device).filter(
            Device.deviceID == device_id
        ).first()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Device with ID '{device_id}' not found."
            )

        # 2. Check if Pod ID already exists
        existing_pod = db.query(Pod).filter(Pod.deviceID == device_id, Pod.podName == payload.podName).first()
        if existing_pod:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Pod ID '{payload.podName}' already exists."
            )

        # 3. Fetch Selected Plant Configuration from `plants` table
        plant = db.query(Plant).filter(Plant.plantID == payload.plantID).first()
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Plant with ID '{payload.plantID}' not found."
            )

        # 4. Prepare Pod instance based on Mode
        new_pod = Pod(
            podID=generate_next_pod_id(db),
            podName=payload.podName,
            deviceID=device_id,
            plantID=plant.plantID,
            mode=payload.mode,
            # Load default plant configurations into the pod
            defaultMoistureLevel=plant.moistureLevel,
            defaultLightIntensity=plant.lightIntensity
        )

        if payload.mode == "MANUAL":
            # Assign manual settings provided by user
            new_pod.podPump = payload.pod_pump
            new_pod.podLight = payload.pod_light
            new_pod.manualMoistureLevel = payload.manual_moisture_level
            new_pod.manualLightIntensity = payload.manual_light_intensity
        else:  # AUTO mode
            # Default operational state in AUTO mode
            new_pod.podPump = False
            new_pod.podLight = False
            new_pod.manualMoistureLevel = None
            new_pod.manualLightIntensity = None

        db.add(new_pod)
        db.commit()
        db.refresh(new_pod)

        logger.info(f"Pod '{new_pod.podID}' created successfully for device '{device_id}' with plant '{plant.plantName}'.")

        return {
            "message": "Pod created successfully",
            "pod": {
                "podID": new_pod.podID,
                "plantID": new_pod.plantID,
                "plantName": plant.plantName,
                "mode": new_pod.mode,
                "defaultMoistureLevel": new_pod.defaultMoistureLevel,
                "defaultLightIntensity": new_pod.defaultLightIntensity,
                "manualMoistureLevel": new_pod.manualMoistureLevel,
                "manualLightIntensity": new_pod.manualLightIntensity,
                "podPump": new_pod.podPump,
                "podLight": new_pod.podLight
            }
        }
    except Exception as e:
                logger.error(f"Failed to create plant: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/pods/{pod_id}/mode")
def update_pod_mode(pod_id:str, payload: ModeUpdate, db: Session = Depends(get_db)):
    pod = db.query(Pod).filter(Pod.podID == pod_id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    pod.mode = payload.mode
    db.commit()
    return {"message": f"Pod mode updated to {payload.mode}"}


# 3. Micro-manage Pod Controls (Instant DB updates for sliders/switches)
@router.patch("/pods/{pod_id}/controllers")
def update_pod_controls(
    pod_id: str, 
    payload: PodControlUpdate, 
    db: Session = Depends(get_db)
):
    print(payload)
    pod = db.query(Pod).filter(Pod.podID == pod_id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")

    if pod.mode != "MANUAL":
        raise HTTPException(
            status_code=400, 
            detail="Pod must be in MANUAL mode to adjust custom controls"
        )
    print(pod_id)
    update_data = payload.model_dump(exclude_unset=True)
    
    # Map frontend camelCase/snake_case to SQLAlchemy model attributes
    if "podPump" in update_data:
        pod.podPump = update_data["podPump"]
    if "podLight" in update_data:
        pod.podLight = update_data["podLight"]
    if "manualLightIntensity" in update_data:
        pod.manualLightIntensity = update_data["manualLightIntensity"]
    if "manualMoistureLevel" in update_data:
        pod.manualMoistureLevel = update_data["manualMoistureLevel"]

    db.commit()
    return {"status": "updated",
            "pod": {
                "podID": pod.podID,
                "podPump": pod.podPump,
                "podLight": pod.podLight,
                "manualLightIntensity": pod.manualLightIntensity,
                "manualMoistureLevel": pod.manualMoistureLevel
            }
        }


# 4. Fetch System Activity Logs with Infinite/Scrolling Pagination (Min limit = 10)
@router.get("/devices/{device_id}/logs")
def get_system_logs(
    device_id: str,
    limit: int = Query(default=10, ge=10),  # Enforce minimum 10 rows
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(PodLog).filter(PodLog.deviceID == device_id).order_by(PodLog.timeStamp.desc())
    
    total_count = query.count()
    logs = query.offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count,
        "items": [
            {
                "timestamp": log.timeStamp.strftime("%Y-%m-%d %H:%M:%S"),
                "pod_id": log.podID,
                "event": log.message
            }
            for log in logs
        ]
    }

@router.post("/pods/{pod_id}/data-log")
def create_pod_data_log(
    pod_id: str,
    payload: CreatePodDataLog,
    db: Session = Depends(get_db)
):
    pod = db.query(Pod).filter(Pod.podID == pod_id).first()
    if not pod:
        raise HTTPException(
            status_code=404,
            detail="Pod not found"
        )
    data_log = PodDataLog(
        podID=pod_id,
        moistureLevel=payload.moistureLevel,
        lightIntensity=payload.lightIntensity
    )

    db.add(data_log)
    db.commit()
    db.refresh(data_log)

@router.get("/devices/{device_id}/pod-data-logs")
def get_pod_data_logs(
    device_id: str,
    cursor: Optional[datetime] = Query(
        None,
        description="Timestamp cursor from previous response"
    ),
    limit: int = Query(20, ge=1, le=100),
    start_time: Optional[datetime] = Query(
        None,
        description="Only return logs recorded at or after this date/time (ISO 8601)"
    ),
    end_time: Optional[datetime] = Query(
        None,
        description="Only return logs recorded at or before this date/time (ISO 8601)"
    ),
    pod_ids: Optional[List[str]] = Query(
        None,
        description="Restrict results to these pod IDs"
    ),
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(
        Device.deviceID == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    query = (
        db.query(PodDataLog, Pod)
        .join(Pod, PodDataLog.podID == Pod.podID)
        .filter(Pod.deviceID == device_id)
    )

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be earlier than or equal to end_time"
        )

    if start_time:
        query = query.filter(PodDataLog.timeStamp >= start_time)

    if end_time:
        query = query.filter(PodDataLog.timeStamp <= end_time)

    if pod_ids:
        query = query.filter(PodDataLog.podID.in_(pod_ids))

    if cursor:
        query = query.filter(
            PodDataLog.timeStamp < cursor
        )

    logs = (
        query.order_by(PodDataLog.timeStamp.desc())
        .limit(limit + 1)
        .all()
    )

    has_more = len(logs) > limit

    if has_more:
        next_cursor = logs[limit - 1][0].timeStamp
        logs = logs[:limit]
    else:
        next_cursor = None

    return {
        "items": [
            {
                "id": log.id,
                "podID": log.podID,
                "podName": pod.podName,
                "timeStamp": log.timeStamp,
                "moistureLevel": log.moistureLevel,
                "lightIntensity": log.lightIntensity,
            }
            for log, pod in logs
        ],
        "nextCursor": next_cursor,
        "hasMore": has_more,
        "startTime": start_time,
        "endTime": end_time
    }


@router.get("/devices/{device_id}/pod-data-series")
def get_pod_data_series(
    device_id: str,
    start_time: Optional[datetime] = Query(
        None,
        description="Only return points recorded at or after this date/time (ISO 8601)"
    ),
    end_time: Optional[datetime] = Query(
        None,
        description="Only return points recorded at or before this date/time (ISO 8601)"
    ),
    pod_ids: Optional[List[str]] = Query(
        None,
        description="Restrict the series to these pod IDs"
    ),
    limit: int = Query(2000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Chronological pod data points for charting (moisture + light intensity)."""
    device = db.query(Device).filter(Device.deviceID == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be earlier than or equal to end_time"
        )

    query = (
        db.query(PodDataLog, Pod)
        .join(Pod, PodDataLog.podID == Pod.podID)
        .filter(Pod.deviceID == device_id)
    )

    if start_time:
        query = query.filter(PodDataLog.timeStamp >= start_time)
    if end_time:
        query = query.filter(PodDataLog.timeStamp <= end_time)
    if pod_ids:
        query = query.filter(PodDataLog.podID.in_(pod_ids))

    rows = (
        query.order_by(PodDataLog.timeStamp.asc())
        .limit(limit)
        .all()
    )

    pods = db.query(Pod).filter(Pod.deviceID == device_id).all()

    return {
        "deviceID": device_id,
        "startTime": start_time,
        "endTime": end_time,
        "pods": [{"podID": p.podID, "podName": p.podName} for p in pods],
        "items": [
            {
                "id": log.id,
                "podID": log.podID,
                "podName": pod.podName,
                "timeStamp": log.timeStamp,
                "moistureLevel": log.moistureLevel,
                "lightIntensity": log.lightIntensity,
            }
            for log, pod in rows
        ],
    }

@router.get("/devices/{device_id}/latest-data-logs")
def get_latest_pod_data(
    device_id: str,
    db: Session = Depends(get_db)
):

    device = (
        db.query(Device)
        .filter(Device.deviceID == device_id)
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    # Get latest log id for each pod
    latest_logs = (
        db.query(
            PodDataLog.podID,
            func.max(PodDataLog.id).label("latest_id")
        )
        .join(Pod, PodDataLog.podID == Pod.podID)
        .filter(Pod.deviceID == device_id)
        .group_by(PodDataLog.podID)
        .subquery()
    )

    # Get pod details + latest log
    results = (
        db.query(
            Pod,
            PodDataLog
        )
        .join(
            latest_logs,
            PodDataLog.id == latest_logs.c.latest_id
        )
        .join(
            Pod,
            PodDataLog.podID == Pod.podID
        )
        .all()
    )

    return {
        "deviceID": device_id,
        "pods": [
            {

                "latestData": {
                    "id": log.id,
                    "podID": pod.podID,
                    "podName": pod.podName,
                    "timeStamp": log.timeStamp,
                    "moistureLevel": log.moistureLevel,
                    "lightIntensity": log.lightIntensity,
                }
            }
            for pod, log in results
        ]
    }

@router.get("/devices/{device_id}/system-logs")
def get_system_logs(
    device_id: str,
    cursor: Optional[int] = Query(None),
    limit: int = Query(2, ge=1, le=100),
    start_time: Optional[datetime] = Query(
        None,
        description="Only return logs recorded at or after this date/time (ISO 8601)"
    ),
    end_time: Optional[datetime] = Query(
        None,
        description="Only return logs recorded at or before this date/time (ISO 8601)"
    ),
    db: Session = Depends(get_db)
):

    device = db.query(Device).filter(
        Device.deviceID == device_id
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    query = (
        db.query(SystemLog)
        .filter(SystemLog.deviceID == device_id)
    )

    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be earlier than or equal to end_time"
        )

    if start_time:
        query = query.filter(SystemLog.timeStamp >= start_time)

    if end_time:
        query = query.filter(SystemLog.timeStamp <= end_time)

    if cursor:
        query = query.filter(
            SystemLog.id < cursor
        )

    logs = (
        query.order_by(SystemLog.id.desc())
        .limit(limit + 1)
        .all()
    )

    has_more = len(logs) > limit

    if has_more:
        next_cursor = logs[limit - 1].id
        logs = logs[:limit]
    else:
        next_cursor = None

    return {
        "items": [
            {
                "id": log.id,
                "podID": log.podID,
                "timeStamp": log.timeStamp,
                "message": log.message,
            }
            for log in logs
        ],
        "nextCursor": next_cursor,
        "hasMore": has_more,
        "startTime": start_time,
        "endTime": end_time
    }
