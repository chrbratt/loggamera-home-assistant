#!/usr/bin/env python3
"""
Home Assistant Command Line Sensor för Vättern badtemperatur
Returnerar bara temperaturvärdet för enkel parsing
"""

import requests
import sys
import re

def get_vattern_temperature():
    """
    Hämtar aktuell temperatur för Vättern och returnerar bara värdet
    """
    try:
        # Hämta data från Loggamera
        url = "https://portal.loggamera.se/PublicViews/OverviewInside"
        data = {'id': 22}
        
        headers = {
            'User-Agent': 'Home Assistant Temperature Sensor',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(url, data=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parsa HTML för temperaturvärden med regex
        temp_pattern = r'data-value="(-?\d+\.?\d*)"'
        matches = re.findall(temp_pattern, response.text)
        
        for match in matches:
            temp = float(match)
            # Sanity check - rimlig temperatur för vatten
            if -5 <= temp <= 40:
                return temp
        
        # Om ingen temperatur hittades
        return None
        
    except requests.RequestException as e:
        print(f"ERROR: Network error - {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Parsing error - {e}", file=sys.stderr)
        return None

def main():
    """
    Huvudfunktion - returnerar temperatur eller 'unavailable'
    """
    temp = get_vattern_temperature()
    
    if temp is not None:
        # Returnera bara temperaturvärdet för Home Assistant
        print(f"{temp:.1f}")
    else:
        print("unavailable")

if __name__ == "__main__":
    main() 