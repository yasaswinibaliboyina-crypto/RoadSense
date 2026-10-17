
import os
import sys

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from backend.video_stream import router as video_router
from fastapi.middleware.cors import CORSMiddleware
from backend.aws_storage import save_road_report
from backend.report_history import save_local_report, get_local_reports

# ----------------------------------------
# Project paths
# ----------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(BASE_DIR, "ml")
DATA_DIR = os.path.join(BASE_DIR, "cleaned")

sys.path.insert(0, ML_DIR)

from mobility_engine import find_nearest_station  # noqa: E402


# ----------------------------------------
# Load model and datasets
# ----------------------------------------

MODEL_PATH = os.path.join(ML_DIR, "risk_model.pkl")
ENCODER_PATH = os.path.join(ML_DIR, "label_encoder.pkl")

VEHICLE_PATH = os.path.join(DATA_DIR, "vehicle_state.csv")
STATION_PATH = os.path.join(DATA_DIR, "mobility_stations.csv")
ROAD_PATH = os.path.join(DATA_DIR, "road_risk.csv")

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

vehicles = pd.read_csv(VEHICLE_PATH)
stations = pd.read_csv(STATION_PATH)
roads = pd.read_csv(ROAD_PATH)

ROAD_RISK_MAP = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
GLARE_MAP = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


# ----------------------------------------
# Create API
# ----------------------------------------

app = FastAPI(
    title="RoadSense API",
    description="Road-risk prediction and vehicle mobility assistance",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(video_router)



class RiskRequest(BaseModel):
    speed: float = Field(ge=0, le=300)
    speed_limit: float = Field(default=60, gt=0, le=200)
    distance_to_risk_zone: float = Field(ge=0, le=100000)
    night: bool = False
    glare: str = "LOW"
    vehicles_detected: int = Field(default=0, ge=0, le=100)

    latitude: float = Field(default=16.3280, ge=-90, le=90)
    longitude: float = Field(default=80.4839, ge=-180, le=180)


# ----------------------------------------
# Health check
# ----------------------------------------

@app.get("/")
def home():
    return {
        "project": "RoadSense",
        "status": "running",
        "features": [
            "XGBoost road-risk prediction",
            "EV mobility assistance",
            "Petrol mobility assistance"
        ]
    }


# ----------------------------------------
# Road-risk endpoint
# ----------------------------------------

@app.post("/predict-risk")
def predict_risk(request: RiskRequest):

    glare = request.glare.upper()

    if glare not in GLARE_MAP:
        raise HTTPException(
            status_code=400,
            detail="glare must be LOW, MEDIUM or HIGH"
        )

    road_row = roads[
        roads["location_name"] == "Guntur Y-Junction"
    ]

    if road_row.empty:
        raise HTTPException(
            status_code=500,
            detail="Guntur Y-Junction road-risk data is missing"
        )

    road = road_row.iloc[0]

    features = pd.DataFrame([{
        "road_risk": ROAD_RISK_MAP[str(road["risk_level"]).upper()],
        "speed": request.speed,
        "speed_limit": request.speed_limit,
        "distance_to_risk_zone": request.distance_to_risk_zone,
        "night": int(request.night),
        "glare": GLARE_MAP[glare],
        "vehicles": request.vehicles_detected
    }])

    prediction = model.predict(features)
    risk = str(label_encoder.inverse_transform(prediction)[0])

    return {
        "location": "Guntur Y-Junction",
        "historical_road_risk": str(road["risk_level"]),
        "distance_to_risk_zone_m": request.distance_to_risk_zone,
        "speed_kmph": request.speed,
        "speed_limit_kmph": request.speed_limit,
        "predicted_immediate_risk": risk,
        "night": request.night,
        "glare": glare,
        "vehicles_detected": request.vehicles_detected,
        "note": "Prototype prediction; speed and distance are supplied inputs."
    }


# ----------------------------------------
# Mobility endpoint
# ----------------------------------------

@app.get("/mobility/{vehicle_type}")
def mobility(
    vehicle_type: str,
    latitude: float = 16.3280,
    longitude: float = 80.4839
):

    vehicle_type = vehicle_type.upper()

    if vehicle_type not in ["EV", "PETROL"]:
        raise HTTPException(
            status_code=400,
            detail="vehicle_type must be EV or PETROL"
        )

    matches = vehicles[
        vehicles["vehicle_type"] == vehicle_type
    ]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail="No sample vehicle data found"
        )

    vehicle = matches.iloc[0]

    result = {
        "vehicle_type": vehicle_type,
        "demo_location": {
            "latitude": latitude,
            "longitude": longitude
        }
    }

    if vehicle_type == "EV":
        battery = vehicle["battery_pct"]
        remaining_range = vehicle["range_km"]

        result["battery_pct"] = (
            None if pd.isna(battery) else float(battery)
        )
        result["estimated_range_km"] = (
            None if pd.isna(remaining_range) else float(remaining_range)
        )

        if pd.notna(battery):
            result["alert"] = (
                "LOW BATTERY"
                if battery <= 20
                else "PLAN A CHARGE"
                if battery <= 40
                else "NO LOW-BATTERY ALERT"
            )

    else:
        fuel = vehicle["fuel_pct"]

        result["fuel_pct"] = (
            None if pd.isna(fuel) else float(fuel)
        )
        result["estimated_range_km"] = None
        result["note"] = (
            "Petrol range is not available in the current dataset."
        )

        if pd.notna(fuel):
            result["alert"] = (
                "LOW FUEL"
                if fuel <= 20
                else "PLAN A FUEL STOP"
                if fuel <= 40
                else "NO LOW-FUEL ALERT"
            )

    candidates = stations[
        (stations["station_type"] == vehicle_type)
        & stations["latitude"].notna()
        & stations["longitude"].notna()
    ]

    if candidates.empty:
        result["nearest_station"] = None
        result["station_note"] = (
            "No station with usable coordinates is available."
        )
    else:
        nearest, distance = find_nearest_station(
            vehicle_type, latitude, longitude
        )

        result["nearest_station"] = {
            "name": str(nearest["station_name"]),
            "straight_line_distance_km": round(float(distance), 2)
        }
        result["station_note"] = (
            "Straight-line distance; road distance may be longer. "
            "Station availability and compatibility are not verified."
        )

    return result



from backend.aws_storage import save_road_report


@app.post("/aws-test-report")
def aws_test_report():
    sample_report = {
        "project": "RoadSense",
        "source": "local_test",
        "brightness": 40.8,
        "visibility_estimate": "LOW LIGHT",
        "vehicle_count": 1,
        "risk_level": "HIGH"
    }

    return save_road_report(sample_report)


@app.post("/save-local-report")
def save_report():
    sample_report = {
        "project": "RoadSense",
        "source": "local_test",
        "brightness": 40.8,
        "visibility_estimate": "LOW LIGHT",
        "vehicle_count": 1,
        "risk_level": "HIGH"
    }

    return save_local_report(sample_report)


@app.get("/report-history")
def report_history():
    return {
        "total_reports": len(get_local_reports()),
        "reports": get_local_reports()
    }


