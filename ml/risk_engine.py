import pandas as pd
import os


# ---------------------------------------
# 1. FIND ROAD SENSE MAIN FOLDER
# ---------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

cleaned_folder = os.path.join(BASE_DIR, "cleaned")


# ---------------------------------------
# 2. LOAD ROAD RISK DATA
# ---------------------------------------

road_risk_file = os.path.join(
    cleaned_folder,
    "road_risk.csv"
)

road_data = pd.read_csv(road_risk_file)

print("Road risk data loaded successfully!")
print()


# ---------------------------------------
# 3. SELECT GUNTUR Y-JUNCTION
# ---------------------------------------

location = "Guntur Y-Junction"

road = road_data[
    road_data["location_name"] == location
].iloc[0]

road_risk = road["risk_level"]
risk_zone_length = road["risk_zone_length_m"]

print("Location:", location)
print("Road Risk:", road_risk)
print("Risk Zone Length:", risk_zone_length, "m")
print()


# ---------------------------------------
# 4. ROAD SENSE RISK FUNCTION
# ---------------------------------------

def calculate_risk(
    road_risk,
    speed,
    speed_limit,
    night,
    glare,
    vehicles
):

    score = 0

    # Road risk
    if road_risk == "HIGH":
        score += 40

    elif road_risk == "MEDIUM":
        score += 20

    # Speed
    if speed > speed_limit:
        score += 20

    # Night
    if night:
        score += 15

    # Glare
    if glare == "HIGH":
        score += 15

    elif glare == "MEDIUM":
        score += 8

    # Traffic
    if vehicles >= 3:
        score += 10

    elif vehicles >= 1:
        score += 5

    # Final risk
    if score >= 60:
        risk_level = "HIGH"

    elif score >= 30:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return score, risk_level


# ---------------------------------------
# 5. TEST VEHICLE + VISION DATA
# ---------------------------------------

speed = 62
speed_limit = 60

night = True
glare = "MEDIUM"
vehicles = 1


# ---------------------------------------
# 6. CALCULATE FINAL RISK
# ---------------------------------------

score, final_risk = calculate_risk(
    road_risk,
    speed,
    speed_limit,
    night,
    glare,
    vehicles
)


# ---------------------------------------
# 7. DISPLAY RESULT
# ---------------------------------------

print("========== ROAD SENSE ==========")
print("Location:", location)
print("Speed:", speed, "km/h")
print("Speed Limit:", speed_limit, "km/h")
print("Night:", night)
print("Glare:", glare)
print("Vehicles:", vehicles)
print("--------------------------------")
print("Risk Score:", score)
print("FINAL RISK:", final_risk)
print("================================")