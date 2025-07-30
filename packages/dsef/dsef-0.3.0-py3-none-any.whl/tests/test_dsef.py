import unittest
import numpy as np
from unittest.mock import patch
from dsef import Dsef


class TestDsef(unittest.TestCase):

    def setUp(self):
        self.initial_direction_deg = 45.0
        self.direction_span = 90
        self.start_pixel = (0, 0)
        self.end_pixel = (100, 100)
        self.speed = "medium"
        self.debug = False
        self.dsef = Dsef(self.initial_direction_deg, self.direction_span, self.start_pixel, self.end_pixel, self.speed, self.debug)

    @patch('cv2.cvtColor')  
    def test_convert_image(self, mock_cvtColor):
        mock_cvtColor.return_value = np.zeros((10, 10, 3), dtype=np.uint8)
        
        img = np.zeros((10, 10, 3), dtype=np.uint8)  
        im_hsv, mask, im_rgb, shape = self.dsef.convert_image(img, ORG=True)
        
        self.assertEqual(im_hsv.shape, (10, 10))
        self.assertEqual(mask.shape, (10, 10))
        self.assertEqual(im_rgb.shape, (10, 10, 3))
        self.assertEqual(shape, (10, 10))

    @patch('dsef.dsef_tools.dsef_test')
    @patch('cv2.circle')
    def test_edge_search(self, mock_circle, mock_dsef_test):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_dsef_test.return_value.FULL = 1.0
        mock_circle.return_value = img

        edge_found, image = self.dsef.edge_search(img)
        
        self.assertFalse(edge_found)
        self.assertEqual(image.shape, (100, 100, 3))
        mock_circle.assert_called()

    def test_get_forced_dtheta(self):
        self.dsef.speed = "high"
        dtheta_high = self.dsef._get_forced_dtheta()
        self.dsef.speed = "medium"
        dtheta_medium = self.dsef._get_forced_dtheta()
        self.dsef.speed = "low"
        dtheta_low = self.dsef._get_forced_dtheta()

        self.assertGreater(dtheta_high, dtheta_medium)
        self.assertGreater(dtheta_medium, dtheta_low)

    @unittest.skip("TODO: handle dtheta with invalid speed")
    def test_get_forced_dtheta_invalid_speed(self):
        pass

    def test_calculate_steps(self):
        self.dsef.speed = "high"
        search_step_high, _ = self.dsef._calculate_steps()
        self.dsef.speed = "medium"
        search_step_medium, _ = self.dsef._calculate_steps()
        self.dsef.speed = "low"
        search_step_low, _ = self.dsef._calculate_steps()

        self.assertGreater(search_step_medium, search_step_high)
        self.assertGreater(search_step_low, search_step_medium)

    @unittest.skip("TODO: handle step with invalid speed")
    def test_get_calculate_steps_invalid_speed(self):
        pass

    def test_edge_search_no_edge(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.dsef.start_pixel = (0, 0)
        self.dsef.end_pixel = (0, 0)

        edge_found, image = self.dsef.edge_search(img)
        self.assertFalse(edge_found)

    @unittest.skip("TODO: test edge search")
    def test_edge_search(self):
        pass

    @unittest.skip("TODO: test edge follow")
    def test_edge_follow(self):
        pass

    @unittest.skip("TODO: handle edge follow without edge")
    def test_edge_follow_no_edge(self):
        pass


if __name__ == '__main__':
    unittest.main()
