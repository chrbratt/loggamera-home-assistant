"""Constants for the Loggamera integration."""

DOMAIN = "loggamera"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes in seconds
MIN_SCAN_INTERVAL = 60       # 1 minute minimum
MAX_SCAN_INTERVAL = 86400    # 24 hours maximum

# Available sensor locations
SENSORS = {
    22: "Lake Vättern",
    21: "Lake Mullsjön"
} 