import numpy as np
from numpy.testing import assert_array_equal

from hpc.indexing import locate_values


class TestLocateValues:
    """Test class for the locate_values function.

    This class contains tests for the locate_values function, which takes a set of (x,y)
    coordinates and finds the closest matching indices in the provided grid_x and grid_y arrays.
    It's particularly useful for mapping point data to grid cells in spatial analysis.
    """

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

    def test_with_empty_coordinates(self):
        """Test locate_values with an empty coordinates array.

        This test verifies that locate_values correctly handles an empty coordinates array
        by returning an empty indices array.

        Assertions:
            - The returned indices array is empty
        """
        # Create grid coordinates
        grid_x = np.array([0, 10, 20, 30, 40, 50])
        grid_y = np.array([0, 20, 40, 60, 80])

        # Create an empty coordinates array
        coords = np.array([]).reshape(0, 2)

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Assert that the indices array is empty
        assert indices.shape == (0, 2)

    def test_with_negative_grid_values(self):
        """Test locate_values with negative grid values.

        This test verifies that locate_values correctly handles grid coordinates
        that include negative values.

        Assertions:
            - The returned indices match the expected values
        """
        # Create grid coordinates with negative values
        grid_x = np.array([-50, -30, -10, 0, 10, 30, 50])
        grid_y = np.array([-40, -20, 0, 20, 40])

        # Create coordinates to locate
        coords = np.array([[-40, -30], [-5, 5], [20, 30]])

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Expected indices
        expected = np.array(
            [
                [0, 0],  # [-40, -30] is closest to grid_x[0]=-50, grid_y[0]=-40
                [2, 2],  # [-5, 5] is closest to grid_x[2]=-10, grid_y[2]=0
                [4, 3],  # [20, 30] is closest to grid_x[4]=10, grid_y[3]=20
            ]
        )

        # Assert that the indices are correct
        assert_array_equal(indices, expected)

    def test_with_non_uniform_grid(self):
        """Test locate_values with a non-uniform grid.

        This test verifies that locate_values correctly handles grid coordinates
        that are not uniformly spaced.

        Assertions:
            - The returned indices match the expected values
        """
        # Create non-uniform grid coordinates
        grid_x = np.array([0, 5, 15, 30, 50, 100])
        grid_y = np.array([0, 10, 30, 70, 150])

        # Create coordinates to locate
        coords = np.array([[10, 20], [40, 50], [75, 100]])

        # Find the closest grid indices
        indices = locate_values(coords, grid_x, grid_y)

        # Expected indices
        expected = np.array(
            [
                [1, 1],  # [10, 20] is closest to grid_x[1]=5, grid_y[1]=10
                [3, 2],  # [40, 50] is closest to grid_x[3]=30, grid_y[2]=30
                [4, 3],  # [75, 100] is closest to grid_x[4]=50, grid_y[3]=70
            ]
        )

        # Assert that the indices are correct
        assert_array_equal(indices, expected)
