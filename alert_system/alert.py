import math
import json
import datetime
import os

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "latest_alerts.json")

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = (math.sin(dphi/2)**2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2)
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def get_alerts_for_citizen(citizen_lat, citizen_lng,
                            bins_data, radius_m=500):
    alerts = []
    for b in bins_data:
        dist = haversine_distance(
            citizen_lat, citizen_lng,
            b["location"]["lat"], b["location"]["lng"]
        )
        if dist <= radius_m and b["fill_level"] > 60:
            eta = max(1, dist // 80)
            alerts.append({
                "bin_id":      b["bin_id"],
                "zone":        b.get("zone", ""),
                "distance_m":  dist,
                "fill_level":  b["fill_level"],
                "waste_type":  b["waste_type"],
                "message": (
                    f"Garbage truck arriving near {b['bin_id']} "
                    f"({b.get('zone','')})! "
                    f"Please dispose waste now. ETA: ~{eta} min."
                ),
                "timestamp": datetime.datetime.now().isoformat()
            })
    alerts.sort(key=lambda x: x["distance_m"])
    with open(OUTPUT_FILE, "w") as f:
        json.dump(alerts, f, indent=2)
    return alerts
if __name__ == "__main__":
    sample_bins = [
        {"bin_id": "Bin_A1", "zone": "Gate-1", "fill_level": 85,
         "waste_type": "wet",
         "location": {"lat": 20.2961, "lng": 85.8245}},
        {"bin_id": "Bin_B2", "zone": "Academic", "fill_level": 20,
         "waste_type": "dry",
         "location": {"lat": 20.3100, "lng": 85.8400}},
    ]
    result = get_alerts_for_citizen(20.2965, 85.8250, sample_bins)
    print(json.dumps(result, indent=2))