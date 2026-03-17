"""Dataset utilities for loading and preparing parking occupancy datasets."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def load_pklot_dataset(root_dir: str, image_size: int = 150) -> tuple[np.ndarray, np.ndarray]:
    """Load images from the PKLot dataset directory structure.

    Expected layout::

        root_dir/
            OCCUPIED/   *.jpg
            FREE/       *.jpg

    Args:
        root_dir: Root directory of the PKLot dataset.
        image_size: Square size to resize each image to.

    Returns:
        Tuple of (images, labels) numpy arrays.
        Labels: 1 = occupied, 0 = free.
    """
    import cv2

    images: list[np.ndarray] = []
    labels: list[int] = []
    root = Path(root_dir)

    class_map = {"OCCUPIED": 1, "occupied": 1, "FREE": 0, "free": 0}
    for class_name, label in class_map.items():
        class_dir = root / class_name
        if not class_dir.exists():
            continue
        for img_path in sorted(class_dir.glob("*.jpg")):
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            img = cv2.resize(img, (image_size, image_size))
            images.append(img.astype(np.float32) / 255.0)
            labels.append(label)

    return np.array(images), np.array(labels)


def load_cnrpark_dataset(root_dir: str, image_size: int = 150) -> tuple[np.ndarray, np.ndarray]:
    """Load images from the CNRPark dataset directory structure.

    Expected layout::

        root_dir/
            0/   *.jpg   (free)
            1/   *.jpg   (occupied)

    Args:
        root_dir: Root directory of the CNRPark dataset.
        image_size: Square size to resize each image to.

    Returns:
        Tuple of (images, labels) numpy arrays.
    """
    import cv2

    images: list[np.ndarray] = []
    labels: list[int] = []
    root = Path(root_dir)

    for label_str in ("0", "1"):
        label = int(label_str)
        class_dir = root / label_str
        if not class_dir.exists():
            continue
        for img_path in sorted(class_dir.glob("*.jpg")):
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            img = cv2.resize(img, (image_size, image_size))
            images.append(img.astype(np.float32) / 255.0)
            labels.append(label)

    return np.array(images), np.array(labels)


def create_data_generators(
    data_dir: str,
    image_size: int = 150,
    batch_size: int = 32,
    val_split: float = 0.2,
    augment: bool = True,
    seed: int = 42,
):
    """Create Keras ImageDataGenerators for a directory with class sub-folders.

    Args:
        data_dir: Root directory with ``free/`` and ``occupied/`` (or similar) sub-folders.
        image_size: Square target size.
        batch_size: Mini-batch size.
        val_split: Validation fraction.
        augment: Enable augmentation for the training generator.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (train_generator, val_generator).
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    common = dict(rescale=1.0 / 255, validation_split=val_split)
    aug = dict(
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        brightness_range=(0.8, 1.2),
        fill_mode="nearest",
    )

    train_gen_params = {**common, **(aug if augment else {})}
    train_datagen = ImageDataGenerator(**train_gen_params)
    val_datagen = ImageDataGenerator(**common)

    flow_kwargs: dict[str, Any] = dict(
        target_size=(image_size, image_size),
        batch_size=batch_size,
        class_mode="binary",
        seed=seed,
    )

    train_gen = train_datagen.flow_from_directory(data_dir, subset="training", shuffle=True, **flow_kwargs)
    val_gen = val_datagen.flow_from_directory(data_dir, subset="validation", shuffle=False, **flow_kwargs)
    return train_gen, val_gen


def get_class_weights(generator) -> dict[int, float]:
    """Compute balanced class weights from a Keras data generator.

    Args:
        generator: Keras flow_from_directory generator with ``.classes`` attribute.

    Returns:
        Dict mapping class index → weight.
    """
    from sklearn.utils.class_weight import compute_class_weight

    classes = np.unique(generator.classes)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=generator.classes)
    return dict(zip(classes.tolist(), weights.tolist()))


def augment_dataset(
    images: np.ndarray,
    labels: np.ndarray,
    augmentation_factor: int = 2,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Augment a numpy dataset by applying random transforms.

    Args:
        images: Float32 array of shape (N, H, W, C) in [0, 1].
        labels: Integer label array of shape (N,).
        augmentation_factor: Number of augmented copies per original image.
        seed: Random seed.

    Returns:
        Tuple of (augmented_images, augmented_labels) concatenated with originals.
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    rng = np.random.default_rng(seed)
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        brightness_range=(0.7, 1.3),
        fill_mode="nearest",
    )

    aug_images: list[np.ndarray] = [images]
    aug_labels: list[np.ndarray] = [labels]

    for _ in range(augmentation_factor):
        transformed = np.stack([
            next(datagen.flow(img[np.newaxis], batch_size=1, seed=int(rng.integers(1e6))))[0]
            for img in images
        ])
        aug_images.append(transformed)
        aug_labels.append(labels)

    return np.concatenate(aug_images, axis=0), np.concatenate(aug_labels, axis=0)
