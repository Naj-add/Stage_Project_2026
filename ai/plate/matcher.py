import re


def normalize_plate(plate: str | None):

    if not plate:
        return None

    plate = plate.strip()

    plate = plate.replace(
        " ",
        ""
    )

    plate = plate.replace(
        "-",
        ""
    )

    plate = plate.replace(
        "|",
        ""
    )

    return plate


def compare_plates(
    entrance_plate: str | None,
    exit_plate: str | None
):

    entrance = normalize_plate(
        entrance_plate
    )

    exit_plate_normalized = normalize_plate(
        exit_plate
    )

    if not entrance:

        return {
            "match": False,
            "status": "ENTRANCE_PLATE_NOT_DETECTED",
            "reason":
                "Entrance plate could not be detected"
        }

    if not exit_plate_normalized:

        return {
            "match": False,
            "status": "EXIT_PLATE_NOT_DETECTED",
            "reason":
                "Exit plate could not be detected"
        }

    if entrance == exit_plate_normalized:

        return {
            "match": True,
            "status": "VEHICLE_VERIFIED",
            "entrance_plate": entrance_plate,
            "exit_plate": exit_plate,
            "reason":
                "Entrance and exit plates match"
        }

    return {
        "match": False,
        "status": "PLATE_MISMATCH",
        "entrance_plate": entrance_plate,
        "exit_plate": exit_plate,
        "reason":
            "Entrance and exit plates do not match"
    }