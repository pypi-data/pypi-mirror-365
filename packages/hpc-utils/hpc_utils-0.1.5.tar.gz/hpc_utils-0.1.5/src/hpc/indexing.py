from typing import List, Optional, Tuple, Union

import numpy as np


def get_indices(
    arr: np.ndarray, mask_val: Union[int, float]
) -> Tuple[np.ndarray, np.ndarray]:
    """Get the array indices for the non-zero cells.

    This function returns the row and column indices of cells in a 2D array that match
    a specific value or all non-zero values.

    Args:
        arr: 2D array with values you need to get the indexes of the cells that are filled with these values.
        mask_val: If you need to locate only a certain value, and not all values in the array.
            If None or falsy, will return indices of all non-zero values.

    Returns:
        A tuple of two numpy arrays:
            - first array is the row indices
            - second array is the column indices

    Raises:
        ValueError: If the input array is not 2D.

    Examples:
        - Import numpy
        ```python
        >>> import numpy as np

        ```
        - Create a sample array
        ```python
        >>> arr = np.array([[0, 1, 0], [0, 0, 2], [3, 0, 0]])

        ```
        - Get indices of all non-zero values
        ```python
        >>> i, j = get_indices(arr, None)
        >>> print(i)
        [0 1 2]
        >>> print(j)
        [1 2 0]

        ```
        - Get indices of a specific value
        ```python
        >>> i, j = get_indices(arr, 2)
        >>> print(i)
        [1]
        >>> print(j)
        [2]

        ```
    """
    # Use the arr to get the indices of the non-zero pixels.
    if mask_val is not None:
        (i, j) = (arr == mask_val).nonzero()
    else:
        (i, j) = arr.nonzero()

    return i, j


def get_pixels(
    arr: np.ndarray, mask: np.ndarray = None, mask_val: Union[int, float, None] = None
) -> np.ndarray:
    """Get pixels from a raster (with optional mask).

    This function extracts pixel values from an array based on a mask. It can work with
    both 2D and 3D arrays and can extract pixels based on specific mask values.

    Args:
        arr: Array of raster data in the form [bands][y][x] or [y][x].
        mask: Array (2D) of values to mask data (from rasterizing a vector).
            If None, returns the original array.
        mask_val: Value of the data pixels in the mask to extract.
            If None or falsy, will extract all non-zero values.

    Returns:
        np.ndarray: Array of non-masked data.
            - For 2D input: 1D array of values
            - For 3D input: 2D array with bands as rows and filtered pixels as columns

    Raises:
        ValueError: If the mask dimensions don't match the array dimensions.

    Examples:
        - Import numpy
        ```python
        >>> import numpy as np

        ```
        - 2D array example
        ```python
        >>> arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> mask = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
        >>> get_pixels(arr_2d, mask)
        array([2, 6])

        ```
        - 3D array example
        ```python
        >>> arr_3d = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        ...                    [[10, 20, 30], [40, 50, 60], [70, 80, 90]]])
        >>> get_pixels(arr_3d, mask)
        array([[ 2,  6],
               [20, 60]])

        ```
        - With specific mask value
        ```python
        >>> mask2 = np.array([[0, 2, 0], [0, 0, 2], [0, 0, 0]])
        >>> get_pixels(arr_2d, mask2, 2)
        array([2, 6])

        ```
    """
    if mask is None:
        return arr

    # Validate that mask dimensions match array dimensions
    if arr.ndim == 2:
        if mask.shape != arr.shape:
            raise ValueError(
                f"Mask shape {mask.shape} does not match array shape {arr.shape}"
            )
    elif arr.ndim == 3:
        if mask.shape != arr.shape[1:]:
            raise ValueError(
                f"Mask shape {mask.shape} does not match array shape {arr.shape[1:]}"
            )
    else:
        raise ValueError(f"Unsupported array dimensions: {arr.ndim}")

    i, j = get_indices(mask, mask_val)
    # get the corresponding values to the indices from the array
    vals = arr[i, j] if arr.ndim == 2 else arr[:, i, j]
    return vals


