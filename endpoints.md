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