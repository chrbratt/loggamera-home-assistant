# 📊 Guide: Statistik för badtemperaturer

Denna guide visar hur du lägger till dygns- och veckomedelvärden för dina badtemperatur-sensorer.

## Snabbstart (3 steg)

### 1. Aktivera statistik-integrationen
- Gå till **Inställningar → Enheter & tjänster → Lägg till integration**
- Sök efter **"Statistik"** och lägg till den

### 2. Lägg till YAML-kod
Kopiera och klistra in detta i din `configuration.yaml`:

```yaml
# Dygnsmedelvärde (24h)
sensor:
  - platform: statistics
    name: "Vättern Dygnsmedelvärde"
    entity_id: sensor.vattern_badtemperatur
    state_characteristic: mean
    sampling_size: 288  # 5-minutersintervall på ett dygn

  - platform: statistics
    name: "Mullsjön Dygnsmedelvärde"
    entity_id: sensor.mullsjon_badtemperatur
    state_characteristic: mean
    sampling_size: 288

# Veckomedelvärde (7 dagar)
  - platform: statistics
    name: "Vättern Veckomedelvärde"
    entity_id: sensor.vattern_badtemperatur
    state_characteristic: mean
    sampling_size: 2016  # 5-minutersintervall på en vecka

  - platform: statistics
    name: "Mullsjön Veckomedelvärde"
    entity_id: sensor.mullsjon_badtemperatur
    state_characteristic: mean
    sampling_size: 2016
```

### 3. Starta om Home Assistant
Efter att du lagt till koden, starta om Home Assistant för att aktivera sensorerna.

## Tillgängliga sensorer

| Sensor | Beskrivning |
|--------|-------------|
| `sensor.vattern_badtemperatur` | Aktuell temperatur Vättern |
| `sensor.mullsjon_badtemperatur` | Aktuell temperatur Mullsjön |
| `sensor.vattern_dygnsmedelvarde` | Dygnsmedelvärde Vättern |
| `sensor.mullsjon_dygnsmedelvarde` | Dygnsmedelvärde Mullsjön |
| `sensor.vattern_veckomedelvarde` | Veckomedelvärde Vättern |
| `sensor.mullsjon_veckomedelvarde` | Veckomedelvärde Mullsjön |

## Visa i Lovelace

1. Gå till **Översikt → Redigera dashboard**
2. Klicka **+ Lägg till kort**
3. Välj **Sensor**
4. Välj en av statistik-sensorerna, t.ex. `sensor.vattern_dygnsmedelvarde`

## Felsökning

**Problem:** Sensorer visas inte
- Kontrollera att statistik-integrationen är aktiverad
- Kontrollera att YAML-syntaxen är korrekt
- Starta om Home Assistant

**Problem:** Inga värden visas
- Vänta några timmar för att samla in data
- Kontrollera att ursprungssensorerna fungerar

## Avancerade inställningar

### Anpassa samplingsintervall
```yaml
# För 10-minutersintervall istället för 5-minuter
sampling_size: 144  # 24h * 6 per timme
```

### Lägg till min/max-värden
```yaml
- platform: statistics
  name: "Vättern Dygns Maximum"
  entity_id: sensor.vattern_badtemperatur
  state_characteristic: max
  sampling_size: 288
```

## Varför använda Home Assistant's statistik?

- ✅ **Beprövad teknologi** - Används av tusentals användare
- ✅ **Automatisk historik** - Integrerar med Home Assistant's databas
- ✅ **Flexibel** - Stödjer medelvärde, min, max, standardavvikelse
- ✅ **Effektiv** - Optimerad för prestanda och minnesanvändning
- ✅ **Framtidsäkert** - Uppdateras automatiskt med Home Assistant

---

*För support, se [GitHub Issues](https://github.com/chrbratt/loggamera-home-assistant/issues)* 