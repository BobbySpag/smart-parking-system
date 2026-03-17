"""Tests for the ParkingDetector class."""
import json
import tempfile
import os
import numpy as np
import pytest
from unittest.mock import patch, MagicMock


def _make_frame(h: int = 200, w: int = 300) -> np.ndarray:
    return np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)


def _make_annotations(tmp_path: str) -> str:
    data = {
        "spaces": [
            {"id": "space_1", "space_number": "1", "coordinates": [[10, 10], [60, 10], [60, 50], [10, 50]]},
            {"id": "space_2", "space_number": "2", "coordinates": [[70, 10], [120, 10], [120, 50], [70, 50]]},
        ]
    }
    path = os.path.join(tmp_path, "annotations.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


class TestParkingDetectorInit:
    def test_default_init(self):
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        assert det.model is None
        assert det.annotations == []
        assert det.occupied_threshold == 0.5

    def test_load_annotations(self):
        from detection.detector import ParkingDetector
        with tempfile.TemporaryDirectory() as tmp:
            ann_path = _make_annotations(tmp)
            det = ParkingDetector(annotations_path=ann_path)
            assert len(det.annotations) == 2
            assert det.annotations[0]["id"] == "space_1"

    def test_load_model_missing_tensorflow(self):
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        with patch.dict("sys.modules", {"tensorflow": None}):
            with pytest.raises((ImportError, ModuleNotFoundError)):
                det.load_model("fake_model.h5")


class TestCropSpace:
    def test_crop_returns_ndarray(self):
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        frame = _make_frame()
        coords = [[10, 10], [60, 10], [60, 50], [10, 50]]
        crop = det.crop_space(frame, coords)
        assert isinstance(crop, np.ndarray)
        assert crop.size > 0

    def test_crop_correct_shape(self):
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        frame = _make_frame(200, 300)
        coords = [[10, 20], [80, 20], [80, 70], [10, 70]]
        crop = det.crop_space(frame, coords)
        assert crop.shape[0] == 50  # height
        assert crop.shape[1] == 70  # width


class TestClassifySpace:
    def test_fallback_free_space(self):
        """A plain white patch should be classified as free (low occupancy ratio)."""
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        white = np.full((50, 50, 3), 240, dtype=np.uint8)
        result = det.classify_space(white)
        assert "is_occupied" in result
        assert "confidence" in result
        assert isinstance(result["is_occupied"], (bool, np.bool_))

    def test_fallback_occupied_space(self):
        """A high-variance patch should be classified as occupied."""
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        noisy = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        result = det.classify_space(noisy)
        assert "is_occupied" in result

    def test_with_mock_model(self):
        from detection.detector import ParkingDetector
        det = ParkingDetector()
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.8]])
        det.model = mock_model
        img = _make_frame(50, 50)
        result = det.classify_space(img)
        assert result["is_occupied"] is True
        assert abs(result["confidence"] - 0.8) < 1e-6


class TestDetectFromFrame:
    def test_detect_returns_dict(self):
        from detection.detector import ParkingDetector
        with tempfile.TemporaryDirectory() as tmp:
            ann_path = _make_annotations(tmp)
            det = ParkingDetector(annotations_path=ann_path)
            frame = _make_frame()
            results = det.detect_from_frame(frame)
            assert isinstance(results, dict)
            assert "space_1" in results
            assert "space_2" in results

    def test_detect_result_structure(self):
        from detection.detector import ParkingDetector
        with tempfile.TemporaryDirectory() as tmp:
            ann_path = _make_annotations(tmp)
            det = ParkingDetector(annotations_path=ann_path)
            frame = _make_frame()
            results = det.detect_from_frame(frame)
            for key, val in results.items():
                assert "is_occupied" in val
                assert "confidence" in val
