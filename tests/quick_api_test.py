#!/usr/bin/env python3
"""
Snabb test av Loggamera API
Kör detta script för att verifiera att API:et fungerar innan du konfigurerar Home Assistant
"""

import requests
import re
import sys
import json
from datetime import datetime

def test_loggamera_api(location_id):
    """Testa Loggamera API för en specifik location."""
    print(f"🧪 Testar Loggamera API för location {location_id}...")
    
    url = "https://portal.loggamera.se/PublicViews/OverviewInside"
    data = {"id": location_id}
    
    try:
        response = requests.post(url, data=data, timeout=30)
        print(f"✅ HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"📄 Response length: {len(html)} characters")
            
            # Extrahera temperatur med samma regex som integrationen använder
            temp_pattern = r'data-value="(-?\d+\.?\d*)"'
            matches = re.findall(temp_pattern, html)
            
            print(f"🔍 Hittade {len(matches)} data-value attribut")
            
            valid_temps = []
            for match in matches:
                try:
                    temp = float(match)
                    if -5 <= temp <= 40:  # Sanity check som integrationen använder
                        valid_temps.append(temp)
                        print(f"🌡️  Giltig temperatur: {temp}°C")
                    else:
                        print(f"⚠️  Temperatur utanför giltigt intervall: {temp}°C")
                except ValueError:
                    print(f"❌ Kunde inte konvertera '{match}' till nummer")
            
            if valid_temps:
                print(f"✅ SUCCESS: Hittade {len(valid_temps)} giltiga temperaturer")
                print(f"🎯 Första giltiga temperatur: {valid_temps[0]}°C")
                return valid_temps[0]
            else:
                print("❌ FAIL: Inga giltiga temperaturer hittades")
                return None
                
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ FAIL: Timeout vid API-anrop")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Nätverksfel: {e}")
        return None
    except Exception as e:
        print(f"❌ FAIL: Oväntat fel: {e}")
        return None

def test_multiple_locations():
    """Testa flera kända locations."""
    locations = {
        22: "Vättern",
        21: "Mullsjön",
        # Lägg till fler här om du känner till dem
    }
    
    results = {}
    
    print("🚀 Startar test av Loggamera API...\n")
    print("=" * 50)
    
    for location_id, name in locations.items():
        print(f"\n📍 Testar {name} (ID: {location_id})")
        print("-" * 30)
        
        temp = test_loggamera_api(location_id)
        results[location_id] = {
            "name": name,
            "temperature": temp,
            "success": temp is not None
        }
        
        print()
    
    # Sammanfattning
    print("=" * 50)
    print("📊 SAMMANFATTNING")
    print("=" * 50)
    
    success_count = 0
    for location_id, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        temp_str = f"{result['temperature']}°C" if result["temperature"] else "N/A"
        print(f"{result['name']} (ID: {location_id}): {status} - {temp_str}")
        if result["success"]:
            success_count += 1
    
    print(f"\n🎯 {success_count}/{len(results)} locations fungerar")
    
    if success_count > 0:
        print("\n✅ API:et fungerar! Du kan fortsätta med Home Assistant konfiguration.")
        print("📝 Använd example_configuration.yaml som mall")
    else:
        print("\n❌ API:et fungerar inte. Kontrollera nätverksanslutning eller prova senare.")
    
    return results

def generate_ha_config(results):
    """Generera Home Assistant konfiguration baserat på testresultat."""
    successful_locations = [(lid, r) for lid, r in results.items() if r["success"]]
    
    if not successful_locations:
        return None
    
    config = []
    config.append("# Automatiskt genererad Loggamera konfiguration")
    config.append(f"# Genererad: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    config.append("")
    config.append("sensor:")
    config.append("  - platform: loggamera")
    config.append("    sensors:")
    
    for location_id, result in successful_locations:
        config.append(f"      - name: \"{result['name']} Temperatur\"")
        config.append(f"        location_id: {location_id}")
    
    return "\n".join(config)

if __name__ == "__main__":
    print("🌡️ Loggamera API Test Tool")
    print("=" * 50)
    
    # Testa API:et
    results = test_multiple_locations()
    
    # Generera HA config om det finns framgångsrika resultat
    ha_config = generate_ha_config(results)
    if ha_config:
        print("\n📝 FÖRSLAG PÅ HOME ASSISTANT KONFIGURATION:")
        print("-" * 50)
        print(ha_config)
        
        # Spara till fil
        with open("generated_ha_config.yaml", "w", encoding="utf-8") as f:
            f.write(ha_config)
        print(f"\n💾 Konfiguration sparad till: generated_ha_config.yaml")
    
    print("\n🔗 Nästa steg:")
    print("1. Kopiera konfigurationen till din configuration.yaml")
    print("2. Starta om Home Assistant") 
    print("3. Kontrollera loggar och entiteter")
    print("4. Följ TEST_GUIDE.md för detaljerade instruktioner") 