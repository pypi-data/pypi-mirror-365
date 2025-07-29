import numpy as np
from numpy.testing import assert_array_equal

from hpc.indexing import (
    get_indices,
    get_indices2,
    get_pixels,
    get_pixels2,
    locate_values,
)


class TestGetIndices:
    """Test class for the get_indices function."""

    def test_with_mask_val(self):
        """Test get_indices with a specific mask value.

        This test verifies that get_indices correctly returns the indices
        of cells that match a specific value in the array.

        Assertions:
            - The returned row indices match the expected values
            - The returned column indices match the expected values
        """
        # Create a test array
        arr = np.array([[0, 1, 0], [0, 0, 2], [3, 0, 0]])

        # Get indices of cells with value 2
        i, j = get_indices(arr, 2)

        # Assert that the indices are correct
        assert_array_equal(i, np.array([1]))
        assert_array_equal(j, np.array([2]))

    def test_without_mask_val(self):
        """Test get_indices without a mask value.

        This test verifies that get_indices correctly returns the indices
        of all non-zero cells in the array when mask_val is None.

        Assertions:
            - The returned row indices match the expected values
            - The returned column indices match the expected values
        """
        # Create a test array
        arr = np.array([[0, 1, 0], [0, 0, 2], [3, 0, 0]])

        # Get indices of all non-zero cells
        i, j = get_indices(arr, None)

        # Assert that the indices are correct
        assert_array_equal(i, np.array([0, 1, 2]))
        assert_array_equal(j, np.array([1, 2, 0]))

    def test_with_empty_array(self):
        """Test get_indices with an empty array.

        This test verifies that get_indices correctly handles empty arrays
        by returning empty index arrays.

        Assertions:
            - The returned row indices array is empty
            - The returned column indices array is empty
        """
        # Create an empty array
        arr = np.array([[0, 0, 0], [0, 0, 0]])

        # Get indices of cells with value 1 (none exist)
        i, j = get_indices(arr, 1)

        # Assert that the indices are empty
        assert_array_equal(i, np.array([]))
        assert_array_equal(j, np.array([]))

    def test_with_all_matching(self):
        """Test get_indices when all cells match the mask value.

        This test verifies that get_indices correctly returns indices for
        all cells when they all match the mask value.

        Assertions:
            - The returned row indices match the expected values
            - The returned column indices match the expected values
        """
        # Create an array with all cells having the same value
        arr = np.ones((2, 3))

        # Get indices of cells with value 1 (all cells)
        i, j = get_indices(arr, 1)

        # Assert that the indices include all cells
        assert_array_equal(i, np.array([0, 0, 0, 1, 1, 1]))
        assert_array_equal(j, np.array([0, 1, 2, 0, 1, 2]))


