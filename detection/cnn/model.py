"""CNN model architecture for parking space occupancy classification."""
from typing import Tuple


def build_cnn_model(input_shape: Tuple[int, int, int] = (150, 150, 3), dropout_rate: float = 0.5):
    """Build a CNN model for binary parking space classification.

    Architecture:
        Four conv blocks (Conv2D → BatchNorm → MaxPool) followed by two
        fully-connected layers and a sigmoid output neuron.

    Args:
        input_shape: (height, width, channels) of the input images.
        dropout_rate: Dropout fraction applied after the first dense layer.

    Returns:
        Compiled ``keras.Sequential`` model.
    """
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(dropout_rate),
        layers.Dense(256, activation='relu'),
        layers.Dropout(dropout_rate / 2),
        layers.Dense(1, activation='sigmoid'),
    ], name='parking_occupancy_cnn')

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss='binary_crossentropy',
        metrics=['accuracy', keras.metrics.AUC(name='auc')]
    )
    return model


def load_model(model_path: str):
    """Load a saved CNN model from disk.

    Args:
        model_path: Path to the saved Keras model file (.h5 or SavedModel dir).

    Returns:
        Loaded and compiled Keras model.
    """
    from tensorflow import keras
    return keras.models.load_model(model_path)
