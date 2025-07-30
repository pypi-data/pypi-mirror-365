import unittest
import numpy as np
from math import pi
from scipy import stats
from dsef.dsef_tools import get_t_critical, calc_dof, calc_heading_vector, calc_heading, heading2rotM, epanechnikov1D, gen_epanechnikov2D_kernel, FlutDir, DsefFilters

class TestDsefTools(unittest.TestCase):

    def test_get_t_critical(self):
        self.assertAlmostEqual(get_t_critical(10, 0.001), stats.t.ppf(0.999, 10))
        self.assertAlmostEqual(get_t_critical(5, 0.05), stats.t.ppf(0.95, 5))

    def test_get_t_critical_invalid_input_type(self):        
        with self.assertRaises(ValueError):
            get_t_critical(11.23, 0.001)

    def test_calc_dof(self):
        self.assertEqual(calc_dof(1.0, 1.0, 10), 18)
        self.assertEqual(calc_dof(2.0, 3.0, 10), 17)

    def test_calc_heading_vector_north(self):         
        result = calc_heading_vector(0)
        expected = np.array([0, 1])
        np.testing.assert_almost_equal(result, expected)
    
    def test_calc_heading_vector_east(self) -> None:
        result = calc_heading_vector(90)
        expected = np.array([1, 0])
        np.testing.assert_almost_equal(result, expected)

    def test_calc_heading_vector_south(self): 
        result = calc_heading_vector(180)
        expected = np.array([0, -1])
        np.testing.assert_almost_equal(result, expected)

    def test_calc_heading_vector_west(self): 
        result = calc_heading_vector(270)
        expected = np.array([-1, 0])
        np.testing.assert_almost_equal(result, expected)

    def test_calc_heading_vector_negative_angle(self): 
        result = calc_heading_vector(-90)
        expected = np.array([-1, 0])
        np.testing.assert_almost_equal(result, expected)
        result = calc_heading_vector(-180)
        expected = np.array([0, -1])
        np.testing.assert_almost_equal(result, expected)

    def test_calc_heading_vector_invalid(self):
        with self.assertRaises(TypeError):
            calc_heading_vector("90")

    def test_calc_heading(self):
        result = calc_heading([1, 0])
        self.assertEqual(result, 90)

    def test_heading2rotM(self):
        result = heading2rotM(90)
        np.testing.assert_almost_equal(result, [[0, 1], [-1, 0]])

    def test_epanechnikov1D_scalar(self):
        self.assertAlmostEqual(epanechnikov1D(0), 0.75)
        self.assertAlmostEqual(epanechnikov1D(1), 0.0)
        self.assertAlmostEqual(epanechnikov1D(-1), 0.0)
        self.assertAlmostEqual(epanechnikov1D(0.5), 0.75 * (1 - 0.25))

    def test_epanechnikov1D_array(self):
        u = np.array([-1, -0.5, 0, 0.5, 1])
        expected = 0.75 * (1 - u**2) * (np.abs(u) <= 1)
        np.testing.assert_array_almost_equal(epanechnikov1D(u), expected)

    def test_gen_epanechnikov2D_kernel_shape(self):
        radius = 3
        kernel = gen_epanechnikov2D_kernel(radius)
        self.assertEqual(kernel.shape, (2 * radius + 1, 2 * radius + 1))

    def test_gen_epanechnikov2D_kernel_sum(self):
        kernel = gen_epanechnikov2D_kernel(4)
        self.assertAlmostEqual(np.sum(kernel), 1.0, places=6)

    def test_gen_epanechnikov2D_kernel_INDEX(self):
        x, y, values = gen_epanechnikov2D_kernel(3, INDEX=True)
        self.assertEqual(len(x), len(y))
        self.assertEqual(len(y), len(values))
        self.assertTrue(np.all(values >= 0))
        self.assertAlmostEqual(np.sum(values), 1.0, places=6)

    def test_FlutDir_init(self):
        flut = FlutDir(10)
        self.assertEqual(len(flut.thetas), 37)

    def test_FlutDir_set_item(self):
        flut = FlutDir(10)
        flut.set_item(30, "Test Item")
        self.assertEqual(flut.items[flut.index(30)], "Test Item")

    def test_FlutDir_set_span(self):
        flut = FlutDir(10)
        center, inds, thetas = flut.set_span(45, 90)
        self.assertEqual(center, 50)
        self.assertEqual(len(inds), 11)

    def test_FlutDir_wrap_angle(self):
        flut = FlutDir(10)
        self.assertEqual(flut.wrap_angle(190), -170)
        self.assertEqual(flut.wrap_angle(-190), 170)

    def test_FlutDir_index(self):
        flut = FlutDir(10)
        self.assertEqual(flut.index(30), 21)

    def test_FlutDir_get_nearest(self):
        flut = FlutDir(10)
        flut.set_item(30, "Test Item")
        nearest_angle, item, vec = flut.get_nearest(30)
        self.assertEqual(nearest_angle, 30)
        self.assertEqual(item, "Test Item")


    def test_FlutDir_set_item_angle_out_of_range(self):
        flut = FlutDir(10)
        flut.set_item(370, "test")
        _ , item, _ = flut.get_nearest(370)
        self.assertEqual(item, "test")

    def test_FlutDir_set_span_length_mismatch(self):
        flut = FlutDir(10)
        with self.assertRaises(IOError):
            center = 0
            d_theta = flut.d_theta
            span = 360 - d_theta / 2 
            flut.set_span(center, span)

    def test_FlutDir_set_span_invalid_values(self):
        flut = FlutDir(10)
        with self.assertRaises(IOError):
            flut.set_span(0, 360)

    def test_FlutDir_get_span_corrupted_state(self):
        flut = FlutDir(10)
        flut.inds = [9999]
        with self.assertRaises(IndexError):
            flut.get_span()

    def test_FlutDir_unwrap_angle_non_iterable(self):
        flut = FlutDir(10)
        result = flut.unwrap_angle(-200)
        self.assertIsInstance(result, float)

    def test_FlutDir_unwrap_angle_non_numeric_elements(self):
        flut = FlutDir(10)
        with self.assertRaises(TypeError):
            flut.unwrap_angle("90")

    def test_FlutDir_wrap_angle_invalid_input(self):
        flut = FlutDir(10)
        with self.assertRaises(TypeError):
            flut.wrap_angle(None)

    def test_FlutDir_index_angle_out_of_range(self):
        flut = FlutDir(10)
        idx = flut.index(1000)
        self.assertTrue(0 <= idx < len(flut.items))

    def test_FlutDir_index_invalid_type(self):
        flut = FlutDir(10)
        with self.assertRaises(TypeError):
            flut.index("9")

    def test_FlutDir_get_nearest_empty_domain(self):
        flut = FlutDir(10)
        flut.inds = []
        with self.assertRaises(IndexError):
            flut.get_nearest(45)

    def test_FlutDir_get_nearest_nan_or_none_angle(self):
        flut = FlutDir(10)
        with self.assertRaises(TypeError):
            flut.get_nearest(None)
        with self.assertRaises(ValueError):
            flut.get_nearest(np.nan)

    def test_DsefFilters_init(self):
        dsef = DsefFilters(45)
        self.assertEqual(dsef.radius, 15)
        self.assertEqual(dsef.N, 3)

    def test_DsefFilters_set_direction(self):
        dsef = DsefFilters(45)
        dsef.set_direction(90, 90)
        self.assertEqual(dsef.flut.center, 0)

    def test_DsefFilters_exception_set_span(self):
        dsef = DsefFilters(45)
        with self.assertRaises(OSError):
            dsef.flut.set_span(0, 360)

    def test_DsefFilters_invalid_input(self):
        with self.assertRaises(TypeError):
            calc_heading_vector("90")
        
    def test_invalid_heading_vector(self):
        with self.assertRaises(ValueError):
            calc_heading("invalid_vector")

    def test_invalid_2d_kernel(self):
        with self.assertRaises(TypeError):
            gen_epanechnikov2D_kernel("string_radius")

if __name__ == '__main__':
    unittest.main()
