
import pandas as pd
import joblib

# Load the trained model and label encoder
model = joblib.load("risk_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# RoadSense test scenario
road_risk_map = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}

glare_map = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}

# Simulated journey toward Guntur Y-Junction
driving_data = [
    (1000, 42),
    (800, 45),
    (600, 48),
    (400, 55),
    (300, 62),
    (200, 64),
    (100, 58),
    (50, 50),
    (0, 45)
]

print("\n========================================")
print("       ROADSENSE GPS + XGBOOST")
print("========================================")
print("Location: Guntur Y-Junction")
print("Historical road risk: HIGH")
print("Speed limit: 60 km/h (prototype assumption)")
print("----------------------------------------")

for distance, speed in driving_data:

    # Inputs for the trained model
    sample = pd.DataFrame([{
        "road_risk": road_risk_map["HIGH"],
        "speed": speed,
        "speed_limit": 60,
        "distance_to_risk_zone": distance,
        "night": 1,
        "glare": glare_map["MEDIUM"],
        "vehicles": 1
    }])

    # Predict immediate risk
    prediction = model.predict(sample)
    risk = label_encoder.inverse_transform(prediction)[0]

    if distance > 500:
        zone_status = "APPROACHING"
    elif distance > 300:
        zone_status = "NEAR RISK ZONE"
    elif distance > 0:
        zone_status = "APPROACHING HIGH-RISK ZONE"
    else:
        zone_status = "INSIDE HIGH-RISK ZONE"

    print(
        f"Distance: {distance:4} m | "
        f"Speed: {speed:2} km/h | "
        f"ML Risk: {risk:6} | "
        f"{zone_status}"
    )

print("----------------------------------------")
print("GPS + XGBoost test completed.")
print("========================================")
