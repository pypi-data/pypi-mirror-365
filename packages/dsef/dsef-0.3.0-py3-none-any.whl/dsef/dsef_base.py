"""
dsef_base.py

The base class of DSEF
"""

import math
import numpy as np
import cv2
import copy
from typing import Optional
import dsef.line_tools as linetools
import dsef.dsef_tools as dftools

class DSEFBase:
    """
    Base of Direct Step Edge Follower

    Attributes:
        im: The input image (2D numpy array) to process.
        edge_direction: Initial edge direction in degrees.
        dir_span: The span of the edge directions (default: 90).
        t_crit: Optional threshold for critical value in edge detection.
        dtype: The data type for the filter operations (default: np.float64).
        force_dtheta: Optional value to enforce a specific angular step size for the filter.
    """
    def __init__(self, im: np.ndarray, edge_direction: float, dir_span: int = 90, t_crit: float = None,
                 dtype: np.dtype = np.float64, force_dtheta: float = None):
        
        if im is None:
            raise ValueError("No Image is being processed")
        
        self.dtype=dtype
        # Initialize the directional step edge filter bank
        self.DF                = dftools.DsefFilters(edge_direction=edge_direction, dir_span=dir_span, force_dtheta=force_dtheta)
        self.edge_direction    = edge_direction
        # Pad image
        # PS! numpy arrays are row major
        self.upad, self.vpad   = math.ceil(self.DF.R+self.DF.radius), math.ceil(self.DF.R+self.DF.radius)
        self.u_float           = 0.0
        self.v_float           = 0.0
        self.Nv, self.Nu       = im.shape[0:2]  # TODO: Check that this is correct
        self.im_pad            = np.pad(im, (self.vpad, self.upad))
        self.mask_pad          = np.pad(np.ones_like(im),(self.vpad, self.upad))
        # kernels                
        self.u, self.v         = None, None
        self.ep2D              = dftools.gen_epanechnikov2D_kernel(self.DF.radius)
        self.ep2D_sq_sum       = np.sum(self.ep2D**2)
        # Calculate the threshold values based on image statistics
        # For a Poisson distribution, the variance equals the mean        
        self.Neff              = (np.sum(self.ep2D)**2) / np.sum(self.ep2D**2)  # Kish Effective sample size
        PoiVar                 = 150.0
        dof_edge               = dftools.calc_dof(PoiVar, PoiVar, self.Neff)
        dof_end                = dftools.calc_dof(PoiVar, PoiVar, self.Neff)
        CRIT_FAC=1#
        self.crit_edge         = t_crit if t_crit is not None else CRIT_FAC * dftools.get_t_critical(df=dof_edge)
        self.crit_end          = t_crit if t_crit is not None else CRIT_FAC * dftools.get_t_critical(df=dof_end)
        
    def _within_bounds(self, u: int, v: int) -> bool:
        """
        Checks if the given pixel coordinates (u, v) are within the image bounds.

        Parameters:
            u: The x-coordinate of the pixel.
            v: The y-coordinate of the pixel.

        Returns:
            bool: True if coordinates are within the bounds, False otherwise.
        """
        if u >= self.upad and u < self.Nu + self.upad and v >= self.vpad and v < self.Nv + self.vpad:
            return True
        return False

    def step(self, du: float, dv: float) -> bool:
        """
        Step filter in given direction. In pixel coordinates.

        Parameters:
            du: The step in the x-direction.
            dv: The step in the y-direction.

        Returns:
            bool: True if the step was successful, False if the new position is out of bounds.
        """
        if type(du) not in [float, int, np.float64] or\
            type(dv) not in [float, int, np.float64]:
            raise ValueError(f"Wrong datatype!")
        return self.move(self.u_float + du - self.upad, self.v_float + dv - self.vpad)
    
    def move(self, u: float, v: float) -> bool:
        """
        Move filter to new location, in pixel coordinates.

        Args:
            u: The new x-coordinate.
            v: The new y-coordinate.

        Returns:
            bool: True if the move was successful (i.e., within bounds), False otherwise.
        """
        if type(u) not in [float, int, np.float64] or\
            type(v) not in [float, int, np.float64]:
            raise ValueError("Wrong datatype!")
        u_new = round(u + self.upad)
        v_new = round(v + self.vpad)
        if not self._within_bounds(u_new, v_new):
            return False
        else:
            self.u = u_new
            self.v = v_new
            self.u_float = u + self.upad
            self.v_float = v + self.upad
            return True
    
    def get_pos(self) -> tuple:
        """ 
        Return position of filter in pixel coordinates (unpadded)

        Returns:
            tuple: (u, v) - The filter position in unpadded pixel coordinates.
        """
        return self.u-self.upad, self.v-self.vpad

    def find_best_direction(self) -> tuple:
        """
        Find the best direction given the current LUT direction and span

        Returns:
            tuple: (direction, direction_vector) - The best direction and its corresponding vector.
        """
        # Get span
        sel_dirs, sel_items, sel_dirvecs = self.DF.flut.get_span()
        # Calculate T_FORWARD for current flut span
        t = [dftools.dsef_test(self, self.u, self.v, direction, FORWARD=True).FORWARD for direction in sel_dirs]    
        # Find best direction to follow
        ind_max = np.argmax(t)
        if (t[ind_max] < t[len(sel_dirs)//2] + self.crit_edge):  # Stay on previous track
            ind_max = len(sel_dirs)//2
        return sel_dirs[ind_max], sel_dirvecs[ind_max]
     
    def EdgeSearch(self, 
                   start: tuple, 
                   stop: tuple, 
                   img: np.ndarray, 
                   OPTIMIZE_SEARCH_DIRECTION: bool = False
                   ) -> tuple:
        """
        Search for edge. Can return multiple edge candidates..

        Parameters:
            start: The starting pixel coordinates (u, v).
            stop: The stopping pixel coordinates (u, v).
            img: The image in which the edge is being searched.
            OPTIMIZE_SEARCH_DIRECTION: Flag to optimize the search direction dynamically (default: False).

        Returns:
            tuple: A tuple (EDGE, position, image), where:
                EDGE (bool): Indicates if the edge was found.
                position (tuple): The final position of the filter in unpadded coordinates.
                image (np.ndarray): The updated image with circles marking the edge positions.
        """
        img_ = img.copy()
        # Step along profile until edge is found, or end of profile/image is reached
        step = (self.DF.radius + min(self.DF.bu, self.DF.bv))

        # Calculate search direction vector
        u_new, v_new   = start
        u_edge, v_edge = start
        v_dir          = [stop[0]-u_new, stop[1]-v_new]
        d              = (v_dir[0]**2 + v_dir[1]**2)**0.5
        v_heading      = [v_dir[0]/d, v_dir[1]/d]

        EDGE = False
        MAX_EDGE = 0
        v = v_dir

        while v_heading[0]*v[0] + v_heading[1]*v[1] > 0:       # until we have passed the stop point
            
            if not self.step(step*v_heading[0], step*v_heading[1]):
                break
            u_new, v_new = self.get_pos()
            img_ = cv2.circle(img_,(int(u_new),int(v_new)),3,(0,0,0),-1)
            
            if OPTIMIZE_SEARCH_DIRECTION:
                self.edge_direction = self.find_best_direction()
            c,r    = self.get_pos()
            T_FULL = dftools.dsef_test(self, self.u, self.v, self.edge_direction, FULL=True).FULL
            EDGE   = T_FULL > self.crit_edge
            # Return if edge is found
            # Refine position nefore returning            
            if EDGE:
                if T_FULL > MAX_EDGE + self.crit_edge:
                    MAX_EDGE = T_FULL
                    u_edge, v_edge = u_new, v_new
                    img_ = cv2.circle(img_,(int(u_edge),int(v_edge)),3,(0,0,0),-1)
                elif MAX_EDGE > 0 and T_FULL < MAX_EDGE - self.crit_edge:
                    # Edge found !!!
                    self.move(u_edge, v_edge)                    
                    img_ = cv2.circle(img_,(int(u_edge),int(v_edge)),3,(0,0,0),-1)
                    break
                
            # Calculate vector from current position to end of profile
            v = [stop[0]-u_new, stop[1]-v_new]  
            img_ = cv2.circle(img_,(int(u_edge),int(v_edge)),4,(0,0,0),-1)      
        return EDGE, self.get_pos(), img_
    
    def EdgeFollow(self, follower_step: float, img: np.ndarray, edge_position: Optional[tuple] = None, MAX_ITT: int = 1000, Ntest_edge: int = 2):
        """ 
        Follow edge until end of line, or image boundary, or maximum number of iterations reached.

        Parameters:
            follower_step (int): The follower step size.
            img (np.ndarray): The input image.
            MAX_ITT (int): maximum number of iterations.
            Ntest_edge (int): number of tests for considering an edge

        Returns:
            Tuple[List[Tuple[float, float]], np.ndarray]: The found edge line and the resulting image.
        """
        img_ = img.copy()
        step = follower_step
        df = copy.deepcopy(self.DF)
        sel_dirs, _, sel_dirvecs = df.flut.get_span()
        consec_edge, consec_no_edge = 0, 0
        message = None
        if edge_position:
            self.u, self.v, self.u_float, self.v_float = edge_position
        self.u_edge, self.v_edge = self.get_pos()
        EDGE_FOUND, END_FOUND = False, False
        ABORT_WHEN_ACCURATE = True 
        REWA = linetools.RunningExponentialVectorAverage(var=np.array([2,2]), rho=0.1)

        # pick best direction from current span
        t1 = [dftools.dsef_test(self, self.u, self.v, d, FORWARD=True, FULL=True).FULL for d in sel_dirs]
        ind_max = np.argmax(t1)
        best_direction = sel_dirvecs[ind_max]
        REWA.push(best_direction)

        
        us_, vs_ = [], []
        arrow_list_follow = []  # We'll store arrow info for each iteration
        Nitt = 0

        while Nitt < MAX_ITT:
            Nitt += 1
            ui, vi = self.get_pos()
            img_ = cv2.circle(img_,(int(ui),int(vi)),3,(128,128,128),-1)
            us_.append(ui)
            vs_.append(vi)

            # forward test for each direction
            t_ = [dftools.dsef_test(self, self.u, self.v, d, FORWARD=True, FULL=True).FULL for d in sel_dirs]
            ind_max = np.argmax(t_)
            if t_[ind_max] < t_[len(sel_dirs)//2] + self.crit_edge:
                ind_max = len(sel_dirs)//2
            v = sel_dirvecs[ind_max]
            T_ALL = dftools.dsef_test(self, self.u, self.v, sel_dirs[ind_max], ALL=True).ALL
            if T_ALL is None:
                T_ALL = []
            ALL_EDGE = np.all(np.array(T_ALL) > self.crit_edge)
            # e.g. store direction & T_FORWARD in arrow_list_follow
            arrow_list_follow.append([
                (d, t_val if t_val is not None else 0.0)
                for d, t_val in zip(sel_dirs, t_)
            ])
            if ALL_EDGE:
                consec_edge = min(consec_edge+1, Ntest_edge)
                consec_no_edge = 0
            else:
                consec_edge = max(0, consec_edge-1)
                consec_no_edge += 1
            if consec_no_edge >= 2*df.N + 1:
                message = "CANCEL. WE LOST THE EDGE"
                break
            if consec_edge >= Ntest_edge:
                if not EDGE_FOUND:
                    self.u_edge, self.v_edge = self.get_pos()
                    EDGE_FOUND = True
                REWA.push(v)
                mu_direction = df.flut.wrap_angle(linetools.calc_heading(REWA.mu))
                var_direction = REWA.var[0]**2 
                var_direction = np.degrees(np.arctan(REWA.var[1]/(1+REWA.var[0])))

                if var_direction > df.flut.d_theta:
                    df.flut.set_span(mu_direction, 4*var_direction**0.5)
                    sel_dirs, sel_items, sel_dirvecs = df.flut.get_span()
                elif ABORT_WHEN_ACCURATE:
                    message = ("ABORTING. Edge direction +/- %.1f deg" 
                                % (var_direction**0.5))
                    break
                
            # move filter forward
            if not self.step(v[0]*step, v[1]*step):
                message = "we reached END of image"
                END_FOUND = True
                break
        return EDGE_FOUND, END_FOUND, REWA, message, us_, vs_, arrow_list_follow, img_
    