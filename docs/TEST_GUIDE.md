# 🧪 Test Guide - Loggamera Integration

## 📁 Steg 1: Kontrollera Filstruktur

Din `custom_components/loggamera/` mapp ska innehålla:

```
custom_components/loggamera/
├── __init__.py           ✅ (Skapad)
├── manifest.json         ✅ (Skapad)  
├── sensor.py            ✅ (Skapad)
└── loggamera_integration.py  (Din ursprungliga fil)
```

## ⚙️ Steg 2: Konfigurera Integration

### Option A: YAML Konfiguration (Enklast att testa)

Lägg till detta i din `configuration.yaml`:

```yaml
# Loggamera Temperature Sensors
sensor:
  - platform: loggamera
    sensors:
      - name: "Vättern Temperatur"
        location_id: 22
      - name: "Mullsjön Temperatur"  
        location_id: 21
```

### Option B: REST Sensor (Alternativ för jämförelse)

```yaml
# REST sensor för jämförelse
rest:
  - resource: "https://portal.loggamera.se/PublicViews/OverviewInside"
    method: POST
    payload: "id=22"
    headers:
      Content-Type: "application/x-www-form-urlencoded"
    sensor:
      - name: "Vättern REST"
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

## 🔄 Steg 3: Starta om Home Assistant

1. **Kontrollera konfiguration först:**
   - Gå till `Developer Tools` → `Check Configuration`
   - Se till att det inte finns några YAML-fel

2. **Starta om:**
   - `Settings` → `System` → `Restart`
   - Eller via terminalen: `sudo systemctl restart home-assistant@homeassistant.service`

## 🔍 Steg 4: Kontrollera att Integration Laddat

### Kontrollera Loggar

Öppna loggar: `Settings` → `System` → `Logs`

**Sök efter:**
```
Setting up Loggamera integration
Setting up Loggamera config entry  
```

**Eller via terminal:**
```bash
tail -f /home/homeassistant/.homeassistant/home-assistant.log | grep -i loggamera
```

### Kontrollera Entiteter

1. Gå till `Settings` → `Devices & Services` → `Entities`
2. Sök efter "loggamera" eller "vättern"
3. Du bör se sensors som:
   - `sensor.vattern_temperatur`
   - `sensor.mullsjon_temperatur`

## 📊 Steg 5: Testa Funktionalitet

### Kontrollera Sensor States

1. **Developer Tools** → **States**
2. Sök efter dina sensorer
3. Kontrollera att de har värden (inte `unknown` eller `unavailable`)

### Kontrollera i Dashboard

Lägg till ett kort i Lovelace:

```yaml
type: entities
entities:
  - entity: sensor.vattern_temperatur
    name: Vättern
  - entity: sensor.mullsjon_temperatur  
    name: Mullsjön
title: Badtemperaturer
```

## 🐛 Steg 6: Felsökning

### Vanliga Problem & Lösningar

#### Problem 1: "Integration not found"
**Orsak:** Felaktig filstruktur eller imports

**Lösning:**
```bash
# Kontrollera filstruktur
ls -la custom_components/loggamera/

# Kontrollera att __init__.py finns
cat custom_components/loggamera/__init__.py
```

#### Problem 2: "Platform loggamera not found"
**Orsak:** sensor.py saknas eller är fel

**Lösning:**
```bash
# Kontrollera sensor.py
ls -la custom_components/loggamera/sensor.py
```

#### Problem 3: Sensorer visar "unknown"
**Orsak:** API-fel eller parsing-problem

**Debugging:**
```bash
# Testa API manuellt
curl -X POST https://portal.loggamera.se/PublicViews/OverviewInside \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "id=22"
```

#### Problem 4: Import errors i loggar
**Orsak:** Dependencies saknas

**Lösning:**
```bash
# Installera dependencies (om det behövs)
pip3 install aiohttp voluptuous beautifulsoup4
```

### Debug-loggning

Lägg till i `configuration.yaml` för detaljerad loggning:

```yaml
logger:
  default: info
  logs:
    custom_components.loggamera: debug
    homeassistant.components.sensor: debug
```

## ✅ Steg 7: Verifiera Framgång

**Integration fungerar om:**

1. ✅ Inga fel i loggar
2. ✅ Sensorer visas i entitets-listan  
3. ✅ Sensorer har numeriska temperaturer (inte unknown)
4. ✅ Sensorer uppdateras var 5:e minut
5. ✅ Device visas under `Devices & Services`

### Exempel på Fungerande Sensor:

```yaml
State: 19.4
Attributes:
  unit_of_measurement: °C
  device_class: temperature
  state_class: measurement
  location_id: 22
  source: Loggamera Portal
  friendly_name: Vättern Temperatur
```

## 🚀 Nästa Steg

När basic integration fungerar:

1. **Testa fler locations** (id: 21, 22, etc.)
2. **Skapa automatiseringar** baserat på temperatur
3. **Lägg till i dashboard** med grafer
4. **Uppgradera till v2.0** för bättre funktioner

## 📞 Support

**Om du stöter på problem:**

1. Kontrollera denna guide igen
2. Kolla Home Assistant loggar
3. Testa REST sensor som backup
4. Jämför med fungerande setup i `ha_rest_optimized.yaml`

**Debug-kommando för manuell test:**
```bash
# Testa Vättern (id=22)
curl -X POST "https://portal.loggamera.se/PublicViews/OverviewInside" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "id=22" | grep -o 'data-value="[^"]*"'
```

Lycka till med testningen! 🌡️💧 