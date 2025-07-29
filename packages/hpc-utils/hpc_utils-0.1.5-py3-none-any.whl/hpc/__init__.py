try:
    from importlib.metadata import PackageNotFoundError  # type: ignore
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError  # type: ignore
    from importlib_metadata import version


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

# documentation format
__author__ = "Mostafa Farrag"
__email__ = "moah.farag@gmail.com"
__docformat__ = "google"


__doc__ = """HPC - Numpy utility package for high-performance computing applications.

This package provides efficient functions for indexing and manipulating numpy arrays
without using loops, resulting in faster execution times.

Examples:
    ```python
    import numpy as np
    import hpc

    # Create a sample array
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    # Get indices of all non-zero values
    i, j = hpc.get_indices(arr, None)
    print(f"Row indices: {i}")
    print(f"Column indices: {j}")
    ```
"""
