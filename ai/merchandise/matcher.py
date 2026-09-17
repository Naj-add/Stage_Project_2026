import re
import unicodedata


def normalize_product(value: str) -> str:
    """
    Normalize product names before comparison.
    """

    if value is None:
        return ""

    value = str(value).strip().lower()

    value = unicodedata.normalize(
        "NFKD",
        value
    )

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )

    value = re.sub(
        r"[^a-z0-9]+",
        "",
        value
    )

    return value


def match_product(
    detected_product: str,
    expected_product: str
):
    detected = normalize_product(
        detected_product
    )

    expected = normalize_product(
        expected_product
    )

    matched = (
        detected != ""
        and expected != ""
        and detected == expected
    )

    result = {
        "detected_product": detected_product,
        "expected_product": expected_product,
        "match": matched,
    }

    if matched:
        result["reason"] = (
            "Detected product matches expected product"
        )
    else:
        result["reason"] = (
            "Detected product does not match expected product"
        )

    return result