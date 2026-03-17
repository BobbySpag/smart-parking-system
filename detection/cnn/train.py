"""Training script for the parking space occupancy CNN.

Usage::

    python -m detection.cnn.train \\
        --data-dir datasets/pklot \\
        --output-dir model_weights \\
        --epochs 50 \\
        --batch-size 32
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the training script."""
    parser = argparse.ArgumentParser(description="Train parking space occupancy CNN")
    parser.add_argument("--data-dir", required=True, help="Root dataset directory with free/ and occupied/ sub-folders")
    parser.add_argument("--output-dir", default="model_weights", help="Directory to save model and logs")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--val-split", type=float, default=0.2, help="Fraction of data for validation")
    parser.add_argument("--image-size", type=int, default=150, help="Square image size fed to the model")
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--no-augmentation", action="store_true", help="Disable data augmentation")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def build_generators(data_dir: str, image_size: int, batch_size: int, val_split: float, augment: bool):
    """Create Keras ImageDataGenerators for train and validation splits.

    Args:
        data_dir: Root directory containing ``free/`` and ``occupied/`` sub-folders.
        image_size: Target square image dimension.
        batch_size: Mini-batch size.
        val_split: Fraction of images reserved for validation.
        augment: Whether to apply random augmentations to the training set.

    Returns:
        Tuple of (train_generator, val_generator).
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    if augment:
        train_datagen = ImageDataGenerator(
            rescale=1.0 / 255,
            validation_split=val_split,
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            shear_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True,
            brightness_range=(0.8, 1.2),
            fill_mode="nearest",
        )
    else:
        train_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=val_split)

    val_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=val_split)

    target_size = (image_size, image_size)
    train_gen = train_datagen.flow_from_directory(
        data_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode="binary",
        subset="training",
        shuffle=True,
    )
    val_gen = val_datagen.flow_from_directory(
        data_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode="binary",
        subset="validation",
        shuffle=False,
    )
    return train_gen, val_gen


def build_callbacks(output_dir: str):
    """Build training callbacks: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau.

    Args:
        output_dir: Directory where the best model checkpoint is saved.

    Returns:
        List of Keras callback objects.
    """
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

    os.makedirs(output_dir, exist_ok=True)
    checkpoint_path = str(Path(output_dir) / "best_model.keras")

    return [
        EarlyStopping(monitor="val_auc", patience=10, restore_best_weights=True, mode="max", verbose=1),
        ModelCheckpoint(
            checkpoint_path, monitor="val_auc", save_best_only=True, mode="max", verbose=1
        ),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-7, verbose=1),
    ]


def plot_history(history, output_dir: str) -> None:
    """Save training history plots to *output_dir*.

    Args:
        history: Keras History object returned by ``model.fit``.
        output_dir: Directory to write PNG files.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed – skipping history plots.")
        return

    os.makedirs(output_dir, exist_ok=True)
    metrics = [("accuracy", "Accuracy"), ("loss", "Loss"), ("auc", "AUC")]
    for metric, title in metrics:
        if metric not in history.history:
            continue
        fig, ax = plt.subplots()
        ax.plot(history.history[metric], label="train")
        val_key = f"val_{metric}"
        if val_key in history.history:
            ax.plot(history.history[val_key], label="val")
        ax.set_title(title)
        ax.set_xlabel("Epoch")
        ax.legend()
        fig.savefig(str(Path(output_dir) / f"{metric}.png"))
        plt.close(fig)
    print(f"History plots saved to {output_dir}/")


def train(args: argparse.Namespace) -> None:
    """Execute the full training pipeline.

    Args:
        args: Parsed command-line arguments.
    """
    import tensorflow as tf
    tf.random.set_seed(args.seed)
    np.random.seed(args.seed)

    from .model import build_cnn_model
    from .data_loader import get_class_weights

    print(f"Building generators from {args.data_dir} ...")
    train_gen, val_gen = build_generators(
        data_dir=args.data_dir,
        image_size=args.image_size,
        batch_size=args.batch_size,
        val_split=args.val_split,
        augment=not args.no_augmentation,
    )

    print("Building model ...")
    model = build_cnn_model(
        input_shape=(args.image_size, args.image_size, 3),
        dropout_rate=args.dropout,
    )
    model.summary()

    # Optional class-weight balancing
    class_weights = None
    try:
        class_weights = get_class_weights(train_gen)
        print(f"Class weights: {class_weights}")
    except Exception as exc:
        print(f"Could not compute class weights: {exc}")

    callbacks = build_callbacks(args.output_dir)

    print(f"Training for up to {args.epochs} epoch(s) ...")
    history = model.fit(
        train_gen,
        epochs=args.epochs,
        validation_data=val_gen,
        callbacks=callbacks,
        class_weight=class_weights,
    )

    # Save final model
    final_path = str(Path(args.output_dir) / "final_model.keras")
    model.save(final_path)
    print(f"Final model saved to {final_path}")

    plot_history(history, args.output_dir)


def main() -> None:
    """CLI entry point."""
    train(parse_args())


if __name__ == "__main__":
    main()