def get_indices2(
    arr: np.ndarray, mask: Optional[List[Union[int, float, np.number]]] = None
) -> List[Tuple[int, int]]:
    """Get indices of array cells after filtering values based on mask values.

    This function returns the indices of array cells that don't match the values in the mask.
    If mask is None, returns indices of all cells in the array. This function is particularly
    useful for filtering out specific values (like NoData values) from an array.

    Args:
        arr: 2D numpy array to get indices from.
        mask: List of values to exclude from the result.
            - If None, returns indices of all cells.
            - If list with one value, returns indices of cells not equal to that value.
            - If list with two values, returns indices of cells not equal to either value.

    Returns:
        List of tuples (row, col) representing the indices of cells that pass the filter.

    Raises:
        ValueError: If mask contains more than two values.
        ValueError: If the input array is not 2D.

    Examples:
        - Import numpy
        ```python
        >>> import numpy as np

        ```
        - Create a sample array
        ```python
        >>> arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        ```
        - Get all indices
        ```python
        >>> indices = get_indices2(arr, None)
        >>> len(indices)  # 3x3 array = 9 indices
        9

        ```
        - Filter out cells with value 5
        ```python
        >>> indices = get_indices2(arr, [5])
        >>> sorted(indices) #doctest: +SKIP
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]

        ```
        - Filter out cells with values 1 and 9
        ```python
        >>> indices = get_indices2(arr, [1, 9])
        >>> sorted(indices)     #doctest: +SKIP
        [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)]

        ```
        - Works with NaN values
        ```python
        >>> arr_with_nan = np.array([[1, 2, np.nan], [4, 5, 6]])
        >>> indices = get_indices2(arr_with_nan, [np.nan])
        >>> sorted(indices) #doctest: +SKIP
        [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]

        ```
    """
    # get the position of cells that is not zeros
    if mask is not None:
        if len(mask) > 1:
            mask = np.logical_and(
                ~np.isclose(arr, mask[0], rtol=0.001),
                ~np.isclose(arr, mask[1], rtol=0.001),
            )
        else:
            if np.isnan(mask[0]):
                mask = ~np.isnan(arr)
            else:
                mask = ~np.isclose(arr, mask[0], rtol=0.001)

        rows = np.nonzero(mask)[0]
        cols = np.nonzero(mask)[1]

        ind = list(zip(rows, cols))
    else:
        rows = arr.shape[0]
        cols = arr.shape[1]
        ind = [(i, j) for i in range(rows) for j in range(cols)]

    return ind


def get_pixels2(
    arr: np.ndarray, mask: Optional[List[Union[int, float, np.number]]] = None
) -> np.ndarray:
    """Get pixels from a raster using the get_indices2 function for filtering.

    This function extracts pixel values from an array based on indices that don't match the mask values.
    It works with both 2D and 3D arrays and is particularly useful for filtering out specific values
    (like NoData values) from an array.

    Args:
        arr: Array of raster data in the form [y][x] for 2D arrays or [bands][y][x] for 3D arrays.
        mask: List of values to exclude from the result.
            - If None, returns all pixels.
            - If list with values, returns pixels not matching those values.
            See get_indices2 for more details on mask behavior.

    Returns:
        np.ndarray: Array of filtered pixel values.
            - For 2D input: 1D array of values
            - For 3D input: 2D array with bands as rows and filtered pixels as columns

    Raises:
        ValueError: If mask contains more than two values.
        ValueError: If the input array dimensions are not supported (must be 2D or 3D).

    Examples:
        - Import numpy
        ```python
        >>> import numpy as np

        ```
        - 2D array example
        ```python
        >>> arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        ```
        - Get all pixels
        ```python
        >>> pixels = get_pixels2(arr_2d, None)
        >>> len(pixels)
        9

        ```
        - Filter out pixels with value 5
        ```python
        >>> pixels = get_pixels2(arr_2d, [5])
        >>> sorted(pixels) #doctest: +SKIP
        [1, 2, 3, 4, 6, 7, 8, 9]

        ```
        - 3D array example
        ```python
        >>> arr_3d = np.array(
        ...     [
        ...         [[1, 2, 3], [4, 5, 6]],
        ...         [[10, 20, 30], [40, 50, 60]]
        ...     ]
        ... )

        ```
        - Filter out pixels with value 5 and 50
        ```python
        >>> pixels = get_pixels2(arr_3d, [5, 50])
        >>> pixels.shape
        (2, 5)
        >>> pixels[0]  # First band values #doctest: +SKIP
        array([1, 2, 3, 4, 6])
        >>> pixels[1]  # Second band values #doctest: +SKIP
        array([10, 20, 30, 40, 60])

        ```
    """
    if arr.ndim == 2:
        ind = get_indices2(arr, mask)
        fn = lambda x: arr[x[0], x[1]]
        values = np.fromiter(map(fn, ind), dtype=arr.dtype)
    else:
        ind = get_indices2(arr[0, :, :], mask)
        fn = lambda x: arr[:, x[0], x[1]]
        values = list(map(fn, ind))
        values = np.array(values, dtype=arr.dtype)
        values = values.transpose()

    return values


