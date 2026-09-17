from pathlib import Path

from ultralytics import YOLO


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "plate_best.pt"
)


class PlateDetector:

    def __init__(self):
        self.model = YOLO(str(MODEL_PATH))

    def detect(self, image_path: str, confidence: float = 0.15):
        results = self.model.predict(
            source=image_path,
            conf=confidence,
            verbose=False
        )

        if not results:
            return None

        result = results[0]

        if result.boxes is None or len(result.boxes) == 0:
            return None

        best_box = None
        best_confidence = 0.0

        for box in result.boxes:
            conf = float(box.conf[0])

            if conf > best_confidence:
                best_confidence = conf

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                best_box = (
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2)
                )

        if best_box is None:
            return None

        return {
            "bbox": best_box,
            "confidence": best_confidence
        }