# Badtemperaturer Hjo Energi

Home Assistant integration for water temperatures from Hjo Energi AB's lakes.

## Installation

### HACS
1. HACS → Integrations → ⋮ → Custom repositories
2. Add: `chrbratt/loggamera-home-assistant`
3. Install "Badtemperaturer Hjo Energi"
4. Restart Home Assistant

### Configuration
1. **Settings** → **Devices & services** → **Add integration**
2. Search for "Badtemperaturer Hjo Energi"
3. Select lakes:
   - Vättern
   - Mullsjön
4. Done!

## Data
- **Vättern**: Water temperature from Lake Vättern
- **Mullsjön**: Water temperature from Lake Mullsjön  
- **Updates**: Every 5 minutes by default
- **Source**: Hjo Energi AB via Loggamera

## Statistics

For daily and weekly averages, use Home Assistant's built-in Statistics integration:

### Enable Statistics
1. **Settings** → **Devices & services** → **Add integration**
2. Search for "Statistics"
3. Add the integration

### Configure Statistics for Lakes
Add to your `configuration.yaml`:

```yaml
# Daily averages
sensor:
  - platform: statistics
    name: "Vättern Dygnsmedelvärde"
    entity_id: sensor.vattern_badtemperatur
    state_characteristic: mean
    sampling_size: 288  # 5-min intervals per day

  - platform: statistics
    name: "Mullsjön Dygnsmedelvärde"
    entity_id: sensor.mullsjon_badtemperatur
    state_characteristic: mean
    sampling_size: 288

# Weekly averages
  - platform: statistics
    name: "Vättern Veckomedelvärde"
    entity_id: sensor.vattern_badtemperatur
    state_characteristic: mean
    sampling_size: 2016  # 5-min intervals per week

  - platform: statistics
    name: "Mullsjön Veckomedelvärde"
    entity_id: sensor.mullsjon_badtemperatur
    state_characteristic: mean
    sampling_size: 2016
```

This provides accurate daily and weekly averages using Home Assistant's proven statistics engine.

Data from Hjo Energi AB's public temperature sensors. 