"""
dsef_tools.py

Util functions for DSEF operations and filters
"""

import logging
import math
import numpy as np
from scipy import stats
from typing import Tuple, List, Union, Optional
import dsef.line_tools as linetools

log = logging.getLogger( "Debug" )


__all__ = ('get_t_critical',
           'calc_dof',
           'calc_heading_vector',
           'calc_heading',
           'heading2rotM',
           'epanechnikov1D',
           'gen_epanechnikov2D_kernel',
           'FlutDir',
           'DsefFilters'
           'DataClass',
           'nw',
           'nw_calc',
           'dsef_test')

def get_t_critical(df: int = 10, p: float = 0.001) -> float:
    """
    Calculate the critical value for a one-sided t-test.
    Parameters:
        df (int): Degrees of freedom for the t-test. Default is 10.
        p (float): Significance level (one-sided). Default is 0.001.

    Returns:
        float: Critical value for the given t-test parameters.
    """
    if int(df) != df:
        raise ValueError(f"'df' must be integer, got: {df}")
    return stats.t.ppf(1 - p, df)


def calc_dof(Lvar: float, Rvar: float, Neff: int) -> int:
    """
    Calculate degrees of freedom (dof)for weighted average.
    https://codingdisciple.com/hypothesis-testing-welch-python.html
    Parameters:
        Lvar (float): Left variance value.
        Rvar (float): Right variance value.
        Neff (int): Effective number of samples.

    Returns:
        int: Calculated degrees of freedom.
    """
    return np.floor(((Lvar+Rvar)/Neff)**2 / (((Lvar/Neff)**2)/(Neff-1) + ((Rvar/Neff)**2)/(Neff-1))).astype(int)
    
# Compass heading tools
def calc_heading_vector(heading_deg: float, dtype=np.float64) -> np.ndarray:
    """
    Calculate a heading vector, given compass heading

    Parameters:
        heading_deg (float): Compass heading in degrees (0, 90, 180, 270 - due north, east, south and west)
        dtype (np.dtype): Data type for the output array. Default is np.float64.

    Returns:
        np.ndarray: vector representing the heading.
    """
    t = np.radians(heading_deg)
    v = np.array([np.sin(t), np.cos(t)], dtype)
    return v/np.linalg.norm(v)

def calc_heading(heading_vec: np.ndarray) -> float:
    """
    Calculate heading from 2D heading vector. 
    Heading is defined from 0 to 360 deg.

    Parameters:
        heading_vec (np.ndarray): Vector representing the heading direction.

    Returns:
        float: Compass heading in degrees (0-360).
    """
    ve, vn = heading_vec    
    return (np.degrees(np.arctan2(ve, vn)) + 360) % 360.0

def heading2rotM(heading_deg: float) -> np.ndarray:
    """
    Calculate counter clockwise rotation matrix

    Parameters:
        heading_deg (float): Heading in degrees.

    Returns:
        np.ndarray: 2x2 rotation matrix.
    """
    heading_rad = math.radians(heading_deg)
    c = math.cos(heading_rad)
    s = math.sin(heading_rad)
    return np.array([[c, s], [-s, c]])

def epanechnikov1D(u: Union[float, np.ndarray], epa_norm: float = 3 / 4.0) -> Union[float, np.ndarray]:
    """
    Compute the 1D Epanechnikov kernel.

    Parameters:
        u (float or np.ndarray): Input values (distance from kernel center, normalized to [-1, 1]).
        epa_norm (float): Scaling factor (default: 3/4).

    Returns:
        float or np.ndarray: Evaluated Epanechnikov kernel values.
    """
    return epa_norm*(1 - u**2)*(np.abs(u) <= 1)*1.0

def gen_epanechnikov2D_kernel(r2: int, INDEX: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Generate a 2D Epanechnikov kernel.

    Parameters:
        r2 (int): Radius of the kernel in pixels.
        INDEX (bool): Whether to return the indices of kernel elements (default: False).

    Returns:
        np.ndarray: 2D array representing the kernel.
        (optional) Tuple of flattened x, y indices and kernel values within the kernel radius.
    """
    x,y  = np.meshgrid(range(0,2*r2+1), range(0,2*r2+1))
    u    = (np.sqrt(((x - r2)/r2) ** 2 + ((y - r2)/r2) ** 2))
    ep   = epanechnikov1D(u)
    ep  /= np.sum(ep)
    if INDEX:
        ind  = np.where(abs(u.ravel()) <= 1)
        return x.ravel()[ind], y.ravel()[ind], ep.ravel()[ind]
    else:
        return ep

class FlutDir:
    """
    Fast Lookup Table of, items and direction vectors.
    Divided into equidistant bins for a full 360-degree coverage.

    Attributes:
        d_theta (float): Angular step size in degrees between bins.
        center (float): Center angle for the lookup table (default: 0 degrees).
        
    """
    def __init__(self, d_theta: float, center: float = 0):
        self.dir_span = 360
        self.center   = center
        k             = int(self.dir_span/(2*d_theta) - 0.5) + 1
        self.d_theta  = self.dir_span/(2*k) 
        self.thetas   = [-k*self.d_theta + t*self.d_theta + self.center for t in range(0, 2*k+1)]    
        self.items    = [None]*len(self.thetas)
        self.dir_vec  = [linetools.calc_heading_vector(theta) for theta in self.thetas]
        self.reset_span()

    def reset_span(self):
        """
        Reset to initial span
        """
        self.dir_span = 360
        self.inds = [ind for ind in range(len(self.thetas))]     

    def set_item(self, theta: float, item: object):
        """
        Assign an item to angle bin.

        Parameters:
            theta (float): Direction in degrees to assign the item.
            item (object): Item to store in the bin.
        """
        index = self.index(theta)
        self.items[index] = item 

    def set_span(self, center: float, dir_span: float) -> Tuple [float, List[float],List[float]]:
        """
        Set span of LUT, as [center-dir_span/2, center+dir_span/2]

        Parameters:
            center (float): Center direction for the active span.
            dir_span (float): Angular width of the active span.

        Returns:
            Tuple [float, List[float],List[float]]:
            center direction, a list of indeces, the list of correspondent angles
        """
        if dir_span >= 360 - self.d_theta:
            raise IOError("You cant set the FLUT span >= 360-d_theta")
        self.dir_span = dir_span
        center    = self.wrap_angle(center)  # Just to make sure angle is within -180, 180
        ind       = int((center - self.thetas[0])/self.d_theta + 0.5)
        center    = self.thetas[ind]         # neares actual center angle
        kk        = int(dir_span/(2*self.d_theta) + 0.5)+1# Number of cells on each side of center   
        thetas    = [self.wrap_angle(center + k*self.d_theta) for k in range(-kk+1, kk)] # The calculated directions
        # The indeces where the calculated directions are closer to the directions in the LUT
        self.inds = [int((theta - self.thetas[0])/self.d_theta + 0.5) for theta in thetas] 
        return center, self.inds, [self.thetas[ind] for ind in self.inds]

    def get_span(self) -> Tuple[List[float], List[Optional[object]], List[np.ndarray]]:
        """
        Get current angle, item and dir_vecs span in LUT

        Returns:
            Tuple[List[float], List[Optional[object]], List[np.ndarray]]:
            angles, items, and direction vectors within the current span.
        """
        return (
            [self.thetas[ind] for ind in self.inds], 
            [self.items[ind] for ind in self.inds], 
            [self.dir_vec[ind] for ind in self.inds]
        )

    def unwrap_angle(self, angle: float) -> float:
        """
        Unwrap to list of monotonic increasing angles. 
        Pay special attention to end points.
        Parameters:
            angle (float): Wrapped angle.

        Returns:
            float: unwrapped angle.
        """
        if angle < self.thetas[self.inds[0]]:
            if abs(angle - self.thetas[self.inds[0]]) > abs(angle - self.thetas[self.inds[-1]]):
                return angle + 360
            else:
                return self.thetas[self.inds[0]]
        else:
            return angle

    def wrap_angle(self, angle: float) -> float:
        """
        Wrap an angle to the range [-180, 180].

        Parameters:
            angle (float): Angle to be wrapped.

        Returns:
            float: Wrapped angle.
        """
        angle = angle % 360
        if (angle <= -180):
            angle += 360
        elif (angle > 180): 
            angle -= 360
        return angle

    def index(self, direction: float) -> int:
        """
        Return index of nearest angle in LUT, relative to current span.      
        clip to prevent index overflow  

        Parameters:
            direction (float): Direction in degrees to find the nearest bin.

        Returns:
            int: Index of the nearest angle.
        """
        direction = self.wrap_angle(direction)
        ind       = int((self.unwrap_angle(direction) - self.thetas[self.inds[0]])/self.d_theta + 0.5)
        return self.inds[min(max(0, ind), len(self.inds)-1)]

    def get_nearest(self, direction: float) -> Tuple[float, object, np.ndarray]:
        """
        Get the nearest angle, item, and direction vector.

        Parameters:
            direction (float): Direction in degrees.

        Returns:
            Tuple[float, object, np.ndarray]: Nearest angle, associated item, and vector.
        """
        ind              = self.index(direction)
        return (self.thetas[ind], self.items[ind], self.dir_vec[ind])
    
class DsefFilters:
    """
    Directional Step Edge Follower (DSEF) Class. Represented as a filter bank.

    Attributes:
        radius (float): Radius of the circular filter area.
        N (int): Number of filters in each direction.
        bu (float): Offset along the u-axis.
        bv (float): Offset along the v-axis.
        flut (FlutDir): Fast lookup table for filter directions.
    """
    def __init__(
        self, 
        edge_direction: float, 
        radius: int = 15, 
        N: int = 3, 
        bu: int = 0, 
        bv: int = 0, 
        dir_span: int = 90, 
        force_dtheta: Union[float, None] = None
    ):
        self.radius = radius                         # Radius per circular filter area
        self.N      = N                              # Number of filters in each direction
        self.bu     = bu                             # Offset along u axis
        self.bv     = bv                             # Offset along v axis
        self.R = math.hypot(self.bu + self.radius, self.bv + self.radius)
        
        d_theta     = np.degrees(self.radius/self.R) # step size between filter bank directions
        if force_dtheta is not None:
            d_theta = force_dtheta   
            
        self.flut   = FlutDir(d_theta)               # Initialize fast LUT #Fabio: d_theta is always the same. too big
        # Initialize the filter bank. Full 360 degrees
        self._ini_filters()                         
        # Set filter bank span and direction
        self.set_direction(edge_direction, dir_span) # Set filterbank main direction and span
        
    def set_direction(self, edge_direction: float, dir_span: float) -> None:
        """
        Set filterbank main direction, calculate normal vector and calculare 
        relative positions along edge normal for edge position refinement
        
        Parameters:
            edge_direction (float): Main edge direction in degrees.
            dir_span (float): Span of directions covered by the filter bank.
        """
        # Set FLUT span
        self.edge_direction        = edge_direction
        self.flut.set_span(self.edge_direction, dir_span)
        # Relative positions along normal vector, used for refining position
        self.edge_direction_vector = linetools.calc_heading_vector(edge_direction)
        self.edge_normal_vector    = linetools.normalvector(self.edge_direction_vector)
        u0,v0 = -self.radius*self.edge_normal_vector
        u1,v1 = self.radius*self.edge_normal_vector
        length = int(np.hypot(u1-u0, v1-v0) + 0.5)            
        self.edge_refine_pos = [np.linspace(u0, u1, length, dtype=int), np.linspace(v0, v1, length, dtype=int)]

    def _calc_regs(self, heading_deg: float, dtype: type = int) -> Tuple[float, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], np.ndarray]:
        """
        Calculate all region coordinates given a specific compass heading in degrees.

        Parameters:
            heading_deg (float): Direction in degrees.
            dtype (type): Data type for coordinates.

        Returns:
            Tuple[float, Tuple[np.ndarray, ...], np.ndarray]: Direction, region coordinates, 
            and direction vector.
        """
        R  = heading2rotM(heading_deg)
        RU = np.round(R.dot(self._RU.T).T).astype(dtype)  # Right-upper
        RD = np.round(R.dot(self._RD.T).T).astype(dtype)  # Right-down
        LU = np.round(R.dot(self._LU.T).T).astype(dtype)  # Left-upper
        LD = np.round(R.dot(self._LD.T).T).astype(dtype)  # Left-down
        return heading_deg, (RU, RD, LU, LD), linetools.calc_heading_vector(heading_deg)
    
    def _ini_filters(self):
        """
        Initializes the regions of interest (ROIs) for the filter bank.
        RU - right-up, RD - right-down, LU - left up, LD - left down
        """
        self._RU   = np.c_[self.N*[self.bu  + self.radius], [(1+2*k)*self.radius   + self.bv for k in range(0, self.N)]]
        self._RD   = np.c_[self.N*[self.bu  + self.radius], [-(1+2*k)*self.radius  - self.bv for k in range(0, self.N)]]
        self._LU   = np.c_[self.N*[-self.bu - self.radius], [(1+2*k)*self.radius  + self.bv for k in range(0, self.N)]]
        self._LD   = np.c_[self.N*[-self.bu - self.radius], [-(1+2*k)*self.radius - self.bv for k in range(0, self.N)]]
        self.max_r = np.ceil(np.linalg.norm(self._RU[-1]) + self.radius - 1).astype(int)  # Max radius of filter bank, for any angles        
        for ind in self.flut.inds:
            theta, (RU, RD, LU, LD), v = self._calc_regs(self.flut.thetas[ind])     # FIXME
            self.flut.set_item(theta, [RU, RD, LU, LD])
    
class DataClass():
    """
    Return the attribute value if defined, if not return None
    """
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
    def __getattr__(self, item): # All unset attributes defaults to None
        return None
    def __repr__(self):
        return str(self.__dict__)


def nw(
        c: int, 
        r: int, 
        kernel: np.ndarray, 
        im_pad: np.ndarray, 
        mask_pad: np.ndarray, 
        dtype: type = np.float64
    ) -> Tuple[float, float]:
    """
    Calculate nadaraya-watson estimate for mean and variance within
    a region = [u, v], using the 2D kernel around that position.

    Parameters:
        c (int): Column coordinate.
        r (int): Row coordinate.
        kernel (np.ndarray): 2D kernel array.
        im_pad (np.ndarray): Padded image data.
        mask_pad (np.ndarray): Padded mask data.
        dtype (type): Data type for calculations.

    Returns:
        Tuple[float, float]: Estimated mean and variance.
    """
    Nw_r, Nw_c = kernel.shape    
    # Compute bounding box for the kernel
    minn_r, maxx_r = r - (Nw_r // 2), r + Nw_r - (Nw_r // 2)
    minn_c, maxx_c = c - (Nw_c // 2), c + Nw_c - (Nw_c // 2)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Option C: Skip partial kernel tests
    # If the bounding box extends outside the valid padded image,
    # just skip or return (0, 0).
    if (
        minn_r < 0 or 
        maxx_r > mask_pad.shape[0] or
        minn_c < 0 or 
        maxx_c > mask_pad.shape[1]
    ):
        # This means the kernel is partially or totally out of bounds.
        # Return (0, 0) so that the calling code sees no edge signal here.
        return (0, 0)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Normal code continues if fully in-bounds
    den = np.sum(kernel * mask_pad[minn_r : maxx_r, minn_c : maxx_c].astype(dtype))
    if den != 0:
        nw_mean  = np.sum(kernel * im_pad[minn_r : maxx_r, minn_c : maxx_c]) / den
        nw_sq    = np.sum(kernel * im_pad[minn_r : maxx_r, minn_c : maxx_c]**2.0) / den
        nw_var   = nw_sq - nw_mean**2.0
    else:
        nw_mean  = 0
        nw_var   = 0

    return (nw_mean, nw_var)


def nw_calc(
        E: DataClass, 
        rcL: List[Tuple[int, int]], 
        rcR: List[Tuple[int, int]], 
        dtype: type = np.float64
    ) -> Union[float, int]:
    """
    Nadaraya-Watson. Coordinates are relative to the padded numpy array.

    Parameters:
        E (DataClass): Encapsulation of input data and parameters.
        rcL (List[Tuple[int, int]]): List of (row, column) coordinates for the left region.
        rcR (List[Tuple[int, int]]): List of (row, column) coordinates for the right region.
        dtype (type, optional): Data type for calculations. Defaults to np.float64.

    Returns:
        Union[float, int]: The computed statistical test value or 0 if variance is too small.
    
    """
    L_nw          = [nw(ri,ci,E.ep2D,E.im_pad, E.mask_pad) for ri,ci in rcL]
    L_mu, L_var   = np.mean(np.array(L_nw, dtype)[:,0]), np.mean(np.array(L_nw, dtype)[:,1])
    R_nw          = [nw(ri,ci,E.ep2D,E.im_pad, E.mask_pad) for ri,ci in rcR]
    R_mu, R_var   = np.mean(np.array(R_nw, dtype)[:,0]), np.mean(np.array(R_nw, dtype)[:,1])
    RL_var        = L_var/E.Neff + R_var/E.Neff
    if RL_var < 1e-6:
        # One or more filters are in the zero padded region
        return 0
    else:
        return (R_mu - L_mu)/np.sqrt(RL_var)    

def dsef_test(
        E: DataClass, 
        u: int, 
        v: int, 
        direction: float, 
        ALL: bool = False, 
        FULL: bool = False, 
        FORWARD: bool = False, 
        REAR: bool = False, 
        END: bool = False, 
        USE_LUT: bool = True
    ) -> DataClass:
    """
    Calculate statistical tests for DSEF searcher.
    u,v are relative to padded image.
    Direction is relative to current span.

    Parameters:
        E (DataClass): Encapsulation of input data and parameters.
        u (int): Row coordinate relative to the padded image.
        v (int): Column coordinate relative to the padded image.
        direction (float): Direction relative to the current span.
        ALL (bool, optional): Whether to test all regions. Defaults to False.
        FULL (bool, optional): Whether to perform a full edge test. Defaults to False.
        FORWARD (bool, optional): Whether to perform a forward edge test. Defaults to False.
        REAR (bool, optional): Whether to perform a rear edge test. Defaults to False.
        END (bool, optional): Whether to perform an end test. Defaults to False.
        USE_LUT (bool, optional): Whether to use the LUT for direction retrieval. Defaults to True.

    Returns:
        DataClass: Encapsulation of test results.
    """
    T = DataClass()
    if USE_LUT:
        _, (RU, RD, LU, LD), _ = E.DF.flut.get_nearest(direction)
    else: 
        _, (RU, RD, LU, LD), _ = E.DF._calc_regs(direction)  

    # Full edge test
    if FULL:
        rcL           = np.r_[LU, LD] + np.array([u, v])
        rcR           = np.r_[RU, RD] + np.array([u, v])
        T.FULL        = nw_calc(E, rcL, rcR)
    # Forward edge test    
    if FORWARD:
        rcL           = np.r_[LU] + np.array([u, v])
        rcR           = np.r_[RU] + np.array([u, v])
        T.FORWARD    = nw_calc(E, rcL, rcR)
    # Rear edge test
    if REAR:
        rcL           = np.r_[LD] + np.array([u, v])
        rcR           = np.r_[RD] + np.array([u, v])
        T.REAR        = nw_calc(E, rcL, rcR)
    # End test - Test one single regions from Right up (RU[0]) side against right down side (RD)
    if END:
        rcD           = np.r_[RD] + np.array([u, v])
        rcU           = np.r_[RU] + np.array([u, v])
        rcU           = np.r_[[RU[-1]]] + np.array([u, v])        
        T.END         = nw_calc(E, rcU, rcD)

    # Test if all right > left
    if ALL:
        rcL           = np.r_[LU, LD] + np.array([u, v])
        rcR           = np.r_[RU, RD] + np.array([u, v])
        T.ALL         = [nw_calc(E, [l], [r]) for l,r in zip(rcL, rcR)]

    
    return T

