"""Image and video preprocessing utilities for the parking detector."""
from __future__ import annotations

import cv2
import numpy as np
from pathlib import Path
from typing import Generator


def preprocess_frame(frame: np.ndarray, target_size: tuple[int, int] | None = None) -> np.ndarray:
    """Apply a standard preprocessing pipeline to a video frame.

    Steps: optional resize → Gaussian blur → contrast normalisation.

    Args:
        frame: BGR image array from OpenCV.
        target_size: Optional (width, height) to resize to before processing.

    Returns:
        Preprocessed BGR frame.
    """
    if target_size is not None:
        frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
    frame = apply_blur(frame, kernel_size=3)
    return frame


def extract_frames_from_video(
    video_path: str,
    frame_interval: int = 30,
    max_frames: int | None = None,
) -> Generator[tuple[int, np.ndarray], None, None]:
    """Yield (frame_number, frame) tuples from a video file at a given interval.

    Args:
        video_path: Path to the video file.
        frame_interval: Extract every N-th frame.
        max_frames: Stop after yielding this many frames (None = no limit).

    Yields:
        Tuples of (frame_index, BGR frame array).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    frame_idx = 0
    yielded = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                yield frame_idx, frame
                yielded += 1
                if max_frames is not None and yielded >= max_frames:
                    break
            frame_idx += 1
    finally:
        cap.release()


def resize_image(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize *image* to the given (width, height) using area interpolation.

    Args:
        image: Input image array.
        width: Target width in pixels.
        height: Target height in pixels.

    Returns:
        Resized image array.
    """
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalise pixel values to the [0, 1] float32 range.

    Args:
        image: Input image array (uint8 or float).

    Returns:
        Float32 array with values in [0, 1].
    """
    return image.astype(np.float32) / 255.0


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert a BGR image to single-channel grayscale.

    Args:
        image: BGR image array. If already grayscale, returns as-is.

    Returns:
        Grayscale image array.
    """
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_threshold(
    image: np.ndarray,
    method: str = "otsu",
    threshold_value: int = 127,
) -> np.ndarray:
    """Apply binary thresholding to a grayscale image.

    Args:
        image: Grayscale image array.
        method: ``"otsu"`` for automatic Otsu thresholding or ``"binary"``
                for a fixed threshold.
        threshold_value: Used only when *method* is ``"binary"``.

    Returns:
        Binary (0/255) image array.
    """
    gray = to_grayscale(image)
    if method == "otsu":
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    return thresh


def apply_edge_detection(
    image: np.ndarray,
    low_threshold: int = 50,
    high_threshold: int = 150,
) -> np.ndarray:
    """Apply Canny edge detection.

    Args:
        image: BGR or grayscale image array.
        low_threshold: Lower hysteresis threshold for Canny.
        high_threshold: Upper hysteresis threshold for Canny.

    Returns:
        Edge image (uint8) with detected edges as white pixels.
    """
    gray = to_grayscale(image)
    return cv2.Canny(gray, low_threshold, high_threshold)


def apply_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Apply Gaussian blur to reduce noise.

    Args:
        image: Input image array.
        kernel_size: Size of the Gaussian kernel (must be odd).

    Returns:
        Blurred image array.
    """
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.GaussianBlur(image, (k, k), 0)
