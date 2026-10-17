
import cv2
from ultralytics import YOLO
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

latest_brightness = 0.0
latest_visibility_estimate = "UNKNOWN"

model = YOLO("yolo26n.pt")
video_path = (
    r"C:\Users\balib\OneDrive\Desktop\RoadSense"
    r"\opencv\road.mp4"
)

latest_vehicle_count = 0


@router.get("/vehicle-count")
def vehicle_count():
    return {
        "vehicles_detected": latest_vehicle_count
    }


def generate_frames():
    global latest_vehicle_count

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("ERROR: Could not open road.mp4")
        return

    vehicle_classes = {"car", "motorcycle", "bus", "truck"}

    try:
        while True:
            ret, frame = cap.read()

            # Estimate overall frame brightness using OpenCV
            if ret:
                global latest_brightness, latest_visibility_estimate
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = float(gray_frame.mean())

            if brightness < 60:
                visibility_estimate = "LOW LIGHT"
            elif brightness < 120:
                visibility_estimate = "MODERATE LIGHT"
            else:
                visibility_estimate = "BRIGHT"

            latest_brightness = brightness
            latest_visibility_estimate = visibility_estimate

            cv2.putText(
                frame,
                f"Brightness: {brightness:.1f} | {visibility_estimate}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            results = model(frame, imgsz=640, verbose=False)
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
                            int, box.xyxy[0]
                        )

                        cv2.rectangle(
                            frame,
                            (x1, y1),
                            (x2, y2),
                            (0, 255, 0),
                            2
                        )

                        cv2.putText(
                            frame,
                            f"{class_name} {confidence:.2f}",
                            (x1, max(y1 - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )

            # Update once per frame, even if the count is zero.
            latest_vehicle_count = vehicle_count

            cv2.putText(
                frame,
                f"Vehicles detected: {vehicle_count}",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            success, buffer = cv2.imencode(".jpg", frame)

            if success:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )

    finally:
        cap.release()


@router.get("/video-feed")
def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/visibility")
def get_visibility():
    return {
        "brightness": latest_brightness,
        "visibility_estimate": latest_visibility_estimate
    }