"""MathUtils - Fast mathematical utilities."""

try:
    from .mathutils_backend import *
except ImportError as e:
    raise ImportError(f"Failed to import C++ backend: {e}")

# Import jit_funs module
from . import jit_funs

__version__ = "0.1.2"
