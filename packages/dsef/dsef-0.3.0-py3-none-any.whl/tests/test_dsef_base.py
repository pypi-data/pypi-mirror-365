import unittest
import numpy as np
from unittest.mock import patch
from dsef.dsef_base import DSEFBase
import dsef.dsef_tools as dftools

class TestDSEFBase(unittest.TestCase):
    
    def setUp(self):
        self.im = np.zeros((100, 100), dtype=np.float64)
        self.edge_direction = 45.0
        self.dsef = DSEFBase(self.im, self.edge_direction)
    
    def test_initialization(self):
        self.assertIsInstance(self.dsef, DSEFBase)
        self.assertEqual(self.dsef.edge_direction, self.edge_direction)
        self.assertEqual(self.dsef.Nu, self.im.shape[1])
        self.assertEqual(self.dsef.Nv, self.im.shape[0])

    def test_within_bounds_valid(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.dsef.upad, self.dsef.vpad = 0, 0
        self.assertTrue(self.dsef._within_bounds(10, 10))
    
    def test_within_bounds_invalid(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.assertFalse(self.dsef._within_bounds(150, 150))
    
    def test_step_success(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.dsef.upad, self.dsef.vpad = 0, 0
        self.assertTrue(self.dsef.step(5.0, 5.0))

    def test_step_failure(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.dsef.Nu, self.dsef.Nv = 50, 50
        self.assertFalse(self.dsef.step(100.0, 100.0))

    def test_move_success(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.assertTrue(self.dsef.move(15.0, 15.0))

    def test_move_failure(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.dsef.Nu, self.dsef.Nv = 50, 50
        self.assertFalse(self.dsef.move(100.0, 100.0))

    def test_get_pos(self):
        self.dsef.u, self.dsef.v = 10, 10
        self.dsef.upad, self.dsef.vpad = 0, 0
        self.assertEqual(self.dsef.get_pos(), (10, 10))

    def test_find_best_direction(self):
        self.dsef.u, self.dsef.v = 10, 10
        with patch.object(dftools.FlutDir, 'get_span', return_value=([0, 45, 90], [0, 1, 2], [[1, 0], [0, 1], [-1, 0]])):
            direction, _ = self.dsef.find_best_direction()
            self.assertIn(direction, [0, 45, 90])

    def test_find_best_direction_crazy_direction(self):        
        self.dsef.u, self.dsef.v = 10, 10
        with patch.object(dftools.FlutDir, 'get_span', return_value=([0, 0, 0], [0, 0, 0], [[1, 0], [0, 1], [1, 1]])):
            direction, _ = self.dsef.find_best_direction()
            self.assertEqual(direction, 0)

    def test_edge_follow_lost_edge(self):
        self.dsef.u, self.dsef.v = 10, 10
        img = np.zeros_like(self.im)
        with patch('dsef.dsef_tools.dsef_test', return_value=type('obj', (object,), {'FULL': 0.0, 'ALL': 0.0})):
            EDGE_FOUND, END_FOUND, _, _, _, _, _, _ = self.dsef.EdgeFollow(1.0, img)
            self.assertFalse(EDGE_FOUND)
            self.assertTrue(END_FOUND)

    def test_invalid_image(self):
        with self.assertRaises(ValueError):
            DSEFBase(None, self.edge_direction)

    def test_invalid_move_coordinates(self):
        with self.assertRaises(ValueError):
            self.dsef.move("invalid", 10)

    def test_invalid_step_coordinates(self):
        with self.assertRaises(ValueError):
            self.dsef.step("invalid", 10)

if __name__ == '__main__':
    unittest.main()
