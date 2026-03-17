"""OpenCV-based GUI tool for annotating parking spaces in images.

Usage::

    python -m detection.annotator --image path/to/image.jpg --output annotations.json

Keyboard shortcuts:
    s   – save annotations to the output file
    c   – clear the most recently drawn space
    r   – reset all annotations
    q   – quit without saving
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from .utils import load_annotations, save_annotations


class ParkingAnnotator:
    """Interactive GUI tool for drawing and saving parking space annotations."""

    def __init__(self, image_path: str, output_path: str = "annotations.json"):
        """Initialise the annotator.

        Args:
            image_path: Path to the image file to annotate.
            output_path: Path where the annotation JSON will be saved.
        """
        self.image_path = image_path
        self.output_path = output_path
        self.annotations: list[dict] = []
        self.current_polygon: list[list[int]] = []
        self.window_name = "Parking Annotator"

        # Load existing annotations if file exists
        if Path(output_path).exists():
            try:
                self.annotations = load_annotations(output_path)
                print(f"Loaded {len(self.annotations)} existing annotation(s).")
            except Exception as exc:
                print(f"Warning: could not load existing annotations: {exc}")

        # Load and copy the source image
        self._source = cv2.imread(image_path)
        if self._source is None:
            raise ValueError(f"Could not load image: {image_path}")
        self._display = self._source.copy()

    # ------------------------------------------------------------------
    # Mouse callback
    # ------------------------------------------------------------------

    def _mouse_callback(self, event: int, x: int, y: int, flags: int, param: object) -> None:
        """Handle mouse events for polygon drawing."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_polygon.append([x, y])
            self._redraw()

        elif event == cv2.EVENT_RBUTTONDOWN and self.current_polygon:
            # Right-click closes the polygon and saves the space
            if len(self.current_polygon) >= 3:
                space = {
                    "id": str(uuid.uuid4()),
                    "space_number": str(len(self.annotations) + 1),
                    "coordinates": self.current_polygon.copy(),
                }
                self.annotations.append(space)
                print(f"  Added space #{space['space_number']} with {len(self.current_polygon)} pts")
            self.current_polygon = []
            self._redraw()

        elif event == cv2.EVENT_MOUSEMOVE and self.current_polygon:
            # Live preview: show edge from last point to cursor
            preview = self._display.copy()
            cv2.line(preview, tuple(self.current_polygon[-1]), (x, y), (255, 165, 0), 1)
            cv2.imshow(self.window_name, preview)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _redraw(self) -> None:
        """Redraw all saved annotations and the in-progress polygon."""
        self._display = self._source.copy()

        # Draw saved spaces
        for space in self.annotations:
            pts = np.array(space["coordinates"], dtype=np.int32)
            cv2.polylines(self._display, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            x0, y0 = pts[0]
            cv2.putText(
                self._display, space["space_number"], (x0, y0 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
            )

        # Draw in-progress polygon
        if self.current_polygon:
            pts = np.array(self.current_polygon, dtype=np.int32)
            cv2.polylines(self._display, [pts], isClosed=False, color=(0, 165, 255), thickness=2)
            for pt in self.current_polygon:
                cv2.circle(self._display, tuple(pt), 4, (0, 165, 255), -1)

        cv2.imshow(self.window_name, self._display)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> list[dict]:
        """Open the annotation GUI and block until the user quits.

        Returns:
            Final list of annotation dicts.
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        self._redraw()

        print("\nInstructions:")
        print("  Left-click  – add polygon vertex")
        print("  Right-click – close polygon (≥3 points required)")
        print("  s           – save annotations")
        print("  c           – undo last space")
        print("  r           – reset all spaces")
        print("  q           – quit\n")

        while True:
            key = cv2.waitKey(20) & 0xFF
            if key == ord("q"):
                print("Quitting without saving.")
                break
            elif key == ord("s"):
                self._save()
            elif key == ord("c"):
                if self.current_polygon:
                    self.current_polygon = []
                elif self.annotations:
                    removed = self.annotations.pop()
                    print(f"  Removed space #{removed['space_number']}")
                self._redraw()
            elif key == ord("r"):
                self.annotations = []
                self.current_polygon = []
                print("  All annotations cleared.")
                self._redraw()

        cv2.destroyAllWindows()
        return self.annotations

    def _save(self) -> None:
        """Write annotations to the output JSON file."""
        save_annotations(self.annotations, self.output_path)
        print(f"  Saved {len(self.annotations)} annotation(s) to {self.output_path}")


def main() -> None:
    """CLI entry point for the parking annotator tool."""
    parser = argparse.ArgumentParser(description="Annotate parking spaces in an image.")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument(
        "--output", default="annotations.json", help="Output JSON path (default: annotations.json)"
    )
    args = parser.parse_args()

    annotator = ParkingAnnotator(args.image, args.output)
    annotations = annotator.run()
    print(f"Done. {len(annotations)} space(s) annotated.")


if __name__ == "__main__":
    main()
