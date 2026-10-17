import joblib
import pandas as pd
import os


# ---------------------------------------
# 1. Find RoadSense folder
# ---------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

model_path = os.path.join(
    BASE_DIR,
    "ml",
    "risk_model.pkl"
)

encoder_path = os.path.join(
    BASE_DIR,
    "ml",
    "label_encoder.pkl"
)


# ---------------------------------------
# 2. Load trained model
# ---------------------------------------

model = joblib.load(model_path)
encoder = joblib.load(encoder_path)

print("RoadSense ML model loaded!")
print()


# ---------------------------------------
# 3. Our actual RoadSense scenario
# ---------------------------------------

road_risk = 2       # HIGH
speed = 62
speed_limit = 60
night = 1           # YES
glare = 1           # MEDIUM
vehicles = 1


# ---------------------------------------
# 4. Create input
# ---------------------------------------

input_data = pd.DataFrame([[
    road_risk,
    speed,
    speed_limit,
    night,
    glare,
    vehicles
]], columns=[
    "road_risk",
    "speed",
    "speed_limit",
    "night",
    "glare",
    "vehicles"
])


# ---------------------------------------
# 5. Predict
# ---------------------------------------

prediction = model.predict(input_data)

risk = encoder.inverse_transform(prediction)[0]


# ---------------------------------------
# 6. Display result
# ---------------------------------------

print("========== ROAD SENSE ML ==========")
print("Location: Guntur Y-Junction")
print("Speed:", speed, "km/h")
print("Speed Limit:", speed_limit, "km/h")
print("Night:", "YES")
print("Glare:", "MEDIUM")
print("Vehicles:", vehicles)
print("------------------------------------")
print("XGBoost Prediction:", risk)
print("====================================")