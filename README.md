# Loggamera Home Assistant Integration

A professional Home Assistant integration for retrieving water temperature data from Hjo Energi's Loggamera IoT sensors.

## Features

- Real-time water temperature monitoring
- Configurable update intervals (1 minute to 12 hours)
- Support for multiple sensor locations
- HACS compatible
- Reliable error handling and logging

## Installation

### Via HACS (Recommended)

1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `chrbratt/loggamera-home-assistant`
4. Category: `Integration`
5. Install "Loggamera Temperature Sensors"

### Manual Installation

1. Download and extract to `custom_components/loggamera/`
2. Restart Home Assistant

## Configuration

Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: loggamera
    sensors:
      - name: "Lake Vättern Temperature"
        location_id: 22
        scan_interval: 300  # Optional: 60-43200 seconds
      - name: "Lake Mullsjön Temperature"
        location_id: 21
        scan_interval: 600
```

## Available Sensors

| Location | ID | Description |
|----------|-----|-------------|
| Lake Vättern | 22 | Main lake temperature sensor |
| Lake Mullsjön | 21 | Secondary lake temperature sensor |

## Configuration Options

| Parameter | Required | Default | Range | Description |
|-----------|----------|---------|-------|-------------|
| `name` | Yes | - | - | Sensor display name |
| `location_id` | Yes | - | 21, 22 | Sensor location identifier |
| `scan_interval` | No | 300 | 60-43200 | Update frequency in seconds |

## Requirements

- Home Assistant 2023.1+
- Internet connection
- HACS (recommended)

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/chrbratt/loggamera-home-assistant/issues).

## License

This integration provides water temperature monitoring from Hjo Energi AB's lakes using their Loggamera IoT sensor platform. Specifically designed for accessing public water temperature data from Lake Vättern and Lake Mullsjön in Sweden.

---
**Version**: 1.0.0 | **HACS Compatible** ✅ 