# Loggamera Home Assistant Integration

Home Assistant integration for Hjo Energi's Loggamera water temperature sensors.

## Features

- Water temperature monitoring for Lake Vättern and Lake Mullsjön
- Configurable update intervals (1 minute to 24 hours)
- Easy setup through Home Assistant UI
- HACS compatible

## Installation

### Via HACS

1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `chrbratt/loggamera-home-assistant`
4. Category: `Integration`
5. Install "Loggamera Temperature Sensors"
6. Restart Home Assistant

### Manual Installation

1. Download and extract to `custom_components/loggamera/`
2. Restart Home Assistant

## Configuration

### Using the UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Loggamera"
4. Select which sensors you want:
   - ☐ Lake Vättern (ID: 22)
   - ☐ Lake Mullsjön (ID: 21)
5. Choose update interval
6. Click **Submit**

Your sensors will appear automatically.

### Legacy YAML Configuration

*YAML configuration is deprecated but still supported:*

```yaml
sensor:
  - platform: loggamera
    sensors:
      - name: "Lake Vättern Temperature"
        location_id: 22
        scan_interval: 300
      - name: "Lake Mullsjön Temperature"
        location_id: 21
        scan_interval: 600
```

## Available Sensors

| Location | ID | 
|----------|-----|
| Lake Vättern | 22 |
| Lake Mullsjön | 21 |

## Update Intervals

- 1 minute to 24 hours
- Default: 5 minutes
- Configurable per setup

## Requirements

- Home Assistant 2023.1+
- Internet connection

## Support

For issues, use the [GitHub issue tracker](https://github.com/chrbratt/loggamera-home-assistant/issues).

## License

This integration provides water temperature monitoring from Hjo Energi AB's lakes using their Loggamera IoT sensor platform. Specifically designed for accessing public water temperature data from Lake Vättern and Lake Mullsjön in Sweden.

---
**Version**: 1.0.1 | HACS Compatible 