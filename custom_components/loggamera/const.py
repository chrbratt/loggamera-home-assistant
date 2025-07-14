"""Constants for the Loggamera integration."""

DOMAIN = "loggamera"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes in seconds
MIN_SCAN_INTERVAL = 60       # 1 minute minimum
MAX_SCAN_INTERVAL = 86400    # 24 hours maximum

# Device information constants
DEVICE_IDENTIFIER = "hjo_energi_badtemperaturer"
DEVICE_NAME = "Hjo Energi Badtemperaturer"
DEVICE_MANUFACTURER = "chrbratt"
DEVICE_MODEL = "Loggamera Temperatursensorer from Hjo Energi AB"
DEVICE_SW_VERSION = "1.0.8"

# Available sensor locations
SENSORS = {
    22: "Lake Vättern",
    21: "Lake Mullsjön"
} 