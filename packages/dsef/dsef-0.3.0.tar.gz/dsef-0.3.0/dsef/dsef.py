"""
dsef.py

The class containing the algorithms that search and follow edges
"""
import os
import math
import cv2
import numpy as np

from typing import Tuple, Optional, List, Literal

# Import the same modules as your original code
from dsef.dsef_base import DSEFBase
import dsef.dsef_tools as dftools
import dsef.line_tools as linetools

class Dsef:
    """
    Parameters:
        initial_direction_deg (float): The initial direction in degrees.
        direction_span (int): The span of directions for search.
        start_pixel (Tuple[float, float]): Starting pixel (x, y).
        end_pixel (Optional[Tuple[float, float]]): Ending pixel (x, y), optional.
        speed (Literal): Speed of the algorithm, one of "high", "medium", or "low".
        debug (bool): If True, enables debugging prints.
    """
    def __init__(self, 
                 initial_direction_deg: float, 
                 direction_span: int = 90, 
                 start_pixel: Tuple[float, float] = (1, 1), 
                 end_pixel: Optional[Tuple[float, float]] = None, 
                 speed: Literal["high", "medium", "low"] = "medium", 
                 debug=False):
        self.initial_direction_deg = initial_direction_deg
        self.direction_span = direction_span
        self.start_pixel = start_pixel
        self.end_pixel = end_pixel or (None, None)
        self.speed = speed.lower()
        self.debug = debug
        
        self.width = 0
        self.height = 0
        self.E = None
        self.edge_position = None
        self.img_edged = None

    def edge_search(self, img: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        Perform an edge search using the DSEF algorithm.

        Parameters:
            img (np.ndarray): The input image.

        Returns:
            Tuple[bool, np.ndarray]: Whether the edge was found and the resulting image.
        """
        img_ = img.copy()
        # Image Load and Initialize DSEF
        self._initialize_dsef(img_)
        search_step, _ = self._calculate_steps()
        edge_found, image = self._edge_search(search_step, img_)

        return edge_found, image


    def edge_follow(self) -> Optional[Tuple[List[Tuple[float, float]],np.ndarray]]:
        """
        Run the DSEF algorithm.

        Parameters:
            img (np.ndarray): The input image.

        Returns:
            Optional[List[Tuple[float, float]]]: List of edge coordinates if found, else None, and resulting image.
        """
        _, follower_step = self._calculate_steps()
        found_edge_line = None
        found_edge_line, image = self._edge_follow(follower_step)        
        
        return found_edge_line, image

    @staticmethod
    def convert_image(img: np.ndarray, ORG: bool = False) -> Tuple[np.ndarray,np.ndarray,np.ndarray, Tuple[int,int]]:
        """
        Convert the input image to different color spaces and return processed components.

        Parameters:
            img (np.ndarray): Input image.
            ORG (bool): If True, returns the original RGB image.

        Returns:
            Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Tuple[int, int]]:
                - The Hue channel of the image.
                - A mask of the image.
                - Original RGB image (if ORG is True).
                - The dimensions of the image (height, width).
        """
        im_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mask   = np.ones(im_rgb[:, :, 0].shape, dtype=int)
        im_hsv = cv2.cvtColor(im_rgb, cv2.COLOR_RGB2HSV_FULL)
        if not ORG:
            return im_hsv[:, :, 0], mask, None, im_hsv.shape[:2] # Only Hue and mask
        else:
            return im_hsv[:, :, 0], mask, im_rgb, im_hsv.shape[:2]

    def _initialize_dsef(self, img: np.ndarray) -> None:
        """
        Initialize the DSEF algorithm with the provided image.

        Parameters:
            img (np.ndarray): Input image.
        """
        im_hsv, _, _, (self.height, self.width) = self.convert_image(img, ORG=True)

        self.E = DSEFBase(im_hsv, edge_direction=self.initial_direction_deg, dir_span=self.direction_span, 
                            force_dtheta=self._get_forced_dtheta())

        self.E.DF.flut.reset_span()
        self.E.DF.flut.set_span(self.initial_direction_deg, self.direction_span)

        start_x, start_y = self.start_pixel
        self.E.move(start_x, start_y)

    def _get_forced_dtheta(self) -> float:
        """
        Returns the dtheta adjustment based on speed. 

        Returns:
            float: The dtheta adjustment based on speed.
        """
        speed_mapping = {"high": 10.0, "medium": 4.0, "low": 1.0}
        if self.debug:            
            print("[DEBUG] Overriding d_theta to:", speed_mapping.get(self.speed, 4.0) * self.direction_span / 90)
        return speed_mapping.get(self.speed, 4.0) * self.direction_span / 90

    def _calculate_steps(self) -> Tuple[float, float]:
        """ 
        Calculate search and follower steps based on speed.

        Returns:
            Tuple[float, float]: Search and follower step sizes.
        """
        start_x, start_y = self.start_pixel
        end_x, end_y = self.end_pixel
        dist = math.hypot(end_x - start_x, end_y - start_y)
        diag = math.hypot(self.width, self.height)

        step_mapping = {
            "low": [dist / 20.0/2, diag / 200.0],
            "medium": [dist / 30.0/2, diag / 100.0],
            "high": [dist / 40.0/2, diag / 50.0]
        }
        search_step, follower_step = step_mapping.get(self.speed, [dist / 30.0/2, diag / 100.0])
        if self.debug:
            print("[DEBUG] Distance between start and end:", dist)
            print("[DEBUG] Search step:", search_step)
            print("[DEBUG] Follower step:", follower_step)
        return search_step, follower_step

    def _edge_search(self, search_step: int, img: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        Execute the EdgeSearch phase of the algorithm.

        Parameters:
            search_step (int): The search step size.
            img (np.ndarray): The input image.

        Returns:
            Tuple[bool, np.ndarray]: Whether the edge was found and the resulting image.
        """        
        img_ = img.copy()
        start_x, start_y = self.start_pixel
        end_x, end_y = self.end_pixel
        v_dir = [end_x - start_x, end_y - start_y]
        d_ = math.hypot(*v_dir)
        if d_ == 0:
            if self.debug:
                print("[DEBUG] Start and end pixels are the same. Stopping EdgeSearch.")
            return [], []

        v_heading = [v_dir[0] / d_, v_dir[1] / d_]
        MAX_EDGE = 0
        u_edge, v_edge = start_x, start_y
        EDGE_FOUND = False
        while True:
            if not self.E.step(search_step * v_heading[0], search_step * v_heading[1]):
                if self.debug:
                    print("[DEBUG] Step out of image bounds => break EdgeSearch")
                break

            ui, vi = self.E.get_pos()
            img_ = cv2.circle(img_,(int(ui),int(vi)),3,(0,0,0),-1)
            T_FULL_main = dftools.dsef_test(self.E, self.E.u, self.E.v, self.E.edge_direction, FULL=True).FULL or 0
            if T_FULL_main > self.E.crit_edge:
                if T_FULL_main > MAX_EDGE + self.E.crit_edge:
                    MAX_EDGE = T_FULL_main
                    u_edge, v_edge = ui, vi
                    img_ = cv2.circle(img_,(int(u_edge),int(v_edge)),3,(0,0,0),-1)
                elif MAX_EDGE > 0 and T_FULL_main < MAX_EDGE - self.E.crit_edge:
                    self.E.move(u_edge, v_edge)
                    img_ = cv2.circle(img_,(int(u_edge),int(v_edge)),3,(0,0,0),-1)
                    EDGE_FOUND = True
                    if self.debug:
                        print("[DEBUG] Edge found. Breaking EdgeSearch.")
                    break

            v_now = [end_x - ui, end_y - vi]
            if v_heading[0] * v_now[0] + v_heading[1] * v_now[1] <= 0:
                if self.debug:
                    print("[DEBUG] We passed the end pixel => break EdgeSearch.")
                break
        self.img_edged = img_.copy()
        if EDGE_FOUND:
            self.edge_position = (self.E.u, self.E.v, self.E.u_float, self.E.v_float)
        return EDGE_FOUND, img_

    def _edge_follow(self, follower_step: int) -> Tuple[List[Tuple[float,float]], np.ndarray]:
        """
        Execute the EdgeFollow phase of the algorithm.

        Parameters:
            follower_step (int): The follower step size.
            img (np.ndarray): The input image.

        Returns:
            Tuple[List[Tuple[float, float]], np.ndarray]: The found edge line and the resulting image.
        """
        img_ = self.img_edged.copy()
        found_edge_line = []
        EDGE_FOUND, _, REWA, message, us, vs, arrow_list_follow, img_out = self.E.EdgeFollow(follower_step, img_, self.edge_position)
        
        if self.debug and message:
            print("[DEBUG] EdgeFollow message:", message)

        if EDGE_FOUND:
            x_start = self.E.u_edge
            y_start = self.E.v_edge
            direction_vec = REWA.mu
            # Draw a big line for visualization
            x_end = x_start + 1000*follower_step * direction_vec[0]
            y_end = y_start + 1000*follower_step * direction_vec[1]
            found_edge_line = [(x_start, y_start), (x_end, y_end)]
            
        return found_edge_line, img_out