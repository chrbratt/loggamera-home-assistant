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

Data from Hjo Energi AB's public temperature sensors. 