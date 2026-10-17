
import pandas as pd
import random

random.seed(42)

data = []

for _ in range(2000):

    # 1. Historical road risk
    road_risk = random.choice([
        "LOW", "MEDIUM", "HIGH"
    ])

    # 2. Vehicle speed and assumed speed limit
    speed_limit = random.choice([40, 50, 60])
    speed = random.randint(20, 90)

    # 3. Distance to the risk zone, in metres
    distance = random.choice([
        random.randint(501, 1500),
        random.randint(301, 500),
        random.randint(101, 300),
        random.randint(0, 100)
    ])

    # 4. Other driving conditions
    night = random.choice([0, 1])
    glare = random.choice(["LOW", "MEDIUM", "HIGH"])
    vehicles = random.randint(0, 5)

    # --------------------------------
    # Calculate immediate driving risk
    # --------------------------------

    score = 0

    # Historical road danger
    if road_risk == "HIGH":
        score += 25
    elif road_risk == "MEDIUM":
        score += 12

    # Overspeeding
    if speed > speed_limit:
        score += min(25, 10 + (speed - speed_limit) // 2)

    # Distance-based risk
    if distance <= 100:
        score += 30
    elif distance <= 300:
        score += 22
    elif distance <= 500:
        score += 12
    elif distance <= 1000:
        score += 5

    # Night driving
    if night == 1:
        score += 10

    # Headlight/glare indicator
    if glare == "HIGH":
        score += 15
    elif glare == "MEDIUM":
        score += 7

    # Traffic density indicator
    if vehicles >= 4:
        score += 10
    elif vehicles >= 2:
        score += 5

    # --------------------------------
    # Convert score into risk category
    # --------------------------------

    if score >= 60:
        risk = "HIGH"
    elif score >= 30:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    data.append([
        road_risk,
        speed,
        speed_limit,
        distance,
        night,
        glare,
        vehicles,
        score,
        risk
    ])

# Create dataset
df = pd.DataFrame(data, columns=[
    "road_risk",
    "speed",
    "speed_limit",
    "distance_to_risk_zone",
    "night",
    "glare",
    "vehicles",
    "risk_score",
    "risk"
])

# Save in the ml folder when running this script there
df.to_csv("training_data.csv", index=False)

print("RoadSense ML Dataset v2 created!")
print("Rows:", len(df))
print("\nSample records:")
print(df.head(10))
print("\nRisk distribution:")
print(df["risk"].value_counts())
print("\nSaved as training_data.csv")
