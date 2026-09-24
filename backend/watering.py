# Default moisture threshold
DEFAULT_THRESHOLD = 30.0


def check_watering_required(
    soil_moisture,
    threshold=DEFAULT_THRESHOLD
):
    """
    Determine whether watering is required.

    Returns True when soil moisture is below
    the configured threshold.
    """

    return soil_moisture < threshold


def get_plant_status(
    soil_moisture,
    threshold=DEFAULT_THRESHOLD
):
    """Return a simple plant health status."""

    if soil_moisture < threshold:
        return "NEEDS WATER"

    return "HEALTHY"


def get_pump_status(
    soil_moisture,
    threshold=DEFAULT_THRESHOLD
):
    """Return the virtual pump status."""

    if check_watering_required(soil_moisture, threshold):
        return "ON"

    return "OFF"