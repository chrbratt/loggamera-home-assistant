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

## 📊 Statistik och medelvärden

För dygns- och veckomedelvärden använd Home Assistant's inbyggda statistik-integration:

### Steg 1: Aktivera statistik-integrationen
1. Gå till **Inställningar → Enheter & tjänster → Lägg till integration**
2. Sök efter **"Statistik"** och lägg till den

### Steg 2: Skapa statistik-sensorer via UI
1. Gå till **Inställningar → Enheter & tjänster → Hjälpare**
2. Sök efter **"Statistik"** och klicka på det
3. Fyll i följande för varje sensor:

**Vättern Dygnsmedelvärde:**
- **Entity ID:** `sensor.vattern_badtemperatur`
- **Name:** `Vättern Dygnsmedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `288` (5-minutersintervall på ett dygn)

**Mullsjön Dygnsmedelvärde:**
- **Entity ID:** `sensor.mullsjon_badtemperatur`
- **Name:** `Mullsjön Dygnsmedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `288`

**Vättern Veckomedelvärde:**
- **Entity ID:** `sensor.vattern_badtemperatur`
- **Name:** `Vättern Veckomedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `2016` (5-minutersintervall på en vecka)

**Mullsjön Veckomedelvärde:**
- **Entity ID:** `sensor.mullsjon_badtemperatur`
- **Name:** `Mullsjön Veckomedelvärde`
- **State Characteristic:** `mean`
- **Sampling Size:** `2016`

### Steg 3: Visa i Lovelace
Lägg till en "Sensor card" och välj t.ex. `sensor.vattern_dygnsmedelvarde` eller `sensor.mullsjon_veckomedelvarde`.

### Tillgängliga sensorer
- `sensor.vattern_badtemperatur` - Aktuell temperatur Vättern
- `sensor.mullsjon_badtemperatur` - Aktuell temperatur Mullsjön
- `sensor.vattern_dygnsmedelvarde` - Dygnsmedelvärde Vättern
- `sensor.mullsjon_dygnsmedelvarde` - Dygnsmedelvärde Mullsjön
- `sensor.vattern_veckomedelvarde` - Veckomedelvärde Vättern
- `sensor.mullsjon_veckomedelvarde` - Veckomedelvärde Mullsjön

Detta ger dig korrekta dygns- och veckomedelvärden med Home Assistant's beprövade statistik-motor.

Data from Hjo Energi AB's public temperature sensors. 