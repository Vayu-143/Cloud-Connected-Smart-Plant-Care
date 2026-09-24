from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import (
    initialize_database,
    save_sensor_reading,
    get_latest_reading,
    get_sensor_history,
    save_watering_event,
    get_watering_history
)

from watering import (
    DEFAULT_THRESHOLD,
    check_watering_required,
    get_plant_status,
    get_pump_status
)


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="Smart Plant Care API",
    description="Simple Cloud-Connected Smart Plant Care System",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# Application State
# =========================================================

MOISTURE_THRESHOLD = DEFAULT_THRESHOLD

DEVICE_ID = "PLANT-001"

PUMP_STATUS = "OFF"


# =========================================================
# Request Models
# =========================================================

class SensorData(BaseModel):

    device_id: str = Field(
        default="PLANT-001",
        min_length=1
    )

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=100
    )

    temperature: float = Field(
        ...,
        ge=-20,
        le=60
    )

    humidity: float = Field(
        ...,
        ge=0,
        le=100
    )

    timestamp: Optional[str] = None


class WaterRequest(BaseModel):

    device_id: str = "PLANT-001"


class ThresholdRequest(BaseModel):

    threshold: float = Field(
        ...,
        ge=0,
        le=100
    )


# =========================================================
# Startup
# =========================================================

@app.on_event("startup")
def startup_event():

    initialize_database()


# =========================================================
# Root
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Smart Plant Care API is running",
        "status": "success"
    }


# =========================================================
# Health Check
# =========================================================

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "service": "smart-plant-backend"
    }


# =========================================================
# Receive Sensor Data
# =========================================================

@app.post("/api/sensor")
def receive_sensor_data(data: SensorData):

    global PUMP_STATUS

    previous_pump_status = PUMP_STATUS

    # -----------------------------------------------------
    # Save sensor reading
    # -----------------------------------------------------

    save_sensor_reading(
        device_id=data.device_id,
        soil_moisture=data.soil_moisture,
        temperature=data.temperature,
        humidity=data.humidity,
        timestamp=data.timestamp
    )

    # -----------------------------------------------------
    # Determine plant status
    # -----------------------------------------------------

    plant_status = get_plant_status(
        data.soil_moisture,
        MOISTURE_THRESHOLD
    )

    # -----------------------------------------------------
    # Automatic watering decision
    # -----------------------------------------------------

    watering_required = check_watering_required(
        data.soil_moisture,
        MOISTURE_THRESHOLD
    )

    if watering_required:

        PUMP_STATUS = "ON"

    else:

        PUMP_STATUS = "OFF"

    # -----------------------------------------------------
    # Detect NEW automatic watering event
    # -----------------------------------------------------

    automatic_watering_started = (
        previous_pump_status == "OFF"
        and PUMP_STATUS == "ON"
    )

    # -----------------------------------------------------
    # Simulated moisture after watering
    # -----------------------------------------------------

    moisture_after_watering = min(
        data.soil_moisture + 10,
        100
    )

    # -----------------------------------------------------
    # Store automatic watering event
    # -----------------------------------------------------

    if automatic_watering_started:

        save_watering_event(
            device_id=data.device_id,
            trigger_type="AUTOMATIC",
            moisture_before=data.soil_moisture,
            moisture_after=moisture_after_watering
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {

        "message": "Sensor data received successfully",

        "device_id": data.device_id,

        "soil_moisture": data.soil_moisture,

        "temperature": data.temperature,

        "humidity": data.humidity,

        "plant_status": plant_status,

        "pump_status": PUMP_STATUS,

        "watering_required": watering_required,

        "watering_started": automatic_watering_started,

        "moisture_after_watering":
            moisture_after_watering

    }


# =========================================================
# Latest Sensor Data
# =========================================================

@app.get("/api/latest")
def latest_sensor_data(
    device_id: str = DEVICE_ID
):

    reading = get_latest_reading(device_id)

    if reading is None:

        raise HTTPException(
            status_code=404,
            detail="No sensor data available"
        )

    soil_moisture = reading["soil_moisture"]

    reading["plant_status"] = get_plant_status(
        soil_moisture,
        MOISTURE_THRESHOLD
    )

    reading["pump_status"] = get_pump_status(
        soil_moisture,
        MOISTURE_THRESHOLD
    )

    reading["threshold"] = MOISTURE_THRESHOLD

    return reading


# =========================================================
# Sensor History
# =========================================================

@app.get("/api/history")
def sensor_history(
    device_id: str = DEVICE_ID,
    limit: int = 50
):

    if limit < 1 or limit > 500:

        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 500"
        )

    history = get_sensor_history(
        device_id=device_id,
        limit=limit
    )

    return {
        "device_id": device_id,
        "count": len(history),
        "data": history
    }


# =========================================================
# Manual Watering
# =========================================================

@app.post("/api/water")
def manual_watering(
    request: WaterRequest
):

    global PUMP_STATUS

    latest = get_latest_reading(
        request.device_id
    )

    if latest is None:

        raise HTTPException(
            status_code=404,
            detail="No sensor reading available"
        )

    moisture_before = latest["soil_moisture"]

    PUMP_STATUS = "ON"

    moisture_after = min(
        moisture_before + 15,
        100
    )

    save_watering_event(
        device_id=request.device_id,
        trigger_type="MANUAL",
        moisture_before=moisture_before,
        moisture_after=moisture_after
    )

    PUMP_STATUS = "OFF"

    return {

        "message":
            "Plant watered successfully",

        "device_id":
            request.device_id,

        "moisture_before":
            moisture_before,

        "moisture_after":
            moisture_after,

        "pump_status":
            PUMP_STATUS

    }


# =========================================================
# Watering History
# =========================================================

@app.get("/api/watering-history")
def watering_history(
    device_id: str = DEVICE_ID,
    limit: int = 20
):

    if limit < 1 or limit > 200:

        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 200"
        )

    history = get_watering_history(
        device_id=device_id,
        limit=limit
    )

    return {

        "device_id": device_id,

        "count": len(history),

        "data": history

    }


# =========================================================
# Get Moisture Threshold
# =========================================================

@app.get("/api/threshold")
def get_threshold():

    return {

        "threshold":
            MOISTURE_THRESHOLD

    }


# =========================================================
# Update Moisture Threshold
# =========================================================

@app.put("/api/threshold")
def update_threshold(
    request: ThresholdRequest
):

    global MOISTURE_THRESHOLD

    MOISTURE_THRESHOLD = request.threshold

    return {

        "message":
            "Moisture threshold updated",

        "threshold":
            MOISTURE_THRESHOLD

    }