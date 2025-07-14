# 🏠 Installation till Home Assistant

## Vad ska kopieras

Endast innehållet i `custom_components/loggamera/` mappen behöver laddas upp till Home Assistant:

```
custom_components/loggamera/
├── __init__.py       # Required
├── manifest.json     # Required  
└── sensor.py        # Required
```

## Installationssteg

### 1. Kopiera till Home Assistant

**Metod A: HACS (Rekommenderat om du använder HACS)**
- Lägg till som custom repository
- Installera via HACS interface

**Metod B: Manuell installation**
```bash
# På ditt Home Assistant system
mkdir -p /config/custom_components/loggamera
cp custom_components/loggamera/* /config/custom_components/loggamera/
```

**Metod C: Samba/Fildelning**
- Navigera till `/config/custom_components/`
- Skapa mapp `loggamera`
- Kopiera de 3 filerna dit

### 2. Konfiguration

Lägg till i din `configuration.yaml`:

```yaml
sensor:
  - platform: loggamera
    sensors:
      - name: "Vättern Temperatur"
        location_id: 22
      - name: "Mullsjön Temperatur"
        location_id: 21
```

### 3. Starta om

Starta om Home Assistant för att ladda den nya integrationen.

### 4. Kontrollera

- Gå till `Settings` → `Devices & Services` → `Entities`
- Sök efter "Vättern" eller "loggamera"
- Verifiera att sensorerna har temperaturvärden

## Felsökning

Om det inte fungerar:
1. Kontrollera HA loggar: `Settings` → `System` → `Logs`
2. Sök efter "loggamera" i loggarna
3. Testa API:et först med `tests/quick_api_test.py`
4. Använd REST sensor som backup (se `examples/`)

## Backup-metod (REST Sensor)

Om custom integration inte fungerar, använd denna enklare metod i `configuration.yaml`:

```yaml
rest:
  - resource: "https://portal.loggamera.se/PublicViews/OverviewInside"
    method: POST
    payload: "id=22"
    headers:
      Content-Type: "application/x-www-form-urlencoded"
    scan_interval: 300
    sensor:
      - name: "Vättern Temperatur"
        value_template: >-
          {% set ns = namespace(temp=None) %}
          {% for line in value.split('\n') %}
            {% set match = line | regex_findall('data-value="(-?\d+\.?\d*)"') %}
            {% if match %}
              {% set temp_val = match[0] | float %}
              {% if -5 <= temp_val <= 40 %}
                {% set ns.temp = temp_val %}
                {% break %}
              {% endif %}
            {% endif %}
          {% endfor %}
          {{ ns.temp }}
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
```

## Version Information

- **Current**: v1.0 (Basic integration)
- **Future**: v2.0 (Enhanced med retry/caching i `loggamera_integration_v2.py`)
- **HA Version**: Kompatibel med HA 2023.1+ 