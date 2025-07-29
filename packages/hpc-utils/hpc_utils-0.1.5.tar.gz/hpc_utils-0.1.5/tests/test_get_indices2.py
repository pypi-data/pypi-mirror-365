import numpy as np
from numpy.testing import assert_array_equal

from hpc.indexing import get_indices2


class TestGetIndices2:
    """Test class for the get_indices2 function.

    This class contains tests for the get_indices2 function, which returns the indices
    of array cells that don't match the values in the mask. If mask is None, returns
    indices of all cells in the array.
    """

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

    def test_with_empty_array(self):
        """Test get_indices2 with an empty array.

        This test verifies that get_indices2 correctly handles empty arrays
        by returning an empty list of indices.

        Assertions:
            - The returned list of indices is empty
        """
        # Create an empty array
        arr = np.array([[]])

        # Get indices
        indices = get_indices2(arr, None)

        # Assert that the indices list is empty
        assert indices == []

    def test_with_all_masked_values(self):
        """Test get_indices2 when all values match the mask.

        This test verifies that get_indices2 correctly returns an empty list
        when all values in the array match the mask value.

        Assertions:
            - The returned list of indices is empty
        """
        # Create an array with all the same value
        arr = np.ones((2, 2))

        # Get indices of cells not equal to 1 (none exist)
        indices = get_indices2(arr, [1])

        # Assert that the indices list is empty
        assert indices == []

    def test_with_float_values(self):
        """Test get_indices2 with floating-point values.

        This test verifies that get_indices2 correctly handles floating-point values
        and uses approximate equality for comparison.

        Assertions:
            - The returned indices match the expected values
        """
        # Create a test array with floating-point values
        arr = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        # Get indices of cells not approximately equal to 0.5
        indices = get_indices2(arr, [0.5])

        # Expected indices (all cells except the one with value 0.5)
        expected = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)]

        # Assert that the indices are correct
        assert sorted(indices) == sorted(expected)

        # Test with a value that's close but not exactly equal
        indices = get_indices2(arr, [0.5001])

        # Expected indices (all cells except the one with value 0.5)
        expected = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)]

        # Assert that the indices are correct (0.5 is considered equal to 0.5001 with default tolerance)
        assert sorted(indices) == sorted(expected)
