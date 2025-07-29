import numpy as np
import pytest
from numpy.testing import assert_array_equal

from hpc.indexing import get_pixels


class TestGetPixels:
    """Test class for the get_pixels function.

    This class contains tests for the get_pixels function, which extracts pixel values
    from an array based on a mask. It can work with both 2D and 3D arrays and can
    extract pixels based on specific mask values.
    """

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

    def test_3d_with_mask_val(self):
        """Test get_pixels with a 3D array, mask, and specific mask value.

        This test verifies that get_pixels correctly extracts pixel values
        from a 3D array based on a mask with a specific mask value.

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
        mask = np.array([[0, 2, 0], [0, 0, 2], [0, 0, 0]])

        # Get pixels based on the mask with value 2
        pixels = get_pixels(arr_3d, mask, 2)

        # Assert that the pixels are correct
        assert_array_equal(pixels, np.array([[2, 6], [20, 60]]))

    def test_with_mismatched_dimensions(self):
        """Test get_pixels with mismatched dimensions between array and mask.

        This test verifies that get_pixels correctly raises a ValueError when
        the dimensions of the array and mask don't match.

        Assertions:
            - A ValueError is raised
        """
        # Create a test array and mask with mismatched dimensions
        arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
        mask = np.array([[0, 1], [0, 0], [0, 0]])

        # Assert that a ValueError is raised
        with pytest.raises(ValueError):
            get_pixels(arr_2d, mask)
