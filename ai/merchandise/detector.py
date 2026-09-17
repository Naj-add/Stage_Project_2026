from pathlib import Path

from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "merchandise_best.pt"
)


class MerchandiseDetector:

    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Merchandise model not found: {MODEL_PATH}"
            )

        self.model = YOLO(str(MODEL_PATH))

    def detect(
        self,
        image_path: str,
        confidence: float = 0.25
    ):
        """
        Detect merchandise in an image.

        Returns the detection having the highest confidence.
        """

        results = self.model.predict(
            source=image_path,
            conf=confidence,
            verbose=False
        )

        if not results:
            return None

        result = results[0]

        if result.boxes is None:
            return None

        if len(result.boxes) == 0:
            return None

        best_detection = None

        for box in result.boxes:

            class_id = int(
                box.cls[0].item()
            )

            score = float(
                box.conf[0].item()
            )

            class_name = result.names[class_id]

            detection = {
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(score, 4),
            }

            if (
                best_detection is None
                or score >
                best_detection["confidence"]
            ):
                best_detection = detection

        return best_detection