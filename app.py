import sys
import os
import json
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from iot_simulation.sensor_sim import simulate_bin_data
from ml_model.predictor        import predict_overflow, optimize_route
from alert_system.alert        import get_alerts_for_citizen
from biogas_module.biogas_calc import calculate_biogas

app = Flask(__name__)

# Replace with your actual Vercel URL for better security
#CORS(app, resources={r"/api/*": {"origins": "https://hack4-impact-track2-dna-j8fj.vercel.app/"}})
CORS(app, origins=["https://hack4-impact-track2-dna-j8fj.vercel.app",
                   "https://hack4-impact-track2-dna-j8fj-1jpoj16q6-anjalijais1412s-projects.vercel.app"])

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

rewards = {}

@app.route("/")
def index():
    return send_from_directory(DASHBOARD_DIR, "index.html")

@app.route("/dashboard/<path:filename>")
def dashboard_files(filename):
    return send_from_directory(DASHBOARD_DIR, filename)

@app.route("/api/bins")
def get_bins():
    data = simulate_bin_data()
    for b in data:
        b["prediction"] = predict_overflow(b["fill_level"])
    return jsonify(data)

@app.route("/api/route")
def get_route():
    return jsonify(optimize_route(simulate_bin_data()))

@app.route("/api/alerts")
def get_alerts():
    lat = float(request.args.get("lat", 20.2961))
    lng = float(request.args.get("lng", 85.8245))
    return jsonify(get_alerts_for_citizen(lat, lng, simulate_bin_data()))

@app.route("/api/biogas")
def get_biogas():
    data   = simulate_bin_data()
    wet_kg = round(sum(
        b["fill_level"] * 0.5
        for b in data if b["waste_type"] == "wet"
    ), 2)
    return jsonify(calculate_biogas(max(wet_kg, 1)))

@app.route("/api/reward", methods=["POST"])
def add_reward():
    body   = request.get_json() or {}
    uid    = body.get("user_id", "citizen_001")
    pts    = int(body.get("points", 10))
    action = body.get("action", "disposal")
    rewards[uid] = rewards.get(uid, 0) + pts
    event = {
        "user_id": uid,
        "points":  pts,
        "action":  action,
        "total":   rewards[uid],
        "time":    datetime.datetime.now().isoformat()
    }
    events_path = os.path.join(BASE_DIR, "disposal_events.json")
    with open(events_path, "w") as f:
        json.dump(event, f, indent=2)
    return jsonify({"user_id": uid, "total_points": rewards[uid]})

@app.route("/api/dashboard")
def dashboard_summary():
    bins   = simulate_bin_data()
    wet_kg = round(sum(
        b["fill_level"] * 0.5
        for b in bins if b["waste_type"] == "wet"
    ), 2)
    biogas = calculate_biogas(max(wet_kg, 1))
    return jsonify({
        "total_bins":    len(bins),
        "full_bins":     sum(1 for b in bins if b["fill_level"] > 75),
        "overflow_risk": sum(1 for b in bins
                             if predict_overflow(b["fill_level"])["overflow_risk"]),
        "energy_kwh":    biogas["electricity_kwh"],
        "co2_saved_kg":  biogas["co2_saved_kg"],
        "top_rewards":   rewards,
        "timestamp":     datetime.datetime.now().isoformat()
    })

@app.route("/api/run-bots", methods=["POST"])
def run_bots():
    import subprocess
    try:
        subprocess.Popen([
            "python",
            os.path.join(BASE_DIR, "..", "uipath_bots",
                         "python_triggers", "trigger_all_bots.py")
        ])
        return jsonify({"status": "All UiPath bots triggered"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("WATT_THE_WASTE! API running")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)