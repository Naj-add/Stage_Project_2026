from pathlib import Path

import cv2
import numpy as np


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def validate_image_path(image_path: str) -> Path:
    """
    Validate that the supplied path points to an allowed image.
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {path.suffix}"
        )

    return path


def load_image(image_path: str):
    """
    Load an image using OpenCV.
    """
    path = validate_image_path(image_path)

    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    return image


def save_uploaded_image(file_storage, destination: str):
    """
    Save a Flask uploaded file to disk.
    """
    destination_path = Path(destination)

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_storage.save(str(destination_path))

    return destination_path


def image_to_numpy(image_path: str):
    """
    Load an image as a NumPy array.
    """
    image = load_image(image_path)

    return np.asarray(image)