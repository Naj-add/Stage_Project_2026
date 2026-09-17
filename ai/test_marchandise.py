from ultralytics import YOLO
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "models" / "merchandise_best.pt"

IMAGE_PATH = Path(
    r"C:\Users\Hp\Downloads\Fruit&veg dataset-20260901T152623Z-1-001\Fruit&veg dataset\yolo_dataset\test\raddish_Image_2.jpg"
)

model = YOLO(str(MODEL_PATH))

results = model.predict(
    source=str(IMAGE_PATH),
    conf=0.25,
    save=True
)

for result in results:
    print("\n=== MERCHANDISE DETECTION ===")

    if result.boxes is None or len(result.boxes) == 0:
        print("No merchandise detected.")
        continue

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = result.names[class_id]

        print(f"Detected: {class_name}")
        print(f"Confidence: {confidence:.2%}")