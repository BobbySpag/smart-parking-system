"""Main parking space detector using OpenCV and CNN."""
import cv2
import numpy as np
import json
from pathlib import Path
from typing import Optional
from .preprocessor import preprocess_frame
from .utils import draw_parking_spaces


class ParkingDetector:
    """Detects parking space occupancy from video feeds or images using OpenCV and CNN."""

    def __init__(self, model_path: Optional[str] = None, annotations_path: Optional[str] = None):
        """Initialize the parking detector.

        Args:
            model_path: Path to a saved Keras .h5/.keras model file.
            annotations_path: Path to a JSON annotations file.
        """
        self.model = None
        self.annotations: list[dict] = []
        self.occupied_threshold: float = 0.5

        if model_path:
            self.load_model(model_path)
        if annotations_path:
            self.load_annotations(annotations_path)

    def load_model(self, model_path: str) -> None:
        """Load CNN model for classification.

        Args:
            model_path: Path to the saved Keras model.

        Raises:
            ImportError: If TensorFlow is not installed.
        """
        try:
            from tensorflow import keras
            self.model = keras.models.load_model(model_path)
        except ImportError:
            raise ImportError("TensorFlow is required for CNN-based detection.")

    def load_annotations(self, annotations_path: str) -> None:
        """Load parking space annotations from a JSON file.

        Args:
            annotations_path: Path to the JSON file containing space definitions.
        """
        with open(annotations_path, "r") as f:
            data = json.load(f)
        self.annotations = data.get("spaces", [])

    def crop_space(self, frame: np.ndarray, coordinates: list) -> np.ndarray:
        """Crop a parking space region from a frame.

        Args:
            frame: Source BGR image.
            coordinates: List of [x, y] polygon vertices.

        Returns:
            Cropped image patch for the space.
        """
        pts = np.array(coordinates, dtype=np.float32)
        x, y, w, h = cv2.boundingRect(pts.astype(np.int32))
        x = max(0, x)
        y = max(0, y)
        cropped = frame[y:y + h, x:x + w]
        return cropped

    def classify_space(self, space_img: np.ndarray) -> dict:
        """Classify a parking space patch as occupied or free.

        Uses the CNN model when available; otherwise falls back to a simple
        grayscale variance threshold.

        Args:
            space_img: BGR image patch of a single parking space.

        Returns:
            Dict with keys ``is_occupied`` (bool) and ``confidence`` (float).
        """
        if self.model is not None:
            resized = cv2.resize(space_img, (150, 150))
            normalized = resized.astype(np.float32) / 255.0
            batch = np.expand_dims(normalized, axis=0)
            prediction = float(self.model.predict(batch, verbose=0)[0][0])
            return {"is_occupied": prediction > self.occupied_threshold, "confidence": prediction}

        # Fallback: simple threshold on grayscale variance
        gray = cv2.cvtColor(space_img, cv2.COLOR_BGR2GRAY) if len(space_img.shape) == 3 else space_img
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        occupancy_ratio = np.sum(thresh > 0) / thresh.size
        return {"is_occupied": occupancy_ratio > 0.3, "confidence": float(occupancy_ratio)}

    def detect_from_frame(self, frame: np.ndarray) -> dict:
        """Detect occupancy of all annotated spaces in a single frame.

        Args:
            frame: BGR image array.

        Returns:
            Dict mapping space-id (str) → classification result dict.
        """
        processed = preprocess_frame(frame)
        results: dict[str, dict] = {}
        for space in self.annotations:
            space_id = space.get("id", space.get("space_number", len(results)))
            coords = space.get("coordinates", [])
            if not coords:
                continue
            crop = self.crop_space(frame, coords)
            if crop.size == 0:
                continue
            result = self.classify_space(crop)
            results[str(space_id)] = result
        return results

    def detect_from_image(self, image_path: str) -> dict:
        """Detect occupancy from a saved image file.

        Args:
            image_path: Path to the image file.

        Returns:
            Dict mapping space-id → classification result.

        Raises:
            ValueError: If the image cannot be loaded.
        """
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Could not load image: {image_path}")
        return self.detect_from_frame(frame)

    def detect_from_video(self, video_path: str, frame_interval: int = 30):
        """Yield occupancy results for frames from a video file.

        Args:
            video_path: Path to the video file.
            frame_interval: Process every N-th frame.

        Yields:
            Dicts with keys ``frame`` (int) and ``occupancy`` (dict).
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % frame_interval == 0:
                    results = self.detect_from_frame(frame)
                    yield {"frame": frame_count, "occupancy": results}
                frame_count += 1
        finally:
            cap.release()

    def detect_from_camera(self, camera_id: int = 0, frame_interval: int = 30):
        """Yield occupancy results from a live camera feed.

        Args:
            camera_id: OpenCV camera index.
            frame_interval: Process every N-th frame.

        Yields:
            Dicts with keys ``frame``, ``occupancy``, and ``annotated_frame``.
        """
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise ValueError(f"Could not open camera: {camera_id}")
        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % frame_interval == 0:
                    results = self.detect_from_frame(frame)
                    annotated = draw_parking_spaces(frame.copy(), self.annotations, results)
                    yield {"frame": frame_count, "occupancy": results, "annotated_frame": annotated}
                frame_count += 1
        finally:
            cap.release()