def locate_values(
    values: np.ndarray, grid_x: np.ndarray, grid_y: np.ndarray
) -> np.ndarray:
    """Locate coordinates in a grid by finding the closest grid points.

    This function takes a set of (x,y) coordinates and finds the closest matching indices
    in the provided grid_x and grid_y arrays. It's particularly useful for mapping point
    data to grid cells in spatial analysis and interpolation tasks.

    Args:
        values: Array with shape (n, 2), where each row contains [x, y] coordinates to locate.
            Example:
            ```
            array([[454795, 503143],
                   [443847, 481850],
                   [454044, 481189]])
            ```
        grid_x: Array of x-coordinates (west to east) to search within.
            These are typically the x-coordinates of a grid.
        grid_y: Array of y-coordinates (north to south) to search within.
            These are typically the y-coordinates of a grid.

    Returns:
        np.ndarray: Array with shape (n, 2) containing the [row, col] indices of the
            closest grid points to each input coordinate.
            Example:
            ```
            array([[ 5,  4],
                   [ 2,  9],
                   [ 5,  9]])
            ```

    Raises:
        ValueError: If values array doesn't have shape (n, 2).
        ValueError: If grid_x or grid_y are empty arrays.

    Examples:
        - Import numpy
        ```python
        >>> import numpy as np

        ```
        - Create sample coordinates to locate
        ```python
        >>> coords = np.array([[10, 20], [30, 40], [50, 60]])

        ```
        - Create grid coordinates
        ```python
        >>> grid_x = np.array([0, 10, 20, 30, 40, 50])
        >>> grid_y = np.array([0, 20, 40, 60, 80])

        ```
        - Find the closest grid indices
        ```python
        >>> indices = locate_values(coords, grid_x, grid_y)
        >>> print(indices)
        [[1 1]
         [3 2]
         [5 3]]

        ```
        - Verify the first coordinate [10, 20] maps to grid_x[1]=10, grid_y[1]=20
        ```python
        >>> grid_x[indices[0, 0]], grid_y[indices[0, 1]]
        (np.int64(10), np.int64(20))

        ```
        - Verify the second coordinate [30, 40] maps to grid_x[3]=30, grid_y[2]=40
        ```python
        >>> grid_x[indices[1, 0]], grid_y[indices[1, 1]]
        (np.int64(30), np.int64(40))

        ```
        - Verify the third coordinate [50, 60] maps to grid_x[5]=50, grid_y[3]=60
        ```python
        >>> grid_x[indices[2, 0]], grid_y[indices[2, 1]]
        (np.int64(50), np.int64(60))

        ```
    """
    # Validate inputs
    if len(grid_x) == 0:
        raise ValueError("grid_x cannot be empty")
    if len(grid_y) == 0:
        raise ValueError("grid_y cannot be empty")

    # Handle empty values array
    if len(values) == 0:
        return np.zeros((0, 2), dtype=int)

    # Validate values shape
    if values.ndim != 2 or values.shape[1] != 2:
        raise ValueError(f"values must have shape (n, 2), got {values.shape}")

    def find(point_i):
        x_ind = np.abs(point_i[0] - grid_x).argmin()
        y_ind = np.abs(point_i[1] - grid_y).argmin()
        return x_ind, y_ind

    indices = np.array(list(map(find, values)))

    return indices
