import datetime

BIOGAS_PER_KG  = 0.30
KWH_PER_M3     = 2.00
CO2_FACTOR     = 0.82
BULB_WATTS     = 10

def calculate_biogas(wet_waste_kg):
    if wet_waste_kg <= 0:
        return {"error": "wet_waste_kg must be greater than 0"}
    biogas_m3   = round(wet_waste_kg * BIOGAS_PER_KG, 2)
    electricity = round(biogas_m3 * KWH_PER_M3, 2)
    co2_saved   = round(electricity * CO2_FACTOR, 2)
    bulb_hours  = round(electricity * 1000 / BULB_WATTS)
    homes       = round(electricity / 3.5, 2)
    return {
        "wet_waste_input_kg":       wet_waste_kg,
        "biogas_produced_m3":       biogas_m3,
        "electricity_kwh":          electricity,
        "co2_saved_kg":             co2_saved,
        "equivalent_led_bulb_hours": bulb_hours,
         "homes_powered_for_day":    homes,
        "calculated_at":            datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    import json
    print("--- 50 kg wet waste ---")
    print(json.dumps(calculate_biogas(50), indent=2))
    print("--- 200 kg wet waste ---")
    print(json.dumps(calculate_biogas(200), indent=2))