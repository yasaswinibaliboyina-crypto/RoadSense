import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo26n.pt")

video_path = r"C:\Users\balib\OneDrive\Desktop\RoadSense\opencv\road.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("ERROR: Could not open the video.")
    exit()

print("RoadSense: Vehicle + Glare Detection Started")

vehicle_classes = {
    "car",
    "motorcycle",
    "bus",
    "truck"
}

while True:
    ret, frame = cap.read()

    if not ret:
        print("Video ended.")
        break

    # --------------------------------
    # 1. VEHICLE DETECTION
    # --------------------------------

    results = model(frame, imgsz=960, verbose=False)

    vehicle_count = 0

    for result in results:
        for box in result.boxes:

            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name in vehicle_classes and confidence >= 0.15:

                vehicle_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                label = f"{class_name} {confidence:.2f}"

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

    # --------------------------------
    # 2. BRIGHTNESS / GLARE DETECTION
    # --------------------------------

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    brightness = gray.mean()

    # Count very bright pixels
    bright_pixels = (gray > 220).sum()

    total_pixels = gray.shape[0] * gray.shape[1]

    bright_percentage = (bright_pixels / total_pixels) * 100

    # Simple prototype glare classification
    if bright_percentage > 3:
        glare_status = "HIGH"
    elif bright_percentage > 1:
        glare_status = "MEDIUM"
    else:
        glare_status = "LOW"

    # --------------------------------
    # 3. DISPLAY INFORMATION
    # --------------------------------

    cv2.putText(
        frame,
        f"Vehicles detected: {vehicle_count}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Brightness: {brightness:.1f}/255",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Headlight/Glare: {glare_status}",
        (30, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "RoadSense - Vision Analysis",
        frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()

print("RoadSense vision analysis finished.")