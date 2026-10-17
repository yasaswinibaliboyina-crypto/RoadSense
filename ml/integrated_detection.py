import cv2
from ultralytics import YOLO
import joblib
import pandas as pd
import os


# ==========================================
# 1. LOAD MODELS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

model = YOLO(os.path.join(BASE_DIR, "opencv", "yolo26n.pt"))

risk_model = joblib.load(
    os.path.join(BASE_DIR, "ml", "risk_model.pkl")
)

encoder = joblib.load(
    os.path.join(BASE_DIR, "ml", "label_encoder.pkl")
)


# ==========================================
# 2. LOAD VIDEO
# ==========================================

video_path = os.path.join(
    BASE_DIR,
    "opencv",
    "road.mp4"
)

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open road video.")
    exit()

print("RoadSense Integrated AI Started!")


# ==========================================
# 3. SETTINGS
# ==========================================

vehicle_classes = {
    "car",
    "motorcycle",
    "bus",
    "truck"
}

# Guntur Y-Junction prototype data
road_risk = 2
speed_limit = 60

# Simulated vehicle speed
current_speed = 62


# ==========================================
# 4. PROCESS VIDEO
# ==========================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Video ended.")
        break


    # --------------------------------------
    # OpenCV + YOLO
    # --------------------------------------

    results = model(
        frame,
        imgsz=960,
        verbose=False
    )

    vehicle_count = 0


    for result in results:

        for box in result.boxes:

            confidence = float(box.conf[0])

            class_id = int(box.cls[0])

            class_name = model.names[class_id]


            if (
                class_name in vehicle_classes
                and confidence >= 0.15
            ):

                vehicle_count += 1

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


    # --------------------------------------
    # Brightness / glare detection
    # --------------------------------------

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    brightness = gray.mean()

    bright_pixels = (
        gray > 220
    ).sum()

    total_pixels = (
        gray.shape[0] *
        gray.shape[1]
    )

    bright_percentage = (
        bright_pixels /
        total_pixels
    ) * 100


    if bright_percentage > 3:

        glare = 2
        glare_text = "HIGH"

    elif bright_percentage > 1:

        glare = 1
        glare_text = "MEDIUM"

    else:

        glare = 0
        glare_text = "LOW"


    # Night because this is our night video
    night = 1


    # --------------------------------------
    # XGBoost prediction
    # --------------------------------------

    input_data = pd.DataFrame([[
        road_risk,
        current_speed,
        speed_limit,
        night,
        glare,
        vehicle_count

    ]], columns=[

        "road_risk",
        "speed",
        "speed_limit",
        "night",
        "glare",
        "vehicles"

    ])


    prediction = risk_model.predict(
        input_data
    )

    risk = encoder.inverse_transform(
        prediction
    )[0]


    # ======================================
    # DISPLAY RESULTS
    # ======================================

    cv2.putText(
        frame,
        f"Vehicles: {vehicle_count}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Brightness: {brightness:.1f}",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Glare: {glare_text}",
        (30, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Speed: {current_speed} km/h",
        (30, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"ROAD RISK: {risk}",
        (30, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )


    cv2.imshow(
        "RoadSense - Integrated AI",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()

print("RoadSense Integrated AI Finished!")