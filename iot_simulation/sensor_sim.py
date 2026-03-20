import random, time, json, datetime

BINS = ["Bin_A1", "Bin_B2", "Bin_C3", "Bin_D4", "Bin_E5"]

def simulate_bin_data():
    data = []
    for bin_id in BINS:
        fill = random.uniform(0, 100)  # % full
        waste_type = random.choice(["wet", "dry", "mixed"])
        data.append({
            "bin_id": bin_id,
            "fill_level": round(fill, 2),
            "waste_type": waste_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "location": {
                "lat": round(20.2961 + random.uniform(-0.01, 0.01), 6),
                "lng": round(85.8245 + random.uniform(-0.01, 0.01), 6)
            }
        })
    return data

if __name__ == "__main__":
    while True:
        readings = simulate_bin_data()
        with open("iot_simulation/bin_data.json", "w") as f:
            json.dump(readings, f, indent=2)
        print(f"Updated at {datetime.datetime.now().strftime('%H:%M:%S')}")
        time.sleep(10)  # Update every 10 seconds