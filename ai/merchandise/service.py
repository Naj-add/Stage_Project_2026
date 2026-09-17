from ai.merchandise.detector import MerchandiseDetector
from ai.merchandise.matcher import match_product


_detector = None


def get_detector():
    global _detector

    if _detector is None:
        _detector = MerchandiseDetector()

    return _detector


def analyze_merchandise(
    image_path: str,
    expected_product: str
):
    detector = get_detector()

    detection = detector.detect(
        image_path
    )

    if detection is None:
        return {
            "detected_product": None,
            "confidence": 0.0,
            "expected_product": expected_product,
            "match": False,
            "reason": "No merchandise detected",
        }

    detected_product = detection[
        "class_name"
    ]

    confidence = detection[
        "confidence"
    ]

    match_result = match_product(
        detected_product,
        expected_product
    )

    return {
        "detected_product":
            detected_product,

        "confidence":
            confidence,

        "expected_product":
            match_result["expected_product"],

        "match":
            match_result["match"],

        "reason":
            match_result["reason"],
    }