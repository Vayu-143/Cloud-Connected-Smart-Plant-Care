import random
import time
from datetime import datetime

import requests


# =========================================================
# Configuration
# =========================================================

API_URL = "http://127.0.0.1:8000/api/sensor"

DEVICE_ID = "PLANT-001"

SEND_INTERVAL = 5


# =========================================================
# Initial Virtual Plant State
# =========================================================

soil_moisture = 55.0

temperature = 28.0

humidity = 65.0


# =========================================================
# Generate Sensor Data
# =========================================================

def generate_sensor_data():

    global soil_moisture
    global temperature
    global humidity

    # -----------------------------------------------------
    # Soil moisture slowly decreases
    # -----------------------------------------------------

    soil_moisture -= random.uniform(
        1.0,
        3.0
    )

    # Keep value between 0 and 100

    soil_moisture = max(
        0,
        min(
            100,
            soil_moisture
        )
    )

    # -----------------------------------------------------
    # Temperature changes gradually
    # -----------------------------------------------------

    temperature += random.uniform(
        -0.5,
        0.5
    )

    temperature = max(
        15,
        min(
            40,
            temperature
        )
    )

    # -----------------------------------------------------
    # Humidity changes gradually
    # -----------------------------------------------------

    humidity += random.uniform(
        -2,
        2
    )

    humidity = max(
        30,
        min(
            90,
            humidity
        )
    )

    return {

        "device_id":
            DEVICE_ID,

        "soil_moisture":
            round(
                soil_moisture,
                2
            ),

        "temperature":
            round(
                temperature,
                2
            ),

        "humidity":
            round(
                humidity,
                2
            ),

        "timestamp":
            datetime.now().isoformat()

    }


# =========================================================
# Apply Watering Effect
# =========================================================

def apply_watering_effect(
    moisture_after_watering
):

    global soil_moisture

    # The virtual plant receives water

    soil_moisture = moisture_after_watering

    print()
    print("======================================")
    print("🚿 AUTOMATIC WATERING")
    print("======================================")

    print(
        f"Soil Moisture Increased To: "
        f"{soil_moisture:.2f}%"
    )

    print(
        "Virtual Pump: ON"
    )

    print(
        "Watering completed."
    )

    print("======================================")


# =========================================================
# Send Sensor Data
# =========================================================

def send_sensor_data(data):

    try:

        response = requests.post(

            API_URL,

            json=data,

            timeout=5

        )

        if response.status_code == 200:

            result = response.json()

            print()
            print("--------------------------------------")
            print("📡 Sensor Data Sent")
            print("--------------------------------------")

            print(
                f"Soil Moisture : "
                f"{data['soil_moisture']:.2f}%"
            )

            print(
                f"Temperature   : "
                f"{data['temperature']:.2f}°C"
            )

            print(
                f"Humidity      : "
                f"{data['humidity']:.2f}%"
            )

            print(
                f"Plant Status  : "
                f"{result['plant_status']}"
            )

            print(
                f"Pump Status   : "
                f"{result['pump_status']}"
            )

            # -------------------------------------------------
            # Check if automatic watering started
            # -------------------------------------------------

            if result.get(
                "watering_started",
                False
            ):

                moisture_after = result[
                    "moisture_after_watering"
                ]

                apply_watering_effect(
                    moisture_after
                )

        else:

            print(
                "Server returned:",
                response.status_code
            )

            print(
                response.text
            )

    except requests.exceptions.ConnectionError:

        print()
        print(
            "❌ ERROR: Backend server "
            "is not running."
        )

    except requests.exceptions.Timeout:

        print()
        print(
            "❌ ERROR: Request timed out."
        )

    except Exception as error:

        print()
        print(
            "❌ ERROR:",
            error
        )


# =========================================================
# Main Simulator
# =========================================================

def main():

    print()
    print("=" * 50)
    print("🌱 SMART PLANT SENSOR SIMULATOR")
    print("=" * 50)

    print(
        f"Device ID : {DEVICE_ID}"
    )

    print(
        f"API       : {API_URL}"
    )

    print(
        f"Interval  : {SEND_INTERVAL} seconds"
    )

    print(
        "Initial Moisture: 55%"
    )

    print("=" * 50)

    print()
    print(
        "Starting virtual plant simulation..."
    )

    print()

    while True:

        sensor_data = (
            generate_sensor_data()
        )

        send_sensor_data(
            sensor_data
        )

        time.sleep(
            SEND_INTERVAL
        )


# =========================================================
# Program Entry
# =========================================================

if __name__ == "__main__":

    main()