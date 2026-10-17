
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier


# --------------------------------
# 1. Load training dataset
# --------------------------------

df = pd.read_csv("training_data.csv")

print("Dataset loaded!")
print("Rows:", len(df))


# --------------------------------
# 2. Convert text into numbers
# --------------------------------

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

df["road_risk"] = df["road_risk"].map(road_risk_map)
df["glare"] = df["glare"].map(glare_map)


# --------------------------------
# 3. Select input features
# --------------------------------

features = [
    "road_risk",
    "speed",
    "speed_limit",
    "distance_to_risk_zone",
    "night",
    "glare",
    "vehicles"
]

X = df[features]
y = df["risk"]


# --------------------------------
# 4. Encode target labels
# --------------------------------

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)


# --------------------------------
# 5. Split data
# --------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)


# --------------------------------
# 6. Train XGBoost
# --------------------------------

model = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    eval_metric="mlogloss"
)

model.fit(X_train, y_train)


# --------------------------------
# 7. Evaluate model
# --------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n========== MODEL RESULTS ==========")
print(f"Accuracy: {accuracy:.2%}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        labels=range(len(label_encoder.classes_)),
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# --------------------------------
# 8. Save model and encoder
# --------------------------------

joblib.dump(model, "risk_model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("\nModel saved as risk_model.pkl")
print("Label encoder saved as label_encoder.pkl")
print("RoadSense training completed!")
