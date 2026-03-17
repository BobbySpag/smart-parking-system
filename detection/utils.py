"""Utility functions for the parking detection module."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np


# Colours (BGR) used for drawing
_COLOUR_FREE = (0, 255, 0)       # green
_COLOUR_OCCUPIED = (0, 0, 255)   # red
_COLOUR_UNKNOWN = (200, 200, 0)  # yellow


def draw_parking_spaces(
    frame: np.ndarray,
    annotations: list[dict],
    results: dict[str, dict],
) -> np.ndarray:
    """Draw coloured bounding boxes on *frame* for each annotated space.

    Args:
        frame: BGR image to draw on (modified in-place).
        annotations: List of annotation dicts with ``id``/``space_number``
                     and ``coordinates`` keys.
        results: Mapping of space-id → ``{"is_occupied": bool, "confidence": float}``.

    Returns:
        The annotated frame.
    """
    for space in annotations:
        space_id = str(space.get("id", space.get("space_number", "")))
        coords = space.get("coordinates", [])
        if not coords:
            continue

        pts = np.array(coords, dtype=np.int32)
        info = results.get(space_id, {})
        if "is_occupied" not in info:
            colour = _COLOUR_UNKNOWN
        elif info["is_occupied"]:
            colour = _COLOUR_OCCUPIED
        else:
            colour = _COLOUR_FREE

        cv2.polylines(frame, [pts], isClosed=True, color=colour, thickness=2)

        # Label
        x, y = pts[0]
        label = f"{space_id}"
        conf = info.get("confidence")
        if conf is not None:
            label += f" {conf:.0%}"
        cv2.putText(frame, label, (x, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colour, 1)

    return frame


def calculate_iou(box_a: list[float], box_b: list[float]) -> float:
    """Calculate the Intersection over Union (IoU) of two axis-aligned bounding boxes.

    Args:
        box_a: ``[x_min, y_min, x_max, y_max]`` for box A.
        box_b: ``[x_min, y_min, x_max, y_max]`` for box B.

    Returns:
        IoU value in [0, 1].
    """
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])

    inter_w = max(0.0, xb - xa)
    inter_h = max(0.0, yb - ya)
    inter_area = inter_w * inter_h

    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union_area = area_a + area_b - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area / union_area)


def load_annotations(annotations_path: str) -> list[dict]:
    """Load parking space annotations from a JSON file.

    Args:
        annotations_path: Path to the JSON file.

    Returns:
        List of annotation dicts.
    """
    path = Path(annotations_path)
    if not path.exists():
        raise FileNotFoundError(f"Annotations file not found: {annotations_path}")
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    return data.get("spaces", [])


def save_annotations(annotations: list[dict], output_path: str) -> None:
    """Persist parking space annotations to a JSON file.

    Args:
        annotations: List of annotation dicts to save.
        output_path: Destination file path.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"spaces": annotations}, f, indent=2)


def format_occupancy_summary(results: dict[str, dict]) -> str:
    """Format a human-readable summary string from detection results.

    Args:
        results: Mapping of space-id → ``{"is_occupied": bool, "confidence": float}``.

    Returns:
        Multi-line summary string.
    """
    total = len(results)
    occupied = sum(1 for v in results.values() if v.get("is_occupied"))
    free = total - occupied
    lines = [
        f"Total spaces : {total}",
        f"Occupied     : {occupied}",
        f"Free         : {free}",
    f"Occupancy    : {occupied / total:.1%}" if total > 0 else "Occupancy    : N/A",
        "",
        "Per-space results:",
    ]
    for space_id, info in sorted(results.items()):
        status = "OCCUPIED" if info.get("is_occupied") else "FREE"
        conf = info.get("confidence")
        conf_str = f" (conf={conf:.2f})" if conf is not None else ""
        lines.append(f"  Space {space_id}: {status}{conf_str}")
    return "\n".join(lines)