class TestGetPixels:
    """Test class for the get_pixels function."""

    def test_2d_with_mask(self):
        """Test get_pixels with a 2D array and a mask.

        This test verifies that get_pixels correctly extracts pixel values
        from a 2D array based on a mask.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array and mask
        arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        mask = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])

        # Get pixels based on the mask
        pixels = get_pixels(arr_2d, mask)

        # Assert that the pixels are correct
        assert_array_equal(pixels, np.array([2, 6]))

    def test_2d_with_mask_val(self):
        """Test get_pixels with a 2D array, mask, and specific mask value.

        This test verifies that get_pixels correctly extracts pixel values
        from a 2D array based on a mask with a specific mask value.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array and mask
        arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        mask = np.array([[0, 2, 0], [0, 0, 2], [0, 0, 0]])

        # Get pixels based on the mask with value 2
        pixels = get_pixels(arr_2d, mask, 2)

        # Assert that the pixels are correct
        assert_array_equal(pixels, np.array([2, 6]))

    def test_3d_with_mask(self):
        """Test get_pixels with a 3D array and a mask.

        This test verifies that get_pixels correctly extracts pixel values
        from a 3D array based on a mask.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test 3D array and mask
        arr_3d = np.array(
            [
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [[10, 20, 30], [40, 50, 60], [70, 80, 90]],
            ]
        )
        mask = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])

        # Get pixels based on the mask
        pixels = get_pixels(arr_3d, mask)

        # Assert that the pixels are correct
        assert_array_equal(pixels, np.array([[2, 6], [20, 60]]))

    def test_without_mask(self):
        """Test get_pixels without a mask.

        This test verifies that get_pixels correctly returns the original array
        when no mask is provided.

        Assertions:
            - The returned array is the same as the input array
        """
        # Create a test array
        arr = np.array([[1, 2, 3], [4, 5, 6]])

        # Get pixels without a mask
        pixels = get_pixels(arr, None)

        # Assert that the pixels are the same as the input array
        assert_array_equal(pixels, arr)

    def test_with_empty_mask_result(self):
        """Test get_pixels when the mask results in no pixels.

        This test verifies that get_pixels correctly handles cases where
        the mask doesn't match any pixels in the array.

        Assertions:
            - The returned array is empty
        """
        # Create a test array and mask
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        mask = np.zeros_like(arr)

        # Get pixels based on the mask with value 1 (none exist in mask)
        pixels = get_pixels(arr, mask, 1)

        # Assert that the pixels array is empty
        assert len(pixels) == 0


class TestGetIndices2:
    """Test class for the get_indices2 function."""

    def test_with_single_mask_value(self):
        """Test get_indices2 with a single mask value.

        This test verifies that get_indices2 correctly returns the indices
        of cells that don't match the mask value.

        Assertions:
            - The returned indices match the expected values
        """
        # Create a test array
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Get indices of cells not equal to 5
        indices = get_indices2(arr, [5])

        # Expected indices (all cells except the one with value 5)
        expected = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]

        # Assert that the indices are correct
        assert sorted(indices) == sorted(expected)

    def test_with_two_mask_values(self):
        """Test get_indices2 with two mask values.

        This test verifies that get_indices2 correctly returns the indices
        of cells that don't match either of the mask values.

        Assertions:
            - The returned indices match the expected values
        """
        # Create a test array
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Get indices of cells not equal to 1 or 9
        indices = get_indices2(arr, [1, 9])

        # Expected indices (all cells except those with values 1 or 9)
        expected = [(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)]

        # Assert that the indices are correct
        assert sorted(indices) == sorted(expected)

    def test_with_nan_value(self):
        """Test get_indices2 with NaN values in the mask.

        This test verifies that get_indices2 correctly handles NaN values
        in the mask and returns indices of cells that are not NaN.

        Assertions:
            - The returned indices match the expected values
        """
        # Create a test array with NaN
        arr = np.array([[1, 2, np.nan], [4, 5, 6]])

        # Get indices of cells that are not NaN
        indices = get_indices2(arr, [np.nan])

        # Expected indices (all cells except the NaN)
        expected = [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)]

        # Assert that the indices are correct
        assert sorted(indices) == sorted(expected)

    def test_without_mask(self):
        """Test get_indices2 without a mask.

        This test verifies that get_indices2 correctly returns indices of all cells
        when no mask is provided.

        Assertions:
            - The returned indices match the expected values
        """
        # Create a test array
        arr = np.array([[1, 2], [3, 4]])

        # Get indices of all cells
        indices = get_indices2(arr, None)

        # Expected indices (all cells)
        expected = [(0, 0), (0, 1), (1, 0), (1, 1)]

        # Assert that the indices are correct
        assert sorted(indices) == sorted(expected)


class TestGetPixels2:
    """Test class for the get_pixels2 function."""

    def test_2d_without_mask(self):
        """Test get_pixels2 with a 2D array and no mask.

        This test verifies that get_pixels2 correctly returns all pixel values
        from a 2D array when no mask is provided.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array
        arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Get all pixels
        pixels = get_pixels2(arr_2d, None)

        # Assert that the pixels are correct
        assert_array_equal(pixels, arr_2d.flatten())

    def test_2d_with_single_mask_value(self):
        """Test get_pixels2 with a 2D array and a single mask value.

        This test verifies that get_pixels2 correctly returns pixel values
        from a 2D array that don't match the mask value.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array
        arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Get pixels not equal to 5
        pixels = get_pixels2(arr_2d, [5])

        # Expected pixels (all values except 5)
        expected = np.array([1, 2, 3, 4, 6, 7, 8, 9])

        # Assert that the pixels are correct
        assert_array_equal(sorted(pixels), sorted(expected))

    def test_2d_with_two_mask_values(self):
        """Test get_pixels2 with a 2D array and two mask values.

        This test verifies that get_pixels2 correctly returns pixel values
        from a 2D array that don't match either of the mask values.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array
        arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Get pixels not equal to 1 or 9
        pixels = get_pixels2(arr_2d, [1, 9])

        # Expected pixels (all values except 1 and 9)
        expected = np.array([2, 3, 4, 5, 6, 7, 8])

        # Assert that the pixels are correct
        assert_array_equal(sorted(pixels), sorted(expected))

    def test_3d_without_mask(self):
        """Test get_pixels2 with a 3D array and no mask.

        This test verifies that get_pixels2 correctly returns all pixel values
        from a 3D array when no mask is provided.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test 3D array
        arr_3d = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

        # Get all pixels
        pixels = get_pixels2(arr_3d, None)

        # Expected shape and values
        expected_shape = (2, 4)  # 2 bands, 4 pixels
        expected_values = np.array(
            [[1, 2, 3, 4], [5, 6, 7, 8]]  # First band  # Second band
        )

        # Assert that the pixels have the correct shape and values
        assert pixels.shape == expected_shape
        assert_array_equal(pixels, expected_values)

    def test_3d_with_mask(self):
        """Test get_pixels2 with a 3D array and a mask.

        This test verifies that get_pixels2 correctly returns pixel values
        from a 3D array that don't match the mask values.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test 3D array
        arr_3d = np.array([[[1, 2, 3], [4, 5, 6]], [[10, 20, 30], [40, 50, 60]]])

        # Get pixels not equal to 5 and 50
        pixels = get_pixels2(arr_3d, [5, 50])

        # Expected shape and values
        expected_shape = (
            2,
            5,
        )  # 2 bands, 5 pixels (excluding the ones with values 5 and 50)

        # Assert that the pixels have the correct shape
        assert pixels.shape == expected_shape

        # Check that the first band contains the expected values (excluding 5)
        assert set(pixels[0]) == {1, 2, 3, 4, 6}

        # Check that the second band contains the expected values (excluding 50)
        assert set(pixels[1]) == {10, 20, 30, 40, 60}


