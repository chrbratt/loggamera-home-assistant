# 🌡️ Loggamera Home Assistant Integration

Home Assistant custom integration for retrieving water temperature data from Hjo Energi's Loggamera IoT platform.

## 📁 Project Structure

```
loggamera-home-assistant/
├── custom_components/loggamera/    # 🏠 HOME ASSISTANT INTEGRATION
│   ├── __init__.py                 # Integration setup
│   ├── manifest.json               # HA metadata
│   └── sensor.py                   # Sensor implementation
├── docs/                           # 📚 DOCUMENTATION
│   ├── TEST_GUIDE.md              # Step-by-step testing guide
│   ├── UTVECKLINGSPLAN.md         # Development roadmap
│   ├── INSTALL_HOME_ASSISTANT.md  # Installation guide
│   └── ha_methods_comparison.md   # Method comparison
├── examples/                       # 📋 EXAMPLES & CONFIGURATIONS
│   ├── example_configuration.yaml # Ready HA configuration
│   ├── ha_rest_optimized.yaml    # REST sensor alternative
│   ├── ha_vattern_sensor.py      # Command line script
│   ├── home_assistant_vattern_sensor.yaml
│   └── home_assistant_command_line_sensor.yaml
├── tests/                          # 🧪 TESTS
│   ├── quick_api_test.py          # Quick API test
│   └── test_loggamera.py          # Unit tests
├── config_flow.py                  # 🔧 Future: GUI setup
└── loggamera_integration_v2.py    # 🚀 Future: Enhanced version
```

## 🚀 Quick Start

### 1. Install via HACS (Recommended)

**Option A: HACS Custom Repository**
1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add repository: `chrbratt/loggamera-home-assistant`
4. Category: `Integration`
5. Install "Loggamera Temperature Sensors"

**Option B: Manual Installation**
```bash
# Copy to your HA system
cp -r custom_components/loggamera /config/custom_components/
```

### 2. Configuration

Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: loggamera
    sensors:
      - name: "Lake Vättern Temperature"
        location_id: 22
        scan_interval: 300  # 5 minutes (60-43200 seconds)
      - name: "Lake Mullsjön Temperature"
        location_id: 21
        scan_interval: 600  # 10 minutes
```

### 3. Test API Connection

Before configuring HA, test the API:

```bash
cd tests/
python3 quick_api_test.py
```

### 4. Restart Home Assistant

After configuration, restart Home Assistant and verify sensors are working.

## 📊 Sensor Data

Integration retrieves temperatures from:
- **Lake Vättern**: `location_id: 22` (Hjo Energi)
- **Lake Mullsjön**: `location_id: 21` (Hjo Energi)

**Default Update Interval**: 5 minutes  
**Configurable Range**: 1 minute - 12 hours (60-43200 seconds)  
**API Endpoint**: `https://portal.loggamera.se/PublicViews/OverviewInside`

## ⚙️ Configuration Options

| Option | Required | Default | Range | Description |
|--------|----------|---------|-------|-------------|
| `name` | Yes | - | - | Sensor display name |
| `location_id` | Yes | - | 21, 22 | Loggamera location ID |
| `scan_interval` | No | 300 | 60-43200 | Update interval in seconds |
| `unit` | No | °C | - | Temperature unit |

## 🔧 Alternative Methods

| Method | Complexity | Reliability | Recommendation |
|--------|------------|-------------|----------------|
| **Custom Integration** | Medium | High | ✅ Best for advanced use |
| **REST Sensor** | Low | High | ✅ Best for simple needs |
| **Command Line** | Medium | Medium | ⚠️ Development only |

See `examples/` for all methods.

## 📚 Documentation

- **[TEST_GUIDE.md](docs/TEST_GUIDE.md)** - Complete testing guide with troubleshooting
- **[UTVECKLINGSPLAN.md](docs/UTVECKLINGSPLAN.md)** - Development roadmap and architecture
- **[INSTALL_HOME_ASSISTANT.md](docs/INSTALL_HOME_ASSISTANT.md)** - Detailed installation
- **[ha_methods_comparison.md](docs/ha_methods_comparison.md)** - Method comparison

## 🧪 Testing

```bash
# API test
cd tests/
python3 quick_api_test.py

# Unit tests (requires pytest)
python3 -m pytest test_loggamera.py -v
```

## 🚀 Future Development

- **v2.0**: Enhanced version with retry logic and caching (`loggamera_integration_v2.py`)
- **Config Flow**: GUI setup in Home Assistant (`config_flow.py`)
- **Multiple Sensors**: Expand to more Loggamera sensors
- **Automation**: Smart rules based on temperature

## 📞 Support

1. **Run `quick_api_test.py`** first - solves 80% of issues
2. **Check HA logs** for error messages
3. **Compare with REST sensor** in `examples/` as backup
4. **Read `TEST_GUIDE.md`** for detailed troubleshooting

## 🏷️ HACS Integration

This integration is compatible with:
- **Home Assistant**: 2023.1+
- **HACS**: Custom repository support
- **Python**: 3.9+

To add as HACS custom repository:
```
Repository: chrbratt/loggamera-home-assistant
Category: Integration
```

## 📋 Changelog

### v1.0.0
- Initial release
- Support for Vättern and Mullsjön temperature sensors
- Configurable update intervals (1 min - 12 hours)
- HACS compatibility
- English documentation

## 🏷️ Tags

`home-assistant` `hacs` `loggamera` `hjo-energi` `water-temperature` `vattern` `iot` `sensors` `custom-integration` `sweden`

---

**Developed for Hjo Energi AB's Loggamera IoT Platform**  
Version: 1.0.0 | Status: Production Ready ✅ | HACS Compatible 🏪 