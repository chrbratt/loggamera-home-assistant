# 📊 Guide: Statistik för badtemperaturer

Denna guide visar hur du lägger till dygns- och veckomedelvärden för dina badtemperatur-sensorer.

## Snabbstart (3 steg)

### 1. Aktivera statistik-integrationen
- Gå till **Inställningar → Enheter & tjänster → Lägg till integration**
- Sök efter **"Statistik"** och lägg till den

### 2. Skapa statistik-sensorer via UI
1. Gå till **Inställningar → Enheter & tjänster → Hjälpare**
2. Sök efter **"Statistik"** och klicka på det
3. Fyll i följande för varje sensor:

#### Vättern Dygnsmedelvärde:
- **Entity ID:** `sensor.vattern_badtemperatur`
- **Name:** `Vättern Dygnsmedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `288` (5-minutersintervall på ett dygn)

#### Mullsjön Dygnsmedelvärde:
- **Entity ID:** `sensor.mullsjon_badtemperatur`
- **Name:** `Mullsjön Dygnsmedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `288`

#### Vättern Veckomedelvärde:
- **Entity ID:** `sensor.vattern_badtemperatur`
- **Name:** `Vättern Veckomedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `2016` (5-minutersintervall på en vecka)

#### Mullsjön Veckomedelvärde:
- **Entity ID:** `sensor.mullsjon_badtemperatur`
- **Name:** `Mullsjön Veckomedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `2016`

### 3. Sensorerna skapas automatiskt
Efter att du fyllt i formuläret och sparat skapas sensorerna automatiskt.

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
- Kontrollera att du använt rätt Entity ID
- Kontrollera att ursprungssensorerna finns

**Problem:** Inga värden visas
- Vänta några timmar för att samla in data
- Kontrollera att ursprungssensorerna fungerar

## Avancerade inställningar

### Anpassa samplingsintervall
För 10-minutersintervall istället för 5-minuter, använd:
- **Sampling Size:** `144` (24h * 6 per timme)

### Lägg till min/max-värden
Skapa nya statistik-sensorer via UI med:
- **State Characteristic:** `max` eller `min`
- **Name:** `Vättern Dygns Maximum` eller `Vättern Dygns Minimum`

## Varför använda Home Assistant's statistik?

- ✅ **Beprövad teknologi** - Används av tusentals användare
- ✅ **Automatisk historik** - Integrerar med Home Assistant's databas
- ✅ **Flexibel** - Stödjer medelvärde, min, max, standardavvikelse
- ✅ **Effektiv** - Optimerad för prestanda och minnesanvändning
- ✅ **Framtidsäkert** - Uppdateras automatiskt med Home Assistant

---

*För support, se [GitHub Issues](https://github.com/chrbratt/loggamera-home-assistant/issues)* 