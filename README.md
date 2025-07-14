# 🌡️ Loggamera Home Assistant Integration

Integration för att hämta badtemperaturer från Hjo Energis Loggamera IoT-plattform till Home Assistant.

## 📁 Projektstruktur

```
loggamera-home-assistant/
├── custom_components/loggamera/    # 🏠 HOME ASSISTANT INTEGRATION
│   ├── __init__.py                 # Integration setup
│   ├── manifest.json               # HA metadata
│   └── sensor.py                   # Sensor implementation
├── docs/                           # 📚 DOKUMENTATION
│   ├── TEST_GUIDE.md              # Steg-för-steg testguide
│   ├── UTVECKLINGSPLAN.md         # Utvecklingsroadmap
│   ├── INSTALL_HOME_ASSISTANT.md  # Installationsguide
│   └── ha_methods_comparison.md   # Jämförelse av metoder
├── examples/                       # 📋 EXEMPEL & KONFIGURATIONER
│   ├── example_configuration.yaml # Klar HA konfiguration
│   ├── ha_rest_optimized.yaml    # REST sensor alternativ
│   ├── ha_vattern_sensor.py      # Command line script
│   ├── home_assistant_vattern_sensor.yaml
│   └── home_assistant_command_line_sensor.yaml
├── tests/                          # 🧪 TESTER
│   ├── quick_api_test.py          # Snabb API test
│   └── test_loggamera.py          # Unit tests
├── config_flow.py                  # 🔧 Future: GUI setup
└── loggamera_integration_v2.py    # 🚀 Future: Enhanced version
```

## 🚀 Snabbstart

### 1. Installera Custom Integration

Kopiera hela `custom_components/loggamera/` mappen till din Home Assistant:

```bash
# Kopiera till ditt HA system
cp -r custom_components/loggamera /config/custom_components/
```

### 2. Konfigurera

Använd `examples/example_configuration.yaml` som mall:

```yaml
sensor:
  - platform: loggamera
    sensors:
      - name: "Vättern Temperatur"
        location_id: 22
      - name: "Mullsjön Temperatur"
        location_id: 21
```

### 3. Testa

Innan HA-konfiguration, testa API:et:

```bash
cd tests/
python3 quick_api_test.py
```

### 4. Starta om HA

Efter konfiguration, starta om Home Assistant och kontrollera att sensorerna fungerar.

## 📊 Sensordata

Integration hämtar temperaturer från:
- **Vättern**: `location_id: 22` (Hjo Energi)
- **Mullsjön**: `location_id: 21` (Hjo Energi)

**Uppdateringsintervall**: 5 minuter  
**API-endpoint**: `https://portal.loggamera.se/PublicViews/OverviewInside`

## 🔧 Alternativa Metoder

| Metod | Komplexitet | Tillförlitlighet | Rekommendation |
|-------|-------------|------------------|----------------|
| **Custom Integration** | Medium | Hög | ✅ Bäst för avancerad användning |
| **REST Sensor** | Låg | Hög | ✅ Bäst för enkla behov |
| **Command Line** | Medium | Medium | ⚠️ Endast för utveckling |

Se `examples/` för alla metoder.

## 📚 Dokumentation

- **[TEST_GUIDE.md](docs/TEST_GUIDE.md)** - Komplett testguide med felsökning
- **[UTVECKLINGSPLAN.md](docs/UTVECKLINGSPLAN.md)** - Utvecklingsroadmap och arkitektur
- **[INSTALL_HOME_ASSISTANT.md](docs/INSTALL_HOME_ASSISTANT.md)** - Detaljerad installation
- **[ha_methods_comparison.md](docs/ha_methods_comparison.md)** - Metod-jämförelse

## 🧪 Tester

```bash
# API test
cd tests/
python3 quick_api_test.py

# Unit tests (kräver pytest)
python3 -m pytest test_loggamera.py -v
```

## 🚀 Framtida Utveckling

- **v2.0**: Enhanced version med retry logic och caching (`loggamera_integration_v2.py`)
- **Config Flow**: GUI setup i Home Assistant (`config_flow.py`)
- **Flera sensorer**: Utöka till fler Loggamera-sensorer
- **Automation**: Smarta regler baserat på temperatur

## 📞 Support

1. **Kör `quick_api_test.py`** först - löser 80% av problemen
2. **Kontrollera HA loggar** för felmeddelanden
3. **Jämför med REST sensor** i `examples/` som backup
4. **Läs `TEST_GUIDE.md`** för detaljerad felsökning

## 🏷️ Tags

`home-assistant` `loggamera` `hjo-energi` `badtemperatur` `vattern` `iot` `sensors` `custom-integration`

---

**Utvecklad för Hjo Energi AB's Loggamera IoT-plattform**  
Version: 1.0 | Status: Produktionsklar ✅ 