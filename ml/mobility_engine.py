
import os
import pandas as pd
import math

# --------------------------------
# 1. Locate the project data
# --------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "cleaned")

VEHICLE_FILE = os.path.join(
    DATA_DIR, "vehicle_state.csv"
)

STATION_FILE = os.path.join(
    DATA_DIR, "mobility_stations.csv"
)


# --------------------------------
# 2. Load the datasets
# --------------------------------

vehicles = pd.read_csv(VEHICLE_FILE)
stations = pd.read_csv(STATION_FILE)

print("\n===================================")
print("     ROADSENSE MOBILITY ENGINE")
print("===================================")


# --------------------------------
# 3. Calculate distance between
#    two GPS coordinates
# --------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371  # kilometres

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# --------------------------------
# 4. Find the nearest known station
# --------------------------------

def find_nearest_station(vehicle_type, latitude, longitude):

    if vehicle_type == "EV":
        station_type = "EV"
    else:
        station_type = "PETROL"

    candidates = stations[
        (stations["station_type"] == station_type)
        & stations["latitude"].notna()
        & stations["longitude"].notna()
    ].copy()

    if candidates.empty:
        return None, None

    candidates["distance_km"] = candidates.apply(
        lambda row: calculate_distance(
            latitude,
            longitude,
            row["latitude"],
            row["longitude"]
        ),
        axis=1
    )

    nearest = candidates.sort_values(
        "distance_km"
    ).iloc[0]

    return nearest, nearest["distance_km"]


# --------------------------------
# 5. Demonstrate mobility assistance
# --------------------------------

# Prototype location only.
# Replace this with actual GPS coordinates when available.
DEMO_LATITUDE = 16.3280
DEMO_LONGITUDE = 80.4839

for vehicle_type in ["EV", "PETROL"]:

    sample = vehicles[
        vehicles["vehicle_type"] == vehicle_type
    ].iloc[0]

    print(f"\nVehicle type: {vehicle_type}")
    print("-----------------------------------")

    if vehicle_type == "EV":

        battery = sample["battery_pct"]
        range_km = sample["range_km"]

        print(f"Battery: {battery:.0f}%")
        print(f"Estimated remaining range: {range_km:.0f} km")

        if battery <= 20:
            print("Alert: Battery is low.")
        elif battery <= 40:
            print("Notice: Consider planning a charge.")
        else:
            print("Battery status: No low-battery alert.")

    else:

        fuel = sample["fuel_pct"]

        print(f"Fuel remaining: {fuel:.0f}%")
        print("Petrol range: Not available in the current dataset.")

        if fuel <= 20:
            print("Alert: Fuel level is low.")
        elif fuel <= 40:
            print("Notice: Consider planning a fuel stop.")
        else:
            print("Fuel status: No low-fuel alert.")

    station, distance = find_nearest_station(
        vehicle_type,
        DEMO_LATITUDE,
        DEMO_LONGITUDE
    )

    if station is None:
        print("Nearest station: Cannot calculate.")
        print("Reason: No station with usable coordinates.")
    else:
        print(f"Nearest mapped {vehicle_type} station:")
        print(station["station_name"])
        print(f"Straight-line distance: {distance:.2f} km")
        print("Note: Road travel distance may be longer.")

print("\n===================================")
print("Mobility demonstration completed.")
print("===================================")
