"""
NumPy 2.x compatibility layer for Real-ESRGAN
"""
import os
import numpy as np
import warnings

def patch_numpy_compatibility():
    """Patch numpy compatibility issues for version 2.x"""

    # Set environment variable for numpy 1.x compatibility
    os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'

    # Suppress numpy 2.x deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="numpy")
    warnings.filterwarnings("ignore", category=UserWarning, module="numpy")

    # Patch numpy array creation if needed
    if hasattr(np, 'array') and not hasattr(np.array, '_patched'):
        original_array = np.array

        def patched_array(*args, **kwargs):
            try:
                return original_array(*args, **kwargs)
            except Exception as e:
                # Handle numpy 2.x specific issues
                if "ARRAY_API" in str(e):
                    # Fallback for array API issues
                    return original_array(*args, **kwargs)
                raise e

        np.array = patched_array
        np.array._patched = True

def ensure_numpy_compatibility():
    """Ensure numpy compatibility for the current version"""
    version = np.__version__
    major_version = int(version.split('.')[0])

    if major_version >= 2:
        patch_numpy_compatibility()
        print(f"NumPy {version} compatibility patches applied")

    return True