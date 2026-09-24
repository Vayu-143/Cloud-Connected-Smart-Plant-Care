import sqlite3
from pathlib import Path
from datetime import datetime


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DATABASE_PATH = BASE_DIR / "data" / "plant.db"


def get_connection():
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create required database tables."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    # Sensor readings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            soil_moisture REAL NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Watering events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watering_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            moisture_before REAL NOT NULL,
            moisture_after REAL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_sensor_reading(
    device_id,
    soil_moisture,
    temperature,
    humidity,
    timestamp=None
):
    """Save a sensor reading to the database."""

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sensor_readings
        (
            device_id,
            soil_moisture,
            temperature,
            humidity,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        device_id,
        soil_moisture,
        temperature,
        humidity,
        timestamp
    ))

    connection.commit()
    connection.close()


def get_latest_reading(device_id="PLANT-001"):
    """Return the latest sensor reading."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM sensor_readings
        WHERE device_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (device_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def get_sensor_history(device_id="PLANT-001", limit=50):
    """Return recent sensor readings."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM sensor_readings
        WHERE device_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (device_id, limit))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in reversed(rows)]


def save_watering_event(
    device_id,
    trigger_type,
    moisture_before,
    moisture_after=None
):
    """Save a watering event."""

    timestamp = datetime.now().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO watering_events
        (
            device_id,
            trigger_type,
            moisture_before,
            moisture_after,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        device_id,
        trigger_type,
        moisture_before,
        moisture_after,
        timestamp
    ))

    connection.commit()
    connection.close()


def get_watering_history(device_id="PLANT-001", limit=20):
    """Return recent watering events."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM watering_events
        WHERE device_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (device_id, limit))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in reversed(rows)]