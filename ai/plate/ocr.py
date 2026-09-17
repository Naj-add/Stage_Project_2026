import re
import cv2
import numpy as np
import easyocr


MOROCCAN_LETTERS = "أبتثجحخدذرزسشصضطظعغفقكلمنهوي"

ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
WESTERN_DIGITS = "0123456789"

ARABIC_TO_WESTERN = str.maketrans(
    ARABIC_DIGITS,
    WESTERN_DIGITS
)


class MoroccanPlateOCR:

    def __init__(self):
        print("Initializing Moroccan OCR...")

        self.reader = easyocr.Reader(
            ["ar", "en"],
            gpu=False
        )

    # ---------------------------------------------------------
    # Basic normalization
    # ---------------------------------------------------------

    def normalize_digits(self, text: str) -> str:
        if not text:
            return ""

        return text.translate(ARABIC_TO_WESTERN)

    def clean_digits(self, text: str) -> str:
        if not text:
            return ""

        text = self.normalize_digits(text)

        # Conservative OCR corrections.
        #
        # These are ONLY used in digit zones.
        # They help with common OCR confusions:
        #
        # O -> 0
        # I/l -> 1
        # Z -> 2
        # S -> 5
        # G -> 6
        # T -> 7
        # B -> 8
        #
        # We do not replace every possible character because
        # aggressive replacement can create false numbers.
        corrections = str.maketrans({
            "O": "0",
            "o": "0",
            "I": "1",
            "l": "1",
            "|": "1",
            "Z": "2",
            "z": "2",
            "S": "5",
            "s": "5",
            "G": "6",
            "g": "6",
            "T": "7",
            "t": "7",
            "B": "8",
            "b": "8"
        })

        text = text.translate(corrections)

        return "".join(
            char for char in text
            if char in WESTERN_DIGITS
        )

    def clean_letter(self, text: str) -> str:
        if not text:
            return ""

        # Normalize common whitespace/noise.
        text = text.strip()

        # Keep only Moroccan Arabic letters.
        letters = [
            char for char in text
            if char in MOROCCAN_LETTERS
        ]

        if not letters:
            return ""

        return letters[0]

    # ---------------------------------------------------------
    # Image preprocessing
    # ---------------------------------------------------------

    def preprocess_variants(self, image):
        """
        Generate several preprocessing versions.

        We keep the original image information while creating
        different versions that can help EasyOCR with:
        - low contrast
        - shadows
        - blur
        - small characters
        - uneven lighting
        """

        if image is None or image.size == 0:
            return []

        # -----------------------------------------------------
        # 1. Enlarge image
        # -----------------------------------------------------

        scale = 3.0

        enlarged = cv2.resize(
            image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

        # -----------------------------------------------------
        # 2. Grayscale
        # -----------------------------------------------------

        gray = cv2.cvtColor(
            enlarged,
            cv2.COLOR_BGR2GRAY
        )

        variants = []

        # -----------------------------------------------------
        # Variant 1 - CLAHE + sharpening
        # -----------------------------------------------------

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        enhanced = clahe.apply(gray)

        blurred = cv2.GaussianBlur(
            enhanced,
            (0, 0),
            1.0
        )

        sharpened = cv2.addWeighted(
            enhanced,
            1.5,
            blurred,
            -0.5,
            0
        )

        variants.append(sharpened)

        # -----------------------------------------------------
        # Variant 2 - OTSU threshold
        # -----------------------------------------------------

        otsu = cv2.threshold(
            sharpened,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        variants.append(otsu)

        # -----------------------------------------------------
        # Variant 3 - Adaptive threshold
        # -----------------------------------------------------

        adaptive = cv2.adaptiveThreshold(
            sharpened,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            9
        )

        variants.append(adaptive)

        # -----------------------------------------------------
        # Variant 4 - Blackhat morphology
        #
        # Useful when dark characters are on a bright plate.
        # -----------------------------------------------------

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (15, 15)
        )

        blackhat = cv2.morphologyEx(
            gray,
            cv2.MORPH_BLACKHAT,
            kernel
        )

        blackhat = cv2.normalize(
            blackhat,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        variants.append(blackhat)

        # -----------------------------------------------------
        # Variant 5 - Mild denoising
        # -----------------------------------------------------

        denoised = cv2.fastNlMeansDenoising(
            sharpened,
            None,
            10,
            7,
            21
        )

        variants.append(denoised)

        return variants

    # Keep the old method name available.
    #
    # This is useful in case another part of your project
    # calls preprocess() directly.
    def preprocess(self, image):

        variants = self.preprocess_variants(image)

        if not variants:
            return None

        return variants[0]

    # ---------------------------------------------------------
    # Internal helper - OCR digit candidate extraction
    # ---------------------------------------------------------

    def _read_digit_candidates(self, processed):

        if processed is None:
            return []

        results = self.reader.readtext(
            processed,
            detail=1,
            paragraph=False,
            allowlist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

        candidates = []

        for result in results:

            if len(result) < 3:
                continue

            text = str(result[1]).strip()
            confidence = float(result[2])

            cleaned = self.clean_digits(text)

            if not cleaned:
                continue

            # Plate number constraints.
            if len(cleaned) > 5:
                continue

            candidates.append(
                (cleaned, confidence)
            )

        return candidates

    # ---------------------------------------------------------
    # OCR digits
    # ---------------------------------------------------------

    def read_digits(self, image):

        variants = self.preprocess_variants(image)

        if not variants:
            return None, 0.0

        all_candidates = []

        # -----------------------------------------------------
        # Run OCR on every preprocessing variant.
        # -----------------------------------------------------

        for processed in variants:

            candidates = self._read_digit_candidates(
                processed
            )

            for candidate in candidates:
                all_candidates.append(candidate)

        if not all_candidates:
            return None, 0.0

        # -----------------------------------------------------
        # Group identical results.
        #
        # If multiple preprocessing methods independently
        # produce the same number, that is stronger evidence
        # than a single high-confidence result.
        # -----------------------------------------------------

        grouped = {}

        for text, confidence in all_candidates:

            if text not in grouped:
                grouped[text] = []

            grouped[text].append(confidence)

        scored_candidates = []

        for text, confidences in grouped.items():

            max_confidence = max(confidences)

            average_confidence = (
                sum(confidences)
                / len(confidences)
            )

            occurrences = len(confidences)

            # Small consistency bonus.
            consistency_bonus = min(
                occurrences * 0.05,
                0.20
            )

            score = (
                max_confidence * 0.60
                + average_confidence * 0.25
                + consistency_bonus
            )

            scored_candidates.append(
                (
                    text,
                    min(score, 1.0),
                    max_confidence,
                    occurrences
                )
            )

        # Highest combined score wins.
        scored_candidates.sort(
            key=lambda x: (
                x[1],
                x[3],
                x[2]
            ),
            reverse=True
        )

        best = scored_candidates[0]

        return best[0], best[1]

    # ---------------------------------------------------------
    # Internal helper - OCR Arabic letter candidates
    # ---------------------------------------------------------

    def _read_letter_candidates(self, processed):

        if processed is None:
            return []

        results = self.reader.readtext(
            processed,
            detail=1,
            paragraph=False,
            allowlist=MOROCCAN_LETTERS
        )

        candidates = []

        for result in results:

            if len(result) < 3:
                continue

            text = str(result[1]).strip()
            confidence = float(result[2])

            letter = self.clean_letter(text)

            if not letter:
                continue

            candidates.append(
                (letter, confidence)
            )

        return candidates

    # ---------------------------------------------------------
    # OCR Arabic letter
    # ---------------------------------------------------------

    def read_letter(self, image):

        variants = self.preprocess_variants(image)

        if not variants:
            return None, 0.0

        all_candidates = []

        # -----------------------------------------------------
        # Run Arabic OCR on several preprocessing variants.
        # -----------------------------------------------------

        for processed in variants:

            candidates = self._read_letter_candidates(
                processed
            )

            for candidate in candidates:
                all_candidates.append(candidate)

        if not all_candidates:
            return None, 0.0

        # -----------------------------------------------------
        # Group identical letters.
        # -----------------------------------------------------

        grouped = {}

        for letter, confidence in all_candidates:

            if letter not in grouped:
                grouped[letter] = []

            grouped[letter].append(confidence)

        scored_candidates = []

        for letter, confidences in grouped.items():

            max_confidence = max(confidences)

            average_confidence = (
                sum(confidences)
                / len(confidences)
            )

            occurrences = len(confidences)

            consistency_bonus = min(
                occurrences * 0.05,
                0.20
            )

            score = (
                max_confidence * 0.60
                + average_confidence * 0.25
                + consistency_bonus
            )

            scored_candidates.append(
                (
                    letter,
                    min(score, 1.0),
                    max_confidence,
                    occurrences
                )
            )

        scored_candidates.sort(
            key=lambda x: (
                x[1],
                x[3],
                x[2]
            ),
            reverse=True
        )

        best = scored_candidates[0]

        return best[0], best[1]

    # ---------------------------------------------------------
    # Main plate reading
    # ---------------------------------------------------------

    def read_plate(self, plate_crop):

        if plate_crop is None:
            return {
                "success": False,
                "plate": None,
                "first_number": None,
                "letter": None,
                "last_number": None,
                "ocr_confidence": 0.0,
                "detections": []
            }

        height, width = plate_crop.shape[:2]

        if width < 100 or height < 30:
            return {
                "success": False,
                "plate": None,
                "first_number": None,
                "letter": None,
                "last_number": None,
                "ocr_confidence": 0.0,
                "detections": []
            }

        # -----------------------------------------------------
        # Moroccan plate geometry
        #
        # left   = first number
        # middle = Arabic letter
        # right  = final 1-2 digits
        #
        # Keep the existing geometry so we don't disturb
        # the rest of the project.
        # -----------------------------------------------------

        left_end = int(width * 0.54)

        center_start = int(width * 0.54)
        center_end = int(width * 0.76)

        right_start = int(width * 0.76)

        left_zone = plate_crop[
            0:height,
            0:left_end
        ]

        center_zone = plate_crop[
            0:height,
            center_start:center_end
        ]

        right_zone = plate_crop[
            0:height,
            right_start:width
        ]

        # -----------------------------------------------------
        # Read each zone independently
        # -----------------------------------------------------

        first_result = self.read_digits(
            left_zone
        )

        letter_result = self.read_letter(
            center_zone
        )

        last_result = self.read_digits(
            right_zone
        )

        first_number = None
        first_confidence = 0.0

        if first_result:
            first_number = first_result[0]
            first_confidence = first_result[1]

        letter = None
        letter_confidence = 0.0

        if letter_result:
            letter = letter_result[0]
            letter_confidence = letter_result[1]

        last_number = None
        last_confidence = 0.0

        if last_result:
            last_number = last_result[0]
            last_confidence = last_result[1]

        # -----------------------------------------------------
        # Moroccan plate validation
        # -----------------------------------------------------

        valid_first = (
            first_number is not None
            and 1 <= len(first_number) <= 5
        )

        valid_last = (
            last_number is not None
            and 1 <= len(last_number) <= 2
        )

        valid_letter = (
            letter is not None
            and len(letter) == 1
        )

        success = (
            valid_first
            and valid_letter
            and valid_last
        )

        # -----------------------------------------------------
        # Average OCR confidence
        # -----------------------------------------------------

        confidence_values = []

        if valid_first:
            confidence_values.append(
                first_confidence
            )

        if valid_letter:
            confidence_values.append(
                letter_confidence
            )

        if valid_last:
            confidence_values.append(
                last_confidence
            )

        if confidence_values:
            ocr_confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )
        else:
            ocr_confidence = 0.0

        # -----------------------------------------------------
        # Build final plate
        # -----------------------------------------------------

        plate = None

        if success:
            plate = (
                f"{first_number} "
                f"{letter} "
                f"{last_number}"
            )

        # -----------------------------------------------------
        # Same response structure as before
        # -----------------------------------------------------

        return {
            "success": success,
            "plate": plate,
            "first_number": first_number,
            "letter": letter,
            "last_number": last_number,
            "ocr_confidence": round(
                ocr_confidence,
                4
            ),
            "detections": {
                "first_number": {
                    "value": first_number,
                    "confidence": round(
                        first_confidence,
                        4
                    )
                },
                "letter": {
                    "value": letter,
                    "confidence": round(
                        letter_confidence,
                        4
                    )
                },
                "last_number": {
                    "value": last_number,
                    "confidence": round(
                        last_confidence,
                        4
                    )
                }
            }
        }