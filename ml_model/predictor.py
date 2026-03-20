import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "overflow_model.pkl")

def train_model():
    np.random.seed(42)
    X = np.column_stack([
        np.random.uniform(0, 100, 600),
        np.random.randint(0, 24, 600),
        np.random.randint(0, 7, 600)
    ])
    y = (X[:, 0] > 75).astype(int)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    print(f"[ML] Model trained and saved to {MODEL_PATH}")
    return model

def predict_overflow(fill_level, hour=None, day=None):
    if hour is None:
           hour = datetime.datetime.now().hour
    if day is None:
        day = datetime.datetime.now().weekday()
    if not os.path.exists(MODEL_PATH):
        train_model()
    model = joblib.load(MODEL_PATH)
    prob = model.predict_proba([[fill_level, hour, day]])[0][1]
    return {
        "overflow_risk": bool(prob > 0.5),
        "probability":   round(float(prob), 2),
        "urgency": "HIGH" if prob > 0.8 else "MEDIUM" if prob > 0.5 else "LOW"
    }

def optimize_route(bins_data):
    urgent = sorted(
        [b for b in bins_data if b["fill_level"] > 50],
        key=lambda x: x["fill_level"],
        reverse=True
    )
    return {
        "optimized_route":       [b["bin_id"] for b in urgent],
        "total_stops":           len(urgent),
        "estimated_time_mins":   len(urgent) * 8
    }

if __name__ == "__main__":
    train_model()
    print("Test 1 (fill=85):", predict_overflow(85))
    print("Test 2 (fill=25):", predict_overflow(25))
    print("Test 3 (fill=60):", predict_overflow(60))