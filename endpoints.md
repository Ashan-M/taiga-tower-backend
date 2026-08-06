create device
{
  "message": "Device created successfully",
  "device": {
    "deviceID": "001004",
    "deviceType": "Taiga Tower",
    "masterLight": false,
    "masterPump": false,
    "floater": false
  }
}

create plant
{
  "message": "Plant created successfully",
  "plant": {
    "plantID": "001002",
    "plantName": "Potato",
    "maxGrowthPeriod": 20,
    "moistureLevel": 80,
    "lightIntensity": 95
  }
}

create pod
{
  "message": "Pod created successfully",
  "pod": {
    "podID": "001003",
    "plantID": "001002",
    "plantName": "Potato",
    "mode": "AUTO",
    "defaultMoistureLevel": 80,
    "defaultLightIntensity": 95,
    "manualMoistureLevel": null,
    "manualLightIntensity": null,
    "podPump": false,
    "podLight": false
  }
}

controllers
{
  "status": "updated",
  "pod": {
    "podID": "001003",
    "podPump": false,
    "podLight": false,
    "manualLightIntensity": 20,
    "manualMoistureLevel": 30
  }
}

mode
{
  "message": "Pod mode updated to MANUAL"
}

master-controllers
{
  "message": "Master controls updated successfully"
}

device-data
{
  "deviceID": "001001",
  "deviceType": "Taiga Tower",
  "masterLight": true,
  "masterPump": true,
  "floater": false,
  "pods": [
    {
      "podID": "001001",
      "podName": "POD 02",
      "plantID": "001001",
      "mode": "AUTO",
      "defaultMoistureLevel": 90,
      "defaultLightIntensity": 100,
      "manualMoistureLevel": null,
      "manualLightIntensity": null,
      "podPump": false,
      "podLight": false
    },
    {
      "podID": "001004",
      "podName": "POD 01",
      "plantID": "001001",
      "mode": "AUTO",
      "defaultMoistureLevel": 90,
      "defaultLightIntensity": 100,
      "manualMoistureLevel": null,
      "manualLightIntensity": null,
      "podPump": false,
      "podLight": false
    },
    {
      "podID": "001005",
      "podName": "POD 03",
      "plantID": "001001",
      "mode": "AUTO",
      "defaultMoistureLevel": 90,
      "defaultLightIntensity": 100,
      "manualMoistureLevel": null,
      "manualLightIntensity": null,
      "podPump": false,
      "podLight": false
    }
  ]
}
## Date & time filtering (new)

The log endpoints accept an optional inclusive date/time window. Values are ISO 8601
(e.g. `2026-08-01T00:00:00Z`). Passing `start_time > end_time` returns HTTP 400.

| Endpoint | Extra query params |
| --- | --- |
| `GET /devices/{device_id}/system-logs` | `start_time`, `end_time` |
| `GET /devices/{device_id}/pod-data-logs` | `start_time`, `end_time`, `pod_ids` (repeatable) |
| `GET /devices/{device_id}/pod-data-series` | `start_time`, `end_time`, `pod_ids` (repeatable), `limit` (default 2000, max 10000) |

`GET /devices/{device_id}/pod-data-series` is new and returns every matching pod data
point in chronological order together with the device's pod list, for charting:

```json
{
  "deviceID": "001002",
  "startTime": "2026-08-01T00:00:00Z",
  "endTime": "2026-08-06T00:00:00Z",
  "pods": [{ "podID": "001001", "podName": "POD 01" }],
  "items": [
    {
      "id": 12,
      "podID": "001001",
      "podName": "POD 01",
      "timeStamp": "2026-08-01T10:00:00Z",
      "moistureLevel": 42.0,
      "lightIntensity": 60.0
    }
  ]
}
```
