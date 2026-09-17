import sys
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:5000"

OPERATION_ID = 42

ENTRANCE_IMAGE = (
    r"C:\Users\Hp\Downloads\Moroccan License Plate.v1i.yolov8\test\images\IMG_0065_jpg.rf.f2bbcde34ec7414efbbcb5ae2d9edfbb.jpg"
)

EXIT_IMAGE = (
    r"C:\Users\Hp\Downloads\Moroccan License Plate.v1i.yolov8\test\images\IMG_0065_jpg.rf.f2bbcde34ec7414efbbcb5ae2d9edfbb.jpg"

)


# ============================================================
# TOKEN
# ============================================================

# Paste your current JWT token here if it is not already
# available through the environment.
#
# PowerShell version:
#
# $env:ZETA_TOKEN = "YOUR_TOKEN"
#
# Then this script will automatically use it.

import os

TOKEN = os.environ.get("ZETA_TOKEN")


# ============================================================
# HELPERS
# ============================================================

def check_file(path, label):
    print(f"Checking {label} image...")

    if not os.path.exists(path):
        print(f"ERROR: {label} image does not exist:")
        print(path)
        return False

    size = os.path.getsize(path)

    print(f"{label} image OK")
    print(f"Path: {path}")
    print(f"Size: {size / 1024:.2f} KB")
    print()

    return True


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print()
    print("=" * 60)
    print("          ZETA-MESURE PLATE VERIFICATION TEST")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Check token
    # --------------------------------------------------------

    if not TOKEN:
        print("ERROR: ZETA_TOKEN is not set.")
        print()
        print("In PowerShell, run:")
        print()
        print('$env:ZETA_TOKEN = "YOUR_JWT_TOKEN"')
        print()
        print("Then run this script again.")
        print()
        sys.exit(1)

    print("JWT token detected.")
    print()

    # --------------------------------------------------------
    # Check images
    # --------------------------------------------------------

    if not check_file(
        ENTRANCE_IMAGE,
        "Entrance"
    ):
        sys.exit(1)

    if not check_file(
        EXIT_IMAGE,
        "Exit"
    ):
        sys.exit(1)

    # --------------------------------------------------------
    # API URL
    # --------------------------------------------------------

    url = (
        f"{BASE_URL}"
        f"/api/ai/operations/"
        f"{OPERATION_ID}"
        f"/plate/verify"
    )

    print("API URL:")
    print(url)
    print()

    # --------------------------------------------------------
    # Headers
    # --------------------------------------------------------

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    # --------------------------------------------------------
    # Send images
    # --------------------------------------------------------

    try:

        with open(
            ENTRANCE_IMAGE,
            "rb"
        ) as entrance_file, open(
            EXIT_IMAGE,
            "rb"
        ) as exit_file:

            files = {
                "entrance_image": (
                    os.path.basename(ENTRANCE_IMAGE),
                    entrance_file,
                    "image/jpeg"
                ),
                "exit_image": (
                    os.path.basename(EXIT_IMAGE),
                    exit_file,
                    "image/jpeg"
                )
            }

            print("=" * 60)
            print("Sending images to Flask...")
            print("=" * 60)
            print()

            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=120
            )

    except requests.exceptions.ConnectionError:

        print()
        print("ERROR: Could not connect to Flask.")
        print()
        print("Make sure your backend is running:")
        print()
        print(
            r"cd C:\Users\Hp\Documents\Project_Stage-Car-WV"
            r"\zeta-mesure\backend"
        )
        print()
        print(
            r"set PYTHONPATH=.."
        )
        print()
        print(
            r".venv\Scripts\python.exe -m app.main"
        )
        print()

        sys.exit(1)

    except requests.exceptions.Timeout:

        print()
        print("ERROR: The request timed out.")
        print("OCR/AI may be taking too long.")
        print()

        sys.exit(1)

    except Exception as error:

        print()
        print("ERROR while sending request:")
        print(str(error))
        print()

        sys.exit(1)

    # --------------------------------------------------------
    # Display response
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("              PLATE VERIFICATION RESULT")
    print("=" * 60)
    print()

    print(f"HTTP Status: {response.status_code}")
    print()

    try:

        result = response.json()

        print("JSON Response:")
        print()

        import json

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )

    except Exception:

        print("Raw response:")
        print()
        print(response.text)

    print()
    print("=" * 60)
    print("                    TEST FINISHED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()