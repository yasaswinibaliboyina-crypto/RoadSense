import pandas as pd
import os

# ==================================================
# FIND OUR FOLDERS
# ==================================================

# Current file:
# RoadSense/data/preprocessing/clean_data.py

# Go up:
# preprocessing -> data -> RoadSense

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# CSV files are directly inside RoadSense/processed
input_folder = os.path.join(BASE_DIR, "processed")

# Cleaned files will be saved here
output_folder = os.path.join(BASE_DIR, "cleaned")

os.makedirs(output_folder, exist_ok=True)


# ==================================================
# CLEAN ONE CSV FILE
# ==================================================

def clean_csv(filename):

    input_path = os.path.join(input_folder, filename)

    df = pd.read_csv(input_path)

    print("\n======================================")
    print("FILE:", filename)
    print("======================================")

    print("\nOriginal shape:", df.shape)

    # Remove completely empty rows
    empty_rows = df.isna().all(axis=1).sum()
    print("Completely empty rows:", empty_rows)

    df = df.dropna(how="all")

    # Find duplicate rows
    duplicates = df.duplicated().sum()
    print("Duplicate rows found:", duplicates)

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean column names
    df.columns = df.columns.str.strip()

    # Remove extra spaces from text
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()

    # Show missing values
    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nCleaned shape:", df.shape)

    # Save cleaned file
    output_path = os.path.join(output_folder, filename)

    df.to_csv(output_path, index=False)

    print("\nSaved to:")
    print(output_path)


# ==================================================
# FOUR DATASETS
# ==================================================

files = [
    "road_features.csv",
    "road_risk.csv",
    "mobility_stations.csv",
    "vehicle_state.csv"
]


# ==================================================
# CLEAN ALL DATASETS
# ==================================================

print("\n==============================================")
print("       ROAD SENSE DATA CLEANING")
print("==============================================")

for file in files:

    try:
        clean_csv(file)

    except FileNotFoundError:
        print("\nERROR: Could not find:", file)

    except Exception as e:
        print("\nERROR while processing:", file)
        print(e)


# ==================================================
# FINISHED
# ==================================================

print("\n==============================================")
print("   ALL DATASETS HAVE BEEN PROCESSED!")
print("==============================================")

print("\nCleaned files are located in:")
print(output_folder)