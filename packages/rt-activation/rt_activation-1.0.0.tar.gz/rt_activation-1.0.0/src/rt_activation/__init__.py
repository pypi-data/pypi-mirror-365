"""RT Activation: Rectified Tanh Activation function for Keras."""

from .activation_functions import RTA, rta, register_rta_activation

__version__ = "0.1.0"
__author__ = "Gaurav Pandey"
__email__ = "gauravpandey@gmail.com"

# Ensure activation is registered when package is imported
register_rta_activation()

# Make the activation function available at package level
__all__ = ["RTA", "rta", "register_rta_activation"]
