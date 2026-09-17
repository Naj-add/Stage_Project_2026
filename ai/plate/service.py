from pathlib import Path

import cv2

from .detector import PlateDetector
from .ocr import MoroccanPlateOCR


class PlateService:

    def __init__(self):

        self.detector = PlateDetector()
        self.ocr = MoroccanPlateOCR()

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            raise ValueError(
                "Unable to read image"
            )

        # -----------------------------------------
        # 1. YOLO PLATE DETECTION
        # -----------------------------------------

        detection = self.detector.detect(
            str(image_path)
        )

        if detection is None:

            return {
                "success": False,
                "status": "PLATE_NOT_DETECTED",
                "plate": None,
                "detection_confidence": 0.0
            }

        x1, y1, x2, y2 = detection["bbox"]

        # -----------------------------------------
        # 2. PADDING
        # -----------------------------------------

        padding = 10

        x1 = max(
            0,
            x1 - padding
        )

        y1 = max(
            0,
            y1 - padding
        )

        x2 = min(
            image.shape[1],
            x2 + padding
        )

        y2 = min(
            image.shape[0],
            y2 + padding
        )

        # -----------------------------------------
        # 3. CROP
        # -----------------------------------------

        plate_crop = image[
            y1:y2,
            x1:x2
        ]

        if plate_crop.size == 0:

            return {
                "success": False,
                "status": "INVALID_PLATE_CROP",
                "plate": None,
                "detection_confidence":
                    detection["confidence"]
            }

        # -----------------------------------------
        # 4. OCR
        # -----------------------------------------

        ocr_result = self.ocr.read_plate(plate_crop)

        if ocr_result is None:

            return {
                "success": False,
                "status": "OCR_NOT_DETECTED",
                "plate": None,
                "detection_confidence":
                    round(
                        detection["confidence"],
                        4
                    )
            }

        # -----------------------------------------
        # 5. FINAL RESULT
        # -----------------------------------------

        return {
            "success": True,
            "status": "PLATE_DETECTED",
            "plate": ocr_result["plate"],
            "detection_confidence":
                round(
                    detection["confidence"],
                    4
                ),
            "ocr_confidence":
                ocr_result["ocr_confidence"],
            "bbox": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            },
            "components": {
                "number": ocr_result[
                    "first_number"
                ],
                "letter": ocr_result[
                    "letter"
                ],
                "code": ocr_result[
                    "last_number"
                ]
            }
        }