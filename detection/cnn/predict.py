"""Prediction utilities for the parking space occupancy CNN."""
from __future__ import annotations

from pathlib import Path
from typing import Generator

import cv2
import numpy as np


def load_model(model_path: str):
    """Load a saved Keras model from *model_path*.

    Args:
        model_path: Path to the ``.h5`` or SavedModel directory.

    Returns:
        Loaded Keras model.
    """
    from tensorflow import keras
    return keras.models.load_model(model_path)


def predict_single_image(
    model,
    image_path: str,
    image_size: int = 150,
    threshold: float = 0.5,
) -> dict:
    """Predict occupancy for a single image file.

    Args:
        model: Loaded Keras model.
        image_path: Path to the image to classify.
        image_size: Square target size expected by the model.
        threshold: Decision threshold for the occupied class.

    Returns:
        Dict with keys ``image_path``, ``is_occupied``, ``confidence``.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot load image: {image_path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(img_rgb, (image_size, image_size))
    normalized = resized.astype(np.float32) / 255.0
    batch = np.expand_dims(normalized, axis=0)
    confidence = float(model.predict(batch, verbose=0)[0][0])
    return {
        "image_path": image_path,
        "is_occupied": confidence >= threshold,
        "confidence": confidence,
    }


def predict_batch(
    model,
    image_paths: list[str],
    image_size: int = 150,
    threshold: float = 0.5,
    batch_size: int = 32,
) -> list[dict]:
    """Predict occupancy for a batch of image files.

    Args:
        model: Loaded Keras model.
        image_paths: List of paths to image files.
        image_size: Square target size expected by the model.
        threshold: Decision threshold for the occupied class.
        batch_size: Number of images to process per forward pass.

    Returns:
        List of result dicts (same format as :func:`predict_single_image`).
    """
    results: list[dict] = []
    images: list[np.ndarray] = []
    paths_buffer: list[str] = []

    def _flush(imgs: list, paths: list) -> list[dict]:
        arr = np.stack(imgs, axis=0)
        preds = model.predict(arr, verbose=0)
        out = []
        for path, conf in zip(paths, preds[:, 0]):
            out.append({
                "image_path": path,
                "is_occupied": float(conf) >= threshold,
                "confidence": float(conf),
            })
        return out

    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            results.append({"image_path": path, "is_occupied": None, "confidence": None, "error": "Cannot load"})
            continue
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(img_rgb, (image_size, image_size)).astype(np.float32) / 255.0
        images.append(resized)
        paths_buffer.append(path)

        if len(images) >= batch_size:
            results.extend(_flush(images, paths_buffer))
            images = []
            paths_buffer = []

    if images:
        results.extend(_flush(images, paths_buffer))

    return results


def predict_directory(
    model,
    directory: str,
    image_size: int = 150,
    threshold: float = 0.5,
    extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp"),
) -> Generator[dict, None, None]:
    """Yield predictions for every image found in *directory*.

    Args:
        model: Loaded Keras model.
        directory: Path to directory containing image files.
        image_size: Square target size expected by the model.
        threshold: Decision threshold for the occupied class.
        extensions: Tuple of accepted file extensions (lower-case).

    Yields:
        Result dicts with keys ``image_path``, ``is_occupied``, ``confidence``.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    for image_path in sorted(dir_path.rglob("*")):
        if image_path.suffix.lower() in extensions:
            yield predict_single_image(model, str(image_path), image_size, threshold)
