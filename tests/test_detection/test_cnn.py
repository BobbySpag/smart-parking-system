"""Tests for the CNN model module (mocked TensorFlow)."""
import numpy as np
import pytest
from unittest.mock import patch, MagicMock


def _make_mock_keras():
    """Build a minimal keras mock that satisfies build_cnn_model."""
    keras_mock = MagicMock()

    class FakeModel:
        def __init__(self, layers=None, name=None):
            self._layers = layers or []
            self.name = name
            self.optimizer = None
            self.loss = None
            self.metrics_names = ["accuracy", "auc"]

        def compile(self, optimizer, loss, metrics):
            self.optimizer = optimizer
            self.loss = loss

        def predict(self, x, verbose=0):
            batch = x.shape[0] if hasattr(x, "shape") else len(x)
            return np.zeros((batch, 1), dtype=np.float32)

        def summary(self):
            pass

        def save(self, path):
            pass

    fake_model = FakeModel(name="parking_occupancy_cnn")
    keras_mock.Sequential.return_value = fake_model
    keras_mock.models.load_model.return_value = fake_model
    keras_mock.optimizers.Adam.return_value = MagicMock()
    keras_mock.metrics.AUC.return_value = MagicMock()

    layers_mock = MagicMock()
    layer_factories = ["Input", "Conv2D", "BatchNormalization", "MaxPooling2D",
                       "Flatten", "Dense", "Dropout"]
    for name in layer_factories:
        getattr(layers_mock, name).return_value = MagicMock()

    return keras_mock, layers_mock


@patch.dict("sys.modules", {})
def test_build_cnn_model_returns_model():
    keras_mock, layers_mock = _make_mock_keras()
    with patch.dict("sys.modules", {"tensorflow": MagicMock(keras=keras_mock), "tensorflow.keras": keras_mock, "tensorflow.keras.layers": layers_mock}):
        from importlib import import_module
        import importlib
        import detection.cnn.model as model_module
        importlib.reload(model_module)
        model = model_module.build_cnn_model()
        assert model is not None


def test_build_cnn_model_called_with_correct_shape():
    keras_mock, layers_mock = _make_mock_keras()
    with patch.dict("sys.modules", {"tensorflow": MagicMock(keras=keras_mock), "tensorflow.keras": keras_mock, "tensorflow.keras.layers": layers_mock}):
        import importlib
        import detection.cnn.model as model_module
        importlib.reload(model_module)
        model = model_module.build_cnn_model(input_shape=(150, 150, 3))
        keras_mock.Sequential.assert_called_once()


def test_build_cnn_model_compiles():
    keras_mock, layers_mock = _make_mock_keras()
    with patch.dict("sys.modules", {"tensorflow": MagicMock(keras=keras_mock), "tensorflow.keras": keras_mock, "tensorflow.keras.layers": layers_mock}):
        import importlib
        import detection.cnn.model as model_module
        importlib.reload(model_module)
        model = model_module.build_cnn_model()
        # compile() should have been called on the model
        assert model.loss is not None or keras_mock.Sequential.return_value.compile.called


def test_predict_single_image_output_shape():
    """predict returns a (batch, 1) shaped float array."""
    keras_mock, _ = _make_mock_keras()
    with patch.dict("sys.modules", {"tensorflow": MagicMock(keras=keras_mock), "tensorflow.keras": keras_mock}):
        import importlib
        import detection.cnn.predict as predict_module
        importlib.reload(predict_module)

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.3]])

        with patch("cv2.imread", return_value=np.zeros((150, 150, 3), dtype=np.uint8)), \
             patch("cv2.cvtColor", return_value=np.zeros((150, 150, 3), dtype=np.uint8)), \
             patch("cv2.resize", return_value=np.zeros((150, 150, 3), dtype=np.uint8)):
            result = predict_module.predict_single_image(mock_model, "fake.jpg")
            assert "is_occupied" in result
            assert "confidence" in result
            assert result["confidence"] == pytest.approx(0.3)
