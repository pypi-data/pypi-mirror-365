import unittest
import numpy as np
from math import sqrt
from dsef.line_tools import normalized, normalvector, calc_heading_vector, calc_heading, RunningExponentialVectorAverage

class TestLineTools(unittest.TestCase):
    
    def test_normalized(self) -> None:
        v = [3, 4]
        result = normalized(v)
        expected = np.array([0.6, 0.8])
        np.testing.assert_almost_equal(result, expected)
    
    def test_normalized_zero_vector(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            normalized([0, 0])

    def test_normalized_wrong_size(self): 
        with self.assertRaises(ValueError):
            normalized([1.0])
        with self.assertRaises(ValueError):
            normalized([1.0, 2.0, 3.0])
    
    def test_normalvector_ccw(self) -> None:
        v = [1, 0]
        result = normalvector(v, CC=True, NORMALIZE=True)
        expected = np.array([0, -1])
        np.testing.assert_almost_equal(result, expected)
    
    def test_normalvector_cw(self) -> None:
        v = [1, 0]
        result = normalvector(v, CC=False, NORMALIZE=True)
        expected = np.array([0, 1])
        np.testing.assert_almost_equal(result, expected)

    def test_normalvector_wrong_length_vector(self): 
        with self.assertRaises(ValueError):
            normalvector([1.0])
        with self.assertRaises(ValueError):
            normalvector([1.0, 2.0, 3.0])

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
    
    def test_calc_heading(self) -> None:
        heading_vec = (1, 0)
        result = calc_heading(heading_vec)
        expected = 90.0
        self.assertAlmostEqual(result, expected)

    def test_calc_heading_diagonal_vector(self): 
        heading_vec = (sqrt(2)/2, sqrt(2)/2)
        result = calc_heading(heading_vec)
        expected = 45.0
        self.assertAlmostEqual(result, expected)
        heading_vec = (1/2, sqrt(3)/2)
        result = calc_heading(heading_vec)
        expected = 30.0
        self.assertAlmostEqual(result, expected)
    
    def test_calc_heading_wrong_length(self): 
        with self.assertRaises(ValueError):
            calc_heading((1.0, 2.0, 3.0))
    
    def test_calc_heading_invalid(self) -> None:
        with self.assertRaises(TypeError):
            calc_heading("invalid_vector")
    
    def test_reva_initialization(self) -> None:
        reva = RunningExponentialVectorAverage()
        np.testing.assert_almost_equal(reva.mu, np.array([0, 0]))
        np.testing.assert_almost_equal(reva.var, np.array([0, 0]))
        self.assertEqual(reva.rho, 0.1)
    
    def test_reva_push(self) -> None:
        reva = RunningExponentialVectorAverage()
        reva.push(np.array([1.0, 1.0]))
        expected_mu = np.array([0.1, 0.1])
        np.testing.assert_almost_equal(reva.mu, expected_mu)
    
    def test_reva_push_multiple(self): 
        reva = RunningExponentialVectorAverage()
        reva.push(np.array([1.0, 1.0]))
        reva.push(np.array([0.0, 1.0]))
        reva.push(np.array([1.0, 0.0]))
        reva.push(np.array([1.0, 0.5]))
        expected_mu = np.array([0.26, 0.2])
        np.testing.assert_almost_equal(reva.mu, expected_mu,2)

    def test_reva_push_non_ndarray(self): 
        reva = RunningExponentialVectorAverage()
        reva.push([1.0, 1.0])
        expected_mu = np.array([0.1, 0.1])
        np.testing.assert_almost_equal(reva.mu, expected_mu)

    def test_reva_push_wrong_dimension(self): 
        reva = RunningExponentialVectorAverage()    
        with self.assertRaises(ValueError):
            reva.push([1.0])

    def test_reva_rho_bounds(self):
        with self.assertRaises(ValueError):
            RunningExponentialVectorAverage(rho=-1)        
        with self.assertRaises(ValueError):
            RunningExponentialVectorAverage(rho=1.1)

    def test_reva_invalid_var_type(self):
        with self.assertRaises(ValueError):
            RunningExponentialVectorAverage(var=[1.0])

    def test_reva_invalid_mu_type(self):         
        with self.assertRaises(ValueError):
            RunningExponentialVectorAverage(mu=[1.0])

if __name__ == "__main__":
    unittest.main()