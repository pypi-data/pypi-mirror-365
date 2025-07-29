import numpy as np
from numpy.testing import assert_array_equal

from hpc.indexing import get_pixels2


class TestGetPixels2:
    """Test class for the get_pixels2 function.

    This class contains tests for the get_pixels2 function, which extracts pixel values
    from an array based on indices that don't match the mask values. It works with both
    2D and 3D arrays and is particularly useful for filtering out specific values.
    """

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

    def test_with_empty_array(self):
        """Test get_pixels2 with an empty array.

        This test verifies that get_pixels2 correctly handles empty arrays
        by returning an empty array.

        Assertions:
            - The returned array is empty
        """
        # Create an empty array
        arr = np.array([[]])

        # Get pixels
        pixels = get_pixels2(arr, None)

        # Assert that the pixels array is empty
        assert len(pixels) == 0

    def test_with_nan_values(self):
        """Test get_pixels2 with NaN values in the array.

        This test verifies that get_pixels2 correctly handles arrays with NaN values
        and can filter them out.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array with NaN values
        arr = np.array([[1, 2, np.nan], [4, 5, 6]])

        # Get pixels not equal to NaN
        pixels = get_pixels2(arr, [np.nan])

        # Expected pixels (all values except NaN)
        expected = np.array([1, 2, 4, 5, 6])

        # Assert that the pixels are correct
        assert_array_equal(sorted(pixels), sorted(expected))

    def test_with_float_values(self):
        """Test get_pixels2 with floating-point values.

        This test verifies that get_pixels2 correctly handles floating-point values
        and uses approximate equality for comparison.

        Assertions:
            - The returned pixel values match the expected values
        """
        # Create a test array with floating-point values
        arr = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        # Get pixels not approximately equal to 0.5
        pixels = get_pixels2(arr, [0.5])

        # Expected pixels (all values except 0.5)
        expected = np.array([0.1, 0.2, 0.3, 0.4, 0.6])

        # Assert that the pixels are correct
        assert_array_equal(sorted(pixels), sorted(expected))

        # Test with a value that's close but not exactly equal
        pixels = get_pixels2(arr, [0.5001])

        # Expected pixels (all values except 0.5)
        expected = np.array([0.1, 0.2, 0.3, 0.4, 0.6])

        # Assert that the pixels are correct (0.5 is considered equal to 0.5001 with default tolerance)
        assert_array_equal(sorted(pixels), sorted(expected))
