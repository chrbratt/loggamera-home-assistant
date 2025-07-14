# 🏠 Installation: Vättern Badtemperatur i Home Assistant

## 🚀 Metod 1: Command Line Sensor (REKOMMENDERAS)

### Steg 1: Installera Python-script

1. **Kopiera scriptet till Home Assistant:**
```bash
# SSH/Terminal till din Home Assistant
cd /config
wget https://raw.githubusercontent.com/[din-repo]/ha_vattern_sensor.py
# ELLER kopiera innehållet från ha_vattern_sensor.py
```

2. **Installera Python-beroenden:**
```bash
# I Home Assistant container/OS
pip install requests

# ELLER för Home Assistant OS/Supervised:
# Lägg till i configuration.yaml:
python_script:
```

3. **Gör scriptet körbart:**
```bash
chmod +x /config/ha_vattern_sensor.py
```

### Steg 2: Konfigurera sensorn

**Lägg till i `configuration.yaml`:**
```yaml
command_line:
  - sensor:
      name: "Vättern Badtemperatur"
      unique_id: "vattern_badtemperatur"
      command: "python3 /config/ha_vattern_sensor.py"
      unit_of_measurement: "°C"
      device_class: "temperature"
      state_class: "measurement"
      icon: "mdi:waves"
      scan_interval: 300  # 5 minuter
```

### Steg 3: Starta om Home Assistant

```yaml
# Kontrollera konfigurationen först
Developer Tools > Check Configuration

# Starta om
Configuration > Server Controls > Restart
```

---

## 🌐 Metod 2: REST Sensor (Enklare installation)

**Lägg till i `configuration.yaml`:**
```yaml
rest:
  - resource: "https://portal.loggamera.se/PublicViews/OverviewInside"
    method: POST
    payload: "id=22"
    headers:
      Content-Type: "application/x-www-form-urlencoded"
      User-Agent: "Home Assistant"
    scan_interval: 300
    sensor:
      - name: "Vättern Badtemperatur REST"
        unique_id: "vattern_badtemperatur_rest"
        unit_of_measurement: "°C"
        device_class: "temperature"
        state_class: "measurement"
        icon: "mdi:waves"
        value_template: >-
          {% set temp_match = value | regex_findall_index('data-value="([0-9.]+)"') %}
          {% if temp_match %}
            {{ temp_match | float | round(1) }}
          {% else %}
            unavailable
          {% endif %}
```

---

## 📱 Lovelace Dashboard-kort

### Enkelt Sensor-kort
```yaml
type: sensor
entity: sensor.vattern_badtemperatur
name: "🌊 Vättern"
icon: mdi:waves
```

### Gauge-kort (Visar temperatur som mätare)
```yaml
type: gauge
entity: sensor.vattern_badtemperatur
name: "Vättern Badtemperatur"
min: 0
max: 30
severity:
  green: 18
  yellow: 12
  red: 0
```

### Statistik-kort (Visar trends)
```yaml
type: statistics-graph
title: "Badtemperatur - Senaste veckan"
entities:
  - sensor.vattern_badtemperatur
period: week
stat_types:
  - mean
  - min
  - max
```

### Avancerat kort med flera värden
```yaml
type: custom:mushroom-entity-card
entity: sensor.vattern_badtemperatur
name: Vättern
icon: mdi:waves
icon_color: blue
primary_info: name
secondary_info: state
tap_action:
  action: more-info
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
```

---

## 🔧 Felsökning

### Kontrollera att sensorn fungerar:
```bash
# SSH till Home Assistant
python3 /config/ha_vattern_sensor.py
# Borde returnera ett temperaturvärde som "18.5"
```

### Debugging i Home Assistant:
```yaml
# Lägg till i configuration.yaml för debug-loggning
logger:
  default: info
  logs:
    homeassistant.components.command_line: debug
```

### Vanliga problem:

1. **"unavailable"** - Kontrollera internetanslutning och endpoint
2. **Sensorn uppdateras inte** - Kontrollera scan_interval och restart HA
3. **Permission denied** - Kontrollera att scriptet är körbart (`chmod +x`)

---

## 📊 Automatiseringar

### Notifiering vid låg temperatur:
```yaml
automation:
  - alias: "Kallbad Varning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.vattern_badtemperatur
        below: 10
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🥶 Kallt vatten!"
          message: "Vättern är bara {{ states('sensor.vattern_badtemperatur') }}°C"
```

### Daglig temperaturrapport:
```yaml
automation:
  - alias: "Daglig Temperaturrapport"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.family
        data:
          message: >
            🏊‍♀️ God morgon! Vättern har {{ states('sensor.vattern_badtemperatur') }}°C idag.
```

---

## 🚀 Resultat

Efter installation kommer du att ha:

✅ **Sensor**: `sensor.vattern_badtemperatur`  
✅ **Uppdateringsfrekvens**: Var 5:e minut  
✅ **Enhet**: °C  
✅ **Device Class**: Temperature (för automationer)  
✅ **Ikon**: 🌊 (vågor)  

Sensorn kan nu användas i:
- Dashboard-kort
- Automatiseringar  
- Notifieringar
- Statistik och grafer
- Röststyrning ("Hey Google, vad är vattentemperaturen?")

---

**🎉 Nu har du Vätterns badtemperatur direkt i Home Assistant!** 