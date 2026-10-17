import pandas as pd
import os
import time


# ==========================================
# 1. LOAD ROAD RISK DATA
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

risk_file = os.path.join(
    BASE_DIR,
    "cleaned",
    "road_risk.csv"
)

road_data = pd.read_csv(risk_file)

guntur = road_data[
    road_data["location_name"] == "Guntur Y-Junction"
].iloc[0]

risk_level = guntur["risk_level"]
risk_zone = guntur["risk_zone_length_m"]


# ==========================================
# 2. SIMULATED GPS + VEHICLE MOVEMENT
# ==========================================

# Distance from the high-risk zone (meters)
# and corresponding vehicle speed (km/h)

driving_data = [
    (1000, 42),
    (800, 45),
    (600, 48),
    (500, 52),
    (400, 55),
    (300, 62),
    (250, 63),
    (200, 64),
    (150, 62),
    (100, 58),
    (50, 50),
    (0, 45)
]


# ==========================================
# 3. START SIMULATION
# ==========================================

print()
print("======================================")
print("       ROADSENSE GPS SIMULATION")
print("======================================")

print("Road:", guntur["location_name"])
print("Highway:", guntur["highway"])
print("Risk Level:", risk_level)
print("Risk Zone:", risk_zone, "m")

print("--------------------------------------")


# ==========================================
# 4. SIMULATE VEHICLE MOVEMENT
# ==========================================

for distance, speed in driving_data:

    # Determine current road status

    if distance > 300:

        status = "SAFE / APPROACHING"

    elif distance > 0:

        status = "⚠️ APPROACHING HIGH-RISK ZONE"

    else:

        status = "🚨 INSIDE HIGH-RISK ZONE"


    # Additional speed warning

    if speed > 60:

        speed_warning = " ⚠️ SPEED HIGH"

    else:

        speed_warning = ""


    print(
        f"Distance to risk zone: {distance:4} m"
        f" | Speed: {speed:2} km/h"
        f" --> {status}"
        f"{speed_warning}"
    )


    # Wait so the movement looks realistic

    time.sleep(0.5)


# ==========================================
# 5. FINISHED
# ==========================================

print("--------------------------------------")
print("GPS + vehicle simulation completed.")
print("======================================")