# Badtemperaturer Hjo Energi

Home Assistant integration för badtemperaturer från Hjo Energi AB:s sjöar.

## Installation

### HACS
1. HACS → Integrations → ⋮ → Custom repositories
2. Lägg till: `chrbratt/loggamera-home-assistant`
3. Installera "Badtemperaturer Hjo Energi"
4. Starta om Home Assistant

### Konfiguration
1. **Inställningar** → **Enheter & tjänster** → **Lägg till integration**
2. Sök efter "Badtemperaturer Hjo Energi"
3. Välj sjöar:
   - Vättern
   - Mullsjön
4. Färdig!

## Data
- **Vättern**: Badtemperatur från sjön Vättern
- **Mullsjön**: Badtemperatur från Mullsjön
- **Uppdatering**: Var 5:e minut som standard
- **Källa**: Hjo Energi AB via Loggamera

Data från Hjo Energi AB:s offentliga temperatursensorer. 