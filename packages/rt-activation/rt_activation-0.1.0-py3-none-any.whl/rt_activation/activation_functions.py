import keras
from keras.utils import get_custom_objects

@keras.utils.register_keras_serializable(package="rt_activation")
def RTA(x):
    """
    Rectified Tanh Activation (RTA) function.

    Formula: f(x) = max(x, tanh(x))
    
    This activation function combines the benefits of ReLU and Tanh:
    - For positive values where tanh(x) < x, it behaves like ReLU (returns x)
    - For negative values and positive values where tanh(x) >= x, it behaves like tanh
    - Provides smooth gradients while maintaining linear growth for large positive values

    Args:
        x: Input tensor.

    Returns:
        The output of the RTA activation function.
    """
    return keras.ops.maximum(x, keras.ops.tanh(x))

@keras.utils.register_keras_serializable(package="rt_activation")  
def rta(x):
    """Alias for RTA activation function (lowercase for consistency with other activations)."""
    return RTA(x)

# Register the activation functions so they can be used by string name
def register_rta_activation():
    """Register RTA activation function with Keras."""
    # Method 1: Register in custom objects
    custom_objects = get_custom_objects()
    custom_objects['RTA'] = RTA
    custom_objects['rta'] = rta
    custom_objects['rectified_tanh'] = RTA
    
    # Method 2: Direct registration in keras.activations module
    import keras.activations
    keras.activations.RTA = RTA
    keras.activations.rta = rta
    keras.activations.rectified_tanh = RTA
    
    # Method 3: Monkey patch the REAL get function in keras.src.activations
    import keras.src.activations
    original_get = keras.src.activations.get
    
    def custom_get(identifier):
        if isinstance(identifier, str):
            if identifier == 'RTA':
                return RTA
            elif identifier == 'rta':
                return rta
            elif identifier == 'rectified_tanh':
                return RTA
        return original_get(identifier)
    
    keras.src.activations.get = custom_get
    # Also patch the top-level one just in case
    keras.activations.get = custom_get

# Automatically register when module is imported
register_rta_activation()
