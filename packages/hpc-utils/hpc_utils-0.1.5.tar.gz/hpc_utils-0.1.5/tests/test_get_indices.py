import numpy as np
from numpy.testing import assert_array_equal

from hpc.indexing import get_indices


class TestGetIndices:
    """Test class for the get_indices function.

    This class contains tests for the get_indices function, which returns the row and column
    indices of cells in a 2D array that match a specific value or all non-zero values.
    """

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

    def test_with_zero_mask_val(self):
        """Test get_indices with zero as the mask value.

        This test verifies that get_indices correctly returns the indices
        of cells that match zero when zero is explicitly provided as the mask value.

        Assertions:
            - The returned row indices match the expected values
            - The returned column indices match the expected values
        """
        # Create a test array
        arr = np.array([[0, 1, 0], [0, 0, 2], [3, 0, 0]])

        # Get indices of cells with value 0
        i, j = get_indices(arr, 0)

        # Assert that the indices are correct
        expected_i = np.array([0, 0, 1, 1, 2, 2])
        expected_j = np.array([0, 2, 0, 1, 1, 2])
        assert_array_equal(i, expected_i)
        assert_array_equal(j, expected_j)

    def test_with_negative_values(self):
        """Test get_indices with negative values in the array.

        This test verifies that get_indices correctly handles arrays with negative values
        and returns the correct indices.

        Assertions:
            - The returned row indices match the expected values
            - The returned column indices match the expected values
        """
        # Create a test array with negative values
        arr = np.array([[-1, 1, 0], [0, -2, 2], [3, 0, -3]])

        # Get indices of cells with value -2
        i, j = get_indices(arr, -2)

        # Assert that the indices are correct
        assert_array_equal(i, np.array([1]))
        assert_array_equal(j, np.array([1]))

        # Get indices of all non-zero cells
        i, j = get_indices(arr, None)

        # Assert that the indices are correct (all cells except [0,2], [1,0], and [2,1])
        expected_i = np.array([0, 0, 1, 1, 2, 2])
        expected_j = np.array([0, 1, 1, 2, 0, 2])
        assert_array_equal(sorted(i), sorted(expected_i))
        assert_array_equal(sorted(j), sorted(expected_j))