class TestLocateValues:
    """Test class for the locate_values function."""

    def test_basic_functionality(self):
        """Test the basic functionality of locate_values.

        This test verifies that locate_values correctly finds the closest grid points
        to a set of coordinates.

        Assertions:
            - The returned indices match the expected values
        """
        # Create grid coordinates
        grid_x = np.array([0, 10, 20, 30, 40, 50])
        grid_y = np.array([0, 20, 40, 60, 80])

        # Create coordinates to locate
        coords = np.array([[10, 20], [30, 40], [50, 60]])

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Expected indices
        expected = np.array(
            [
                [1, 1],  # [10, 20] maps to grid_x[1]=10, grid_y[1]=20
                [3, 2],  # [30, 40] maps to grid_x[3]=30, grid_y[2]=40
                [5, 3],  # [50, 60] maps to grid_x[5]=50, grid_y[3]=60
            ]
        )

        # Assert that the indices are correct
        assert_array_equal(indices, expected)

    def test_with_non_exact_matches(self):
        """Test locate_values with coordinates that don't exactly match grid points.

        This test verifies that locate_values correctly finds the closest grid points
        to coordinates that don't exactly match any grid point.

        Assertions:
            - The returned indices match the expected values
        """
        # Create grid coordinates
        grid_x = np.array([0, 10, 20, 30, 40, 50])
        grid_y = np.array([0, 20, 40, 60, 80])

        # Create coordinates to locate (slightly off from grid points)
        coords = np.array([[12, 22], [28, 38], [52, 62]])

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Expected indices
        expected = np.array(
            [
                [1, 1],  # [12, 22] is closest to grid_x[1]=10, grid_y[1]=20
                [3, 2],  # [28, 38] is closest to grid_x[3]=30, grid_y[2]=40
                [5, 3],  # [52, 62] is closest to grid_x[5]=50, grid_y[3]=60
            ]
        )

        # Assert that the indices are correct
        assert_array_equal(indices, expected)

    def test_with_single_coordinate(self):
        """Test locate_values with a single coordinate.

        This test verifies that locate_values correctly handles a single coordinate
        (as a 2D array with one row).

        Assertions:
            - The returned indices match the expected values
        """
        # Create grid coordinates
        grid_x = np.array([0, 10, 20, 30, 40, 50])
        grid_y = np.array([0, 20, 40, 60, 80])

        # Create a single coordinate to locate
        coords = np.array([[25, 45]])

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Expected indices
        expected = np.array(
            [[2, 2]]
        )  # [25, 45] is closest to grid_x[2]=20, grid_y[2]=40

        # Assert that the indices are correct
        assert_array_equal(indices, expected)

    def test_with_coordinates_outside_grid(self):
        """Test locate_values with coordinates outside the grid.

        This test verifies that locate_values correctly finds the closest grid points
        to coordinates that are outside the grid range.

        Assertions:
            - The returned indices match the expected values
        """
        # Create grid coordinates
        grid_x = np.array([0, 10, 20, 30, 40, 50])
        grid_y = np.array([0, 20, 40, 60, 80])

        # Create coordinates outside the grid
        coords = np.array([[-10, -5], [60, 90], [100, 100]])

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Expected indices
        expected = np.array(
            [
                [0, 0],  # [-10, -5] is closest to grid_x[0]=0, grid_y[0]=0
                [5, 4],  # [60, 90] is closest to grid_x[5]=50, grid_y[4]=80
                [5, 4],  # [100, 100] is closest to grid_x[5]=50, grid_y[4]=80
            ]
        )

        # Assert that the indices are correct
        assert_array_equal(indices, expected)
