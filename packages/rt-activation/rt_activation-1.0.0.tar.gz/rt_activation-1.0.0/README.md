# RT Activation
A custom activation function for Keras/TensorFlow implementing Rectified Tangent Activation (RTA).

## Formula
f(x) = max(x, tanh(x))

## Installation
```bash
pip install rt-activation
```
## Usage

### Simple Usage (String-based)
```python
import keras
from keras import layers
import rt_activation  # This registers the activation function

model = keras.Sequential([
    keras.Input(shape=input_shape),
    layers.Conv2D(32, kernel_size=(3, 3), activation="RTA"),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Conv2D(64, kernel_size=(3, 3), activation="RTA"),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Flatten(),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation="softmax"),
])
```

### Function-based Usage
```python
import keras
from keras import layers
from rt_activation import RTA

model = keras.Sequential([
    keras.Input(shape=input_shape),
    layers.Conv2D(32, kernel_size=(3, 3), activation=RTA),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Conv2D(64, kernel_size=(3, 3), activation=RTA),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Flatten(),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation="softmax"),
])
```

## Properties
- **Smooth**: Differentiable everywhere
- **Non-saturating**: Linear growth for large positive values
- **Bounded for negatives**: tanh behavior for negative inputs
- **Zero-centered**: Output can be negative

## License
MIT License
