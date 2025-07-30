"""MathUtils - Fast mathematical utilities."""

try:
    from .mathutils_backend import *
except ImportError as e:
    raise ImportError(f"Failed to import C++ backend: {e}")

# For now, commenting out until we add it to the package structure
# import src.python.jit_funs as jit_funs

__version__ = "0.1.0"
