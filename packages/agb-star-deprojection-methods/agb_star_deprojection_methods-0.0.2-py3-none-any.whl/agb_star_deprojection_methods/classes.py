from astropy.io import fits
from astropy.io.fits import PrimaryHDU, Header
from astropy import units as u
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.patches import Ellipse
import numpy as np
from numpy import ndarray, dtype, float64
from scipy.interpolate import interpn
from scipy.optimize import curve_fit
from scipy.optimize.elementwise import find_root, bracket_root
from collections.abc import Callable
from typing import Literal
import plotly.graph_objects as go 
import warnings
import scipy.integrate as integrate
from dataclasses import dataclass
from matplotlib.path import Path
from matplotlib.widgets import LassoSelector
from matplotlib.image import AxesImage
from matplotlib.backend_bases import MouseEvent
import matplotlib as mpl

# custom type aliases
DataArray1D = ndarray[tuple[int], dtype[float64]]
DataArray3D = ndarray[tuple[int, int, int], dtype[float64]]
Matrix2x2 = ndarray[tuple[Literal[2], Literal[2]], dtype[float64]]
VelocityModel = Callable[[ndarray], ndarray]

# custom errors
class FITSHeaderError(Exception):
    pass

@dataclass
class CondensedData:
    """
    Container for storing a condensed version of the data cube and its associated metadata.

    Attributes
    ----------
    x_offsets : DataArray1D
        1D array of x-coordinates (offsets) in AU.
    y_offsets : DataArray1D
        1D array of y-coordinates (offsets) in AU.
    v_offsets : DataArray1D
        1D array of velocity offsets in km/s.
    data : DataArray3D
        3D data array (velocity, y, x) containing the intensity values.
    star_name : str
        Name of the star or object.
    distance_to_star : float
        Distance to the star in AU.
    v_exp : float
        Expansion velocity in km/s.
    v_sys : float
        Systemic velocity in km/s.
    beta : float
        Beta parameter of the velocity law.
    r_dust : float
        Dust formation radius in AU.
    beam_maj : float
        Major axis of the beam in degrees.
    beam_min : float
        Minor axis of the beam in degrees.
    beam_angle : float
        Beam position angle in degrees.
    header : Header
        FITS header containing metadata.
    mean : float or None, optional
        Mean intensity of the data (default is None).
    std : float or None, optional
        Standard deviation of the data (default is None).
    """
    x_offsets: DataArray1D
    y_offsets: DataArray1D
    v_offsets: DataArray1D
    data: DataArray3D
    star_name: str
    distance_to_star: float
    v_exp: float
    v_sys: float
    beta: float
    r_dust: float
    beam_maj: float
    beam_min: float
    beam_angle: float
    header: Header
    mean: float | None = None
    std: float | None = None


class StarData:

    """
    Class for manipulating and analyzing astronomical data cubes of radially expanding circumstellar envelopes.

    The StarData class provides a comprehensive interface for loading, processing, analyzing, and visualizing
    3D data cubes (typically from FITS files) representing the emission from expanding circumstellar shells.
    It supports both direct loading from FITS files and from preprocessed CondensedData objects, and manages
    all relevant metadata and derived quantities.

    Key Features
    ------------
    - **Data Loading:** Supports initialization from FITS files or CondensedData objects.
    - **Metadata Management:** Stores and exposes all relevant observational and physical parameters, including
      beam properties, systemic and expansion velocities, beta velocity law parameters, and FITS header information.
    - **Noise Estimation:** Automatically computes mean and standard deviation of background noise for filtering.
    - **Filtering:** Provides methods to filter data by significance (standard deviations) and to remove small clumps
      of points that fit within the beam (beam filtering).
    - **Coordinate Transformations:** Handles conversion between velocity space and spatial (cartesian) coordinates,
      supporting both constant velocity models and general velocity laws.
    - **Time Evolution:** Can compute the expansion of the envelope over time, transforming the data cube accordingly.
    - **Visualization:** Includes a variety of plotting methods:
        - Channel maps (2D slices through velocity channels)
        - 3D volume rendering (with Plotly)
        - Diagnostic plots for velocity/intensity and radius/velocity relationships
    - **Interactive Masking:** Supports interactive creation of masks for manual data cleaning.

    Attributes
    ----------
    data : DataArray3D
        The main data cube (v, y, x) containing intensity values.
    X : DataArray1D
        1D array of x-coordinates (offsets) in AU.
    Y : DataArray1D
        1D array of y-coordinates (offsets) in AU.
    V : DataArray1D
        1D array of velocity offsets in km/s.
    distance_to_star : float
        Distance to the star in AU.
    beam_maj : float
        Major axis of the beam in degrees.
    beam_min : float
        Minor axis of the beam in degrees.
    beam_angle : float
        Beam position angle in degrees.
    mean : float
        Mean intensity of the background noise.
    std : float
        Standard deviation of the background noise.
    v_sys : float
        Systemic velocity in km/s.
    v_exp : float
        Expansion velocity in km/s.
    beta : float
        Beta parameter of the velocity law.
    r_dust : float
        Dust formation radius in AU.
    radius : float
        Characteristic radius (e.g., maximum intensity change) in AU.
    beta_velocity_law : VelocityModel
        Callable implementing the beta velocity law with the current object's parameters.
    star_name : str
        Name of the star or object.

    Methods
    -------
    export() -> CondensedData
        Export all defining attributes to a CondensedData object.
    get_filtered_data(stds=5)
        Return a copy of the data, with values below the specified number of standard deviations set to np.nan.
    beam_filter(filtered_data)
        Remove clumps of points that fit inside the beam, setting these values to np.nan.
    get_expansion(years, v_func, ...)
        Compute the expanded data cube after a given time interval.
    plot_channel_maps(...)
        Plot the data cube as a set of 2D channel maps.
    plot_3D(...)
        Plot a 3D volume rendering of the data cube using Plotly.
    plot_velocity_vs_intensity(...)
        Plot velocity vs. intensity at the center of the xy plane.
    plot_radius_vs_intensity()
        Plot radius vs. intensity at the center of the xy plane.
    plot_radius_vs_velocity(...)
        Plot radius vs. velocity at the center of the xy plane.
    create_mask(...)
        Launch an interactive mask creator for the data cube.
    """

    _c = 299792.458  # speed of light, km/s
    v0 = 3  # km/s, speed of sound

    def __init__(
        self,
        info_source: str | CondensedData,
        distance_to_star: float | None = None,
        rest_frequency: float | None = None,
        maskfile: str | None = None,
        beta_law_params: tuple[float, float] | None = None,
        v_exp: float | None = None,
        v_sys: float | None = None,
        absolute_star_pos: tuple[float, float] | None = None
    ) -> None:
        """
        Initialize a StarData object by reading data from a FITS file or a CondensedData object.

        Parameters
        ----------
        info_source : str or CondensedData
            Path to FITS file or a CondensedData object containing preprocessed data.
        distance_to_star : float or None, optional
            Distance to the star in AU (required if info_source is a FITS file).
        rest_frequency : float or None, optional
            Rest frequency in Hz (required if info_source is a FITS file).
        maskfile : str or None, optional
            Path to a .npy file containing a mask to apply to the data.
        beta_law_params : tuple of float or None, optional
            (r_dust (AU), beta) parameters for the beta velocity law. If None, will be fit from data.
        v_exp : float or None, optional
            Expansion velocity in km/s. If None, will be fit from data.
        v_sys : float or None, optional
            Systemic velocity in km/s. If None, will be fit from data.
        absolute_star_pos : tuple of float or None, optional
            Absolute (RA, Dec) position of the star in degrees. If None, taken to be the centre of the image.

        Raises
        ------
        ValueError
            If required parameters are missing when reading from a FITS file.
        FITSHeaderError
            If any attribute in the FITS file header is an incorrect type.
        """
        if isinstance(info_source, str):
            if distance_to_star is None or rest_frequency is None:
                raise ValueError("Distance to star and rest frequency required when reading from FITS file.")
            self.__load_from_fits_file(info_source, distance_to_star, rest_frequency, absolute_star_pos, v_sys = v_sys, v_exp = v_exp)
            if beta_law_params is None:
                self._r_dust, self._beta, self._radius = self.__get_beta_law()
            else:
                self._r_dust, self._beta = beta_law_params

        else:
            # load from CondensedData
            self._X = info_source.x_offsets
            self._Y = info_source.y_offsets
            self._V = info_source.v_offsets
            self._data = info_source.data
            self.star_name = info_source.star_name
            self._distance_to_star = info_source.distance_to_star
            self._v_exp = info_source.v_exp if v_exp is None else v_exp
            self._v_sys = info_source.v_sys if v_sys is None else v_sys
            self._r_dust = info_source.r_dust if beta_law_params is None else beta_law_params[0]
            self._beta = info_source.beta if beta_law_params is None else beta_law_params[1]
            self._beam_maj = info_source.beam_maj
            self._beam_min = info_source.beam_min
            self._beam_angle = info_source.beam_angle
            self._header = info_source.header
            self.__process_beam()

            # compute mean and standard deviation
            if info_source.mean is None or info_source.std is None:
                self._mean, self._std = self.__mean_and_std()
            else:
                self._mean = info_source.mean
                self._std = info_source.std


        if maskfile is not None:
            # mask data (permanent)
            mask = np.load(maskfile)
            self._data = self._data * mask
        
    # ---- READ ONLY ATTRIBUTES ----

    @property
    def data(self) -> DataArray3D:
        """
        DataArray3D: Stores the intensity of light at each data point.
        Dimensions: k x m x n, where k is the number of frequency channels,
        m is the number of declination channels, and n is the number of right ascension channels.

        Returns
        -------
        DataArray3D
            The data cube.
        """
        return self._data

    @property
    def X(self) -> DataArray1D:
        """
        DataArray1D: Stores the x-coordinates relative to the centre in AU.
        Obtained from right ascension coordinates.

        Returns
        -------
        DataArray1D
            Array of x-coordinates (length n).
        """
        return self._X

    @property
    def Y(self) -> DataArray1D:
        """
        DataArray1D: Stores the y-coordinates relative to the centre in AU.
        Obtained from declination coordinates.

        Returns
        -------
        DataArray1D
            Array of y-coordinates (length m).
        """
        return self._Y

    @property
    def V(self) -> DataArray1D:
        """
        DataArray1D: Stores the v-coordinates relative to the star velocity in km/s.
        Obtained from frequency channels.

        Returns
        -------
        DataArray1D
            Array of velocity offsets (length k).
        """
        return self._V

    @property
    def distance_to_star(self) -> float:
        """
        Distance to star in AU.

        Returns
        -------
        float
            Distance to the star in AU.
        """
        return self._distance_to_star

    @property
    def B(self) -> Matrix2x2:
        """
        Ellipse matrix of beam. For 1x2 vectors v, w with coordinates (ra, dec) in degrees,
        if (v-w)^T B (v-w) < 1, then v is within the beam centred at w.

        Returns
        -------
        Matrix2x2
            Beam ellipse matrix.
        """
        return self._B

    @property
    def beam_maj(self) -> float:
        """
        Major axis of the beam in degrees.

        Returns
        -------
        float
            Beam major axis.
        """
        return self._beam_maj

    @property
    def beam_min(self) -> float:
        """
        Minor axis of the beam in degrees.

        Returns
        -------
        float
            Beam minor axis.
        """
        return self._beam_min

    @property
    def beam_angle(self) -> float:
        """
        Beam position angle in degrees.

        Returns
        -------
        float
            Beam position angle.
        """
        return self._beam_angle

    @property
    def mean(self) -> float:
        """
        The mean intensity of the light, taken over coordinates away from the centre.

        Returns
        -------
        float
            Mean intensity.
        """
        return self._mean

    @property
    def std(self) -> float:
        """
        The standard deviation of the intensity of the light, taken over coordinates away from the centre.

        Returns
        -------
        float
            Standard deviation.
        """
        return self._std

    @property
    def v_sys(self) -> float:
        """
        The velocity of the star in km/s.

        Returns
        -------
        float
            Systemic velocity.
        """
        return self._v_sys

    @property
    def v_exp(self) -> float:
        """
        The max radial expansion speed in km/s.

        Returns
        -------
        float
            Expansion velocity.
        """
        return self._v_exp

    @property
    def beta(self) -> float:
        """
        Beta parameter of the velocity law.

        Returns
        -------
        float
            Beta parameter.
        """
        return self._beta

    @property
    def r_dust(self) -> float:
        """
        Dust formation radius in AU.

        Returns
        -------
        float
            Dust formation radius.
        """
        return self._r_dust

    @property
    def radius(self) -> float:
        """
        Characteristic radius (e.g., maximum intensity change).

        Returns
        -------
        float
            Characteristic radius.
        """
        return self._radius

    @property
    def beta_velocity_law(self) -> VelocityModel:
        """
        Returns a callable implementing the beta velocity law with the current object's parameters.

        Returns
        -------
        VelocityModel
            Callable that takes radius (ndarray) and returns velocity (ndarray).
        """
        def law(r):
            return self.__general_beta_velocity_law(r, self.r_dust, self.beta)
        return law

    # ---- EXPORT ----

    def export(self) -> CondensedData:
        """
        Export all defining attributes to a CondensedData object.
        """
        return CondensedData(
            self.X,
            self.Y,
            self.V,
            self.data, 
            self.star_name,
            self.distance_to_star,
            self.v_exp,
            self.v_sys,
            self.beta,
            self.r_dust,
            self.beam_maj,
            self.beam_min,
            self.beam_angle,
            self._header,
            self.mean,
            self.std 
        )

    # ---- HELPER METHODS FOR INITIALISATION ----

    @staticmethod
    def __header_check(header: Header) -> bool:
        """
        Check that the FITS header contains all required values with appropriate types.

        Parameters
        ----------
        header : Header
            FITS header object to check.

        Returns
        -------
        missing_beam : bool
            True if beam parameters are missing from the header, False otherwise.

        Raises
        ------
        FITSHeaderError
            If any required attribute is present but has an incorrect type.
        """
        missing_beam = False
        types_to_check = {
            "BSCALE": float,
            "BZERO": float,
            "OBJECT": str,
            "BMAJ": float,
            "BMIN": float,
            "BPA": float,
            "BTYPE": str,
            "BUNIT": str
        }
        for num in range(1, 4):
            types_to_check["CTYPE" + str(num)] = str
            types_to_check["NAXIS" + str(num)] = int
            types_to_check["CRPIX" + str(num)] = float
            types_to_check["CRVAL" + str(num)] = float
            types_to_check["CDELT" + str(num)] = float

        # check if beam is present in data
        if "BMAJ" not in header or "BMIN" not in header or "BPA" not in header:
            missing_beam = True

        for attr in types_to_check:
            if attr in ["BMAJ", "BMIN", "BPA"] and missing_beam:
                continue
            attr_type = types_to_check[attr]
            if not type(header[attr]) is attr_type:
                raise FITSHeaderError(f"Header attribute {attr} should have type {attr_type}, instead is {type(attr)}")
        return missing_beam

    def __load_from_fits_file(
        self,
        filename: str,
        distance_to_star: float,
        rest_freq: float,
        absolute_star_pos: tuple[float, float] | None = None,
        v_sys: float | None = None,
        v_exp: float | None = None
    ) -> None:
        """
        Load data and metadata from a FITS file and initialize StarData attributes.

        Parameters
        ----------
        filename : str
            Path to the FITS file.
        distance_to_star : float
            Distance to the star in AU.
        rest_freq : float
            Rest frequency in Hz.
        absolute_star_pos : tuple of float or None, optional
            Absolute (RA, Dec) position of the star in degrees. If None, use image center.
        v_sys : float or None, optional
            Systemic velocity in km/s. If None, will be fit from data.
        v_exp : float or None, optional
            Expansion velocity in km/s. If None, will be fit from data.

        Returns
        -------
        None

        Raises
        ------
        FITSHeaderError
            If the FITS header is missing required attributes or has incorrect types.
        AssertionError
            If the FITS file does not contain data.
        """
        # read data from file
        with fits.open(filename) as hdul:
            hdu: PrimaryHDU = hdul[0] # type: ignore

            missing_beam = self.__header_check(hdu.header)  # check that all the information is available before proceeding
            self._header: Header = hdu.header
            if missing_beam:  # data is in hdul[1].data instead
                beam_data = list(hdul[1].data)

                str_to_conversion = {
                    "arcsec": 1/3600,
                    "deg": 1,
                    "degrees": 1,
                    "degree": 1
                }
                unit_maj = hdul[1].header["TUNIT1"]
                unit_min = hdul[1].header["TUNIT2"]

                # 1 arcsec = 1/3600 degree
                self._beam_maj = np.mean(np.array([beam[0] for beam in beam_data]))*str_to_conversion[unit_maj]
                self._beam_min = np.mean(np.array([beam[1] for beam in beam_data]))*str_to_conversion[unit_min]
                self._beam_angle = np.mean(np.array([beam[2] for beam in beam_data]))
            else:
                self._beam_maj = self._header["BMAJ"]
                self._beam_min = self._header["BMIN"]
                self._beam_angle = self._header["BPA"]
                
            

            brightness_scale: float = self._header["BSCALE"]  # type: ignore
            brightness_zero: float = self._header["BZERO"]  # type: ignore

            # scale data to be in specified brightness units
            assert hdu.data is not None
            self._data: DataArray3D = np.array(hdu.data[0], dtype = float64)*brightness_scale+brightness_zero  #freq, dec, ra

        self.star_name: str = self._header["OBJECT"]  # type: ignore
        self._distance_to_star = distance_to_star


        # get velocities from frequencies
        freq_range: DataArray1D = self.__get_header_array(3)
        vel_range: DataArray1D = (1/freq_range-1/rest_freq)*rest_freq*StarData._c  # velocity in km/s
        if vel_range[-1] < vel_range[0]:  # array is backwards
            vel_range = np.flip(vel_range)


        # get X and Y coordinates
        ra_vals = self.__get_header_array(1)
        dec_vals = self.__get_header_array(2)   # reverse !!
        if absolute_star_pos is None:
            ra_offsets = ra_vals - np.mean(ra_vals)
            dec_offsets = dec_vals - np.mean(dec_vals)
        else:
            ra_offsets = ra_vals - absolute_star_pos[0]
            dec_offsets = dec_vals - absolute_star_pos[1]

        self._X = ra_offsets*self.distance_to_star*np.pi/180  # measured in AU
        self._Y = dec_offsets*self.distance_to_star*np.pi/180

        self.__process_beam()

        # get mean and standard deviation of intensity values of noise
        self._mean, self._std = self.__mean_and_std()

        # get velocity offsets
        self._v_sys, self._v_exp = self.__get_star_and_exp_velocity(vel_range, v_sys = v_sys, v_exp = v_exp)
        self._V = vel_range - self.v_sys

    def __process_beam(self) -> None:
        """
        Compute the beam ellipse matrix and pixel offsets for the beam and its boundary.

        Returns
        -------
        None

        Notes
        -----
        Sets the attributes `_B`, `_offset_in_beam`, and `_boundary_offset` for use in beam-related calculations.
        """
        # get matrix for elliptical distance corresponding to beam
        major: float = float(self.beam_maj)/2  # type: ignore
        minor: float = self.beam_min/2  # type: ignore

        # degress -> radians
        theta: float = self.beam_angle*np.pi/180  # type: ignore
        R = np.array([
                [np.cos(theta), -np.sin(theta)],
                [np.sin(theta), np.cos(theta)]
        ])
        D = np.diag([1/minor, 1/major])
        self._B = R@D@D@R.T  # beam matrix: (v-w)^T B (v-w) < 1 means v is within beam centred at w
        self._offset_in_beam, self._boundary_offset = self.__pixels_in_beam(major)

    def __pixels_in_beam(self, major: float) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """
        Determine which pixel offsets are inside or on the boundary of the beam ellipse.

        Parameters
        ----------
        major : float
            Length of the major axis of the ellipse, in degrees.

        Returns
        -------
        pixels_in_beam : list of tuple of int
            List of (x, y) offsets inside the beam ellipse, relative to the center.
        pixels_on_bdry : list of tuple of int
            List of (x, y) offsets on the boundary of the beam ellipse, relative to the center.
        """
        delta_x: float = self._header["CDELT1"]  # type: ignore
        delta_y: float = self._header["CDELT2"]  # type: ignore

        bound_x: int = int(np.abs(major/delta_y) + 1)  # square to bound search in x direction
        bound_y: int = int(np.abs(major/delta_x) + 1)  # y direction

        pixels_on_bdry = []
        pixels_in_beam = []

        for x_offset in range(-bound_x, bound_x + 1):
            for y_offset in range(-bound_y, bound_y + 1):

                # get position and elliptic distance from origin
                pos = np.array([delta_x*x_offset, delta_y*y_offset])
                dist = np.sqrt(pos.T @ self.B @ pos)

                # determine if on boundary or inside ellipse
                if 1 <= dist <= 1.2:
                    pixels_on_bdry.append((x_offset, y_offset))
                elif dist < 1:
                    pixels_in_beam.append((x_offset, y_offset))

        return pixels_in_beam, pixels_on_bdry
    
    def __get_header_array(self, num: Literal[1, 2, 3]) -> DataArray1D:
        """
        Get coordinate values from the FITS header for RA, DEC, or FREQ axes.

        Parameters
        ----------
        num : {1, 2, 3}
            Axis number: 1 for RA, 2 for DEC, 3 for FREQ.

        Returns
        -------
        vals : DataArray1D
            1-D array of coordinate values for the specified axis, computed from the header.
        """
        vals_length: int = self._header["NAXIS" + str(num)]  # type: ignore
        vals: np.ndarray[tuple[int], np.dtype[np.float64]] = np.zeros(vals_length)
        x0: float = self._header["CRPIX" + str(num)]  # type: ignore
        y0: float = self._header["CRVAL" + str(num)]  # type: ignore
        delta: float = self._header["CDELT" + str(num)]  # type: ignore

        # vals[i] should be delta*(i - x0) + y0, for 1-indexing. but we are 0-indexed
        for i in range(len(vals)):
            vals[i] = delta*(i + 1 - x0) + y0

        return vals

    def __mean_and_std(self) -> tuple[float, float]:
        """
        Calculate the mean and standard deviation of the background noise, by looking at points away from the center.

        Returns
        -------
        mean : float
            Mean intensity of the background noise.
        std : float
            Standard deviation of the background noise.
        """
        # trim, as edges can be unreliable
        outer_trim = 20  # remove outer 1/20th

        frames, y_obs, x_obs = self.data.shape
        trimmed_data = self.data[:, y_obs//outer_trim:y_obs - y_obs//outer_trim, x_obs//outer_trim:x_obs - x_obs//outer_trim]
        frames, y_obs, x_obs = trimmed_data.shape
        

        # take edges of trimmed data
        inner_trim = 5  # take outer 1/5 th
        left_close = trimmed_data[:frames//inner_trim, :y_obs//inner_trim, :].flatten()
        right_close = trimmed_data[:frames//inner_trim, y_obs - y_obs//inner_trim:, :].flatten()
        top_close = trimmed_data[:frames//inner_trim, y_obs//inner_trim:y_obs - y_obs//inner_trim, :x_obs//inner_trim].flatten()
        bottom_close = trimmed_data[:frames//inner_trim, y_obs//inner_trim:y_obs - y_obs//inner_trim, x_obs-x_obs//inner_trim:].flatten()
        
        left_far = trimmed_data[frames - frames//inner_trim:, :y_obs//inner_trim, :].flatten()
        right_far = trimmed_data[frames - frames//inner_trim:, y_obs - y_obs//inner_trim:, :].flatten()
        top_far = trimmed_data[frames - frames//inner_trim:, y_obs//inner_trim:y_obs - y_obs//inner_trim, :x_obs//inner_trim].flatten()
        bottom_far = trimmed_data[frames - frames//inner_trim:, y_obs//inner_trim:y_obs - y_obs//inner_trim, x_obs-x_obs//inner_trim:].flatten()


        ring = np.concatenate((left_close, right_close, top_close, bottom_close, left_far, right_far, top_far, bottom_far))
        ring = ring[~np.isnan(ring)]

        if len(ring) < 20:
            warnings.warn("Only {len(ring)} data points selected for finding mean and standard deviation of noise.")

        mean: float = float(np.mean(ring))
        std: float = float(np.std(ring))

        return mean, std

    def __multiply_beam(self, times: float | int) -> list[tuple[int, int]]:
        """
        Generate a list of pixel offsets that represent the beam, scaled by a factor.

        Parameters
        ----------
        times : float or int
            Scaling factor for the beam size.

        Returns
        -------
        insides : list of tuple of int
            List of (x, y) offsets inside the scaled beam.
        """
        if times <= 0.0001:
            return []
        insides = []
        beam_bound = max(max([x for x, y in self._offset_in_beam]), max([y for x, y in self._offset_in_beam]))
        
        # search a square around the origin
        for x in range(-int(beam_bound*times), int(beam_bound*times) + 1):
            for y in range(-int(beam_bound*times), int(beam_bound*times) + 1):

                # check if point would shrink into beam
                pos = (int(x/times), int(y/times))
                if pos in self._offset_in_beam:
                    insides.append((x, y))

        return insides

    def __get_centre_intensities(self, beam_widths: float | int = 1) -> DataArray1D:
        """
        Calculate the mean intensity at the center of each velocity channel, averaged over a region the size of the beam.

        Parameters
        ----------
        beam_widths : float or int, optional
            Scale factor of beam (default is 1).

        Returns
        -------
        all_densities : DataArray1D
            Array of mean intensities for each velocity channel.
        """
        # centre index
        y_idx = np.argmin(self.Y**2)
        x_idx = np.argmin(self.X**2)
        beam_pixels = self.__multiply_beam(beam_widths)
        density_list = []

        # compute average density
        for v in range(len(self.data)):
            total =  0
            for x_offset, y_offset in beam_pixels:
                if 0 <= y_idx + y_offset < self.data.shape[1] and 0 <= x_idx + x_offset < self.data.shape[2]:
                    intensity = self.data[v][y_idx + y_offset][x_idx + x_offset]
                if intensity > 0 and not np.isnan(intensity):
                    total += intensity
            density_list.append(total/len(beam_pixels))

        all_densities = np.array(density_list)
        return all_densities

    def __get_star_and_exp_velocity(self, vel_range: DataArray1D, plot: bool = False, fit_parabola: bool = False, v_sys: float | None= None, v_exp: float | None = None) -> tuple[float, float]:
        """
        Computes the systemic and expansion velocities, in km/s, by fitting a parabola to the centre intensities.

        Parameters
        ----------
        vel_range : DataArray1D
            1-D array of channel velocities in km/s.
        plot : bool, optional
            If True, plot the iterative process (default is False).
        fit_parabola : bool, optional
            If True, plot a fitted parabola (default is False).
        v_sys : float or None, optional
            If provided, use this as the systemic velocity (default is None).
        v_exp : float or None, optional
            If provided, use this as the expansion velocity (default is None).

        Returns
        -------
        v_sys : float
            Systemic velocity in km/s.
        v_exp : float
            Expansion velocity in km/s.
        """
        given_v_sys = v_sys
        given_v_exp = v_exp
        if given_v_exp is not None and given_v_sys is not None:
            return given_v_sys, given_v_exp

        all_densities = self.__get_centre_intensities(2)
        
        
        v_exp_seen = np.array([])
        v_sys_seen = np.array([])

        converged = False
        densities = all_densities.copy()
        i = 1
        while not converged:  # loop until computation converges
            densities /= np.sum(densities) # normalise
            if plot:
                plt.plot(vel_range, densities, label = f"iteration {i}")
            v_sys = np.dot(densities, vel_range) if given_v_sys is None else given_v_sys

            v_exp = np.sqrt(5*np.dot(((vel_range - v_sys)**2), densities)) if given_v_exp is None else given_v_exp
            
            if any(np.isclose(v_exp_seen, v_exp)) and any(np.isclose(v_sys_seen, v_sys)):
                converged = True
            v_exp_seen = np.append(v_exp_seen, v_exp)
            v_sys_seen = np.append(v_sys_seen, v_sys)

            densities = all_densities.copy()
            densities[vel_range < (v_sys - v_exp)] = 0
            densities[vel_range > (v_sys + v_exp)] = 0
            i += 1

            if i >= 100:
                warnings.warn("Systemic and expansion velocity computation did not converge after 100 iterations.")
                break

        if plot and fit_parabola:
            parabola = (1 -((vel_range - v_sys)**2/v_exp**2))
            parabola[parabola < 0] = 0
            parabola /= np.sum(parabola)
            plt.plot(vel_range, parabola, label = "parabola")

        if plot:
            plt.title("Determining v_sys, v_exp")
            plt.xlabel("Relative velocity (km/s)")
            plt.ylabel(f"{self._header['BTYPE']} at centre point ({self._header['BUNIT']})")
            plt.legend()
            plt.show()
        
        return v_sys, v_exp

    def __get_beta_law(self, plot_intensities = False, plot_velocities = False, plot_beta_law = False) -> tuple[float, float, float]:
        """
        Fit the beta velocity law to the data and return the dust formation radius, beta parameter, and the radius of maximum intensity change.

        Parameters
        ----------
        plot_intensities : bool, optional
            If True, plot intensity vs. radius (default is False).
        plot_velocities : bool, optional
            If True, plot velocity vs. radius (default is False).
        plot_beta_law : bool, optional
            If True, plot the fitted beta law (default is False).

        Returns
        -------
        r_dust : float
            Dust formation radius.
        beta : float
            Beta parameter of the velocity law.
        radius : float
            Radius of maximum intensity change.
        """
        intensities = self.__get_centre_intensities(0.5)

        def v_from_i(i):
            return np.sqrt(1 - i/np.max(intensities))*self.v_exp
    
        centre_idx = np.argmin(self.V**2)
        frame = self.data[centre_idx]
        
        max_radius = np.minimum(np.max(self.X), np.max(self.Y))
        precision = min(len(self.X), len(self.Y))//2
        radii = np.linspace(0, max_radius, precision)
        
        X, Y = np.meshgrid(self.X, self.Y, indexing="ij")

        deltas = np.array([])
        I = np.array([])  # average intensity in each ring
        for i in range(len(radii) - 1):
            ring = frame[(radii[i]**2 <= X**2 + Y**2)  &  (X**2 + Y**2 <= radii[i+1]**2)]
            avg_intensity = np.mean(ring[np.isfinite(ring)]) 
            I = np.append(I, avg_intensity)

            inner = frame[X**2+Y**2 <= radii[i+1]**2]
            outer = frame[~(X**2+Y**2 <= radii[i+1]**2)]
            deltas = np.append(deltas,len(inner[(inner >= self.mean+5*self.std)])+len(outer[outer < self.mean+5*self.std]))

        V = v_from_i(I)
        V[~np.isfinite(V)] = 0
        R = radii[1:]
        radius_index = np.argmax(deltas)
        radius = R[radius_index]

        if plot_intensities:
            plt.plot(R, I, label = "intensities")
            plt.axvline(x = radius, label = "radius", color = "gray", linestyle = "dashed")
            plt.legend()
            plt.xlabel("Radius (AU)")
            plt.ylabel(f"Average {self._header['BTYPE']} ({self._header['BUNIT']})")
            plt.title("Average intensity at each radius")
            plt.show()
            return self.r_dust, self.beta, self.radius

        v_fit = V[(V > 0)]
        r_fit = R[(V > 0)]

        if plot_velocities:
            r_dust, beta = self.r_dust, self.beta
        else:
            params = curve_fit(self.__general_beta_velocity_law, r_fit, v_fit)[0]
            r_dust, beta =  params[0], params[1]

        if plot_velocities:
            plt.plot(R, V, label = "velocities")
            if plot_beta_law:
                LAW = self.__general_beta_velocity_law(R, r_dust, beta)
                plt.plot(R, LAW, label = "beta law")
            plt.axvline(x = radius, label = "radius", color = "gray", linestyle = "dashed")
            plt.legend()
            plt.xlabel("Radius (AU)")
            plt.ylabel(f"Velocity (km/s)")
            plt.title("Velocity at each radius")
            plt.show()
        
        return r_dust, beta, radius

    def __general_beta_velocity_law(self, r: ndarray, r_dust: float, beta: float) -> ndarray:
        """
        General beta velocity law.

        Parameters
        ----------
        r : array_like
            Radius values.
        r_dust : float
            Dust formation radius.
        beta : float
            Beta parameter.

        Returns
        -------
        v : array_like
            Velocity at each radius.
        """
        return self.v0+(self.v_exp-self.v0)*((1-r_dust/r)**beta)
    
    # ---- FILTERING DATA ----

    def get_filtered_data(self, stds: float | int = 5) -> DataArray3D:
        """
        Return a copy of the data, with values below the specified number of standard deviations set to np.nan.

        Parameters
        ----------
        stds : float or int, optional
            Number of standard deviations to filter by (default is 5).

        Returns
        -------
        filtered_data : DataArray3D
            Filtered data array.
        """
        filtered_data = self.data.copy()  # creates a deep copy
        filtered_data[filtered_data < stds*self.std] = np.nan
        return filtered_data
    
    def beam_filter(self, filtered_data: DataArray3D) -> DataArray3D:
        """
        Remove clumps of points that fit inside the beam, setting these values to np.nan.

        Parameters
        ----------
        filtered_data : DataArray3D
            3-D array with the same dimensions as the data array.

        Returns
        -------
        beam_filtered_data : DataArray3D
            3-D array with small clumps of points removed.
        """
        beam_filtered_data = filtered_data.copy()
        for frame in range(len(filtered_data)):
            for y_idx in range(len(filtered_data[frame])):
                for x_idx in range(len(filtered_data[frame][y_idx])):
                    if np.isnan(filtered_data[frame][y_idx][x_idx]):  # ignore empty points
                        continue
                    
                    # filled point that we are searching around
                
                    erase = True

                    for x_offset, y_offset in self._boundary_offset:
                        x_check = x_idx + x_offset
                        y_check = y_idx + y_offset
                        try:
                            if not np.isnan(filtered_data[frame][y_check][x_check]):
                                erase = False  # there is something present on the border - saved!
                                break
                        except IndexError:  # in case x_check, y_check are out of range
                            pass

                    if erase:  # consider ellipse to be an anomaly
                        # erase entire inside of ellipse centred at w
                        for x_offset, y_offset in self._offset_in_beam:
                            x_check = x_idx + x_offset
                            y_check = y_idx + y_offset
                            try:
                                beam_filtered_data[frame][y_check][x_check] = np.nan  # erase
                            except IndexError:
                                pass
            
        return beam_filtered_data

    # ---- HELPER METHODS FOR PLOTTING ----

    def __crop_data(self, x: DataArray1D, y: DataArray1D, v: DataArray1D, data: DataArray3D, crop_leeway: int | float = 0, fill_data: DataArray3D | None = None) -> tuple[DataArray1D, DataArray1D, DataArray1D, DataArray3D]:
        """
        Crop the data arrays to the smallest region containing all valid (non-NaN) data.

        Parameters
        ----------
        x, y, v : DataArray1D
            Small coordinate arrays.
        data : DataArray3D
            Data array to use for crop.
        crop_leeway : int or float, optional
            Fractional leeway to expand the crop region (default is 0).
        fill_data : DataArray3D or None, optional
            Data array to use for filling values (default is None).

        Returns
        -------
        cropped_x, cropped_y, cropped_v : DataArray1D
            Cropped coordinate arrays.
        cropped_data : DataArray3D
            Cropped data array.
        """
        if fill_data is None:
            fill_data = self.data
        
        v_max, y_max, x_max = data.shape 

        # gets indices
        v_indices = np.arange(v_max)
        y_indices = np.arange(y_max)
        x_indices = np.arange(x_max)

        # turn into flat arrays
        V_IDX, Y_IDX, X_IDX = np.meshgrid(v_indices, y_indices, x_indices, indexing="ij")

        # filter out nan data
        valid_V = V_IDX[~np.isnan(data)]
        valid_X = X_IDX[~np.isnan(data)]
        valid_Y = Y_IDX[~np.isnan(data)]

        # indices to crop at
        v_mid = (np.min(valid_V) + np.max(valid_V))/2
        v_lo = max(int(v_mid - (1 + crop_leeway)*(v_mid - np.min(valid_V))), 0)
        v_hi = min(int(v_mid + (1 + crop_leeway)*(np.max(valid_V) - v_mid)), len(v) - 1) + 1

        x_mid = (np.min(valid_X) + np.max(valid_X))/2
        x_lo = max(int(x_mid - (1 + crop_leeway)*(x_mid - np.min(valid_X))), 0)
        x_hi = min(int(x_mid + (1 + crop_leeway)*(np.max(valid_X) - x_mid)), len(x) - 1) + 1

        y_mid = (np.min(valid_Y) + np.max(valid_Y))/2
        y_lo = max(int(y_mid - (1 + crop_leeway)*(y_mid - np.min(valid_Y))), 0)
        y_hi = min(int(y_mid + (1 + crop_leeway)*(np.max(valid_Y) - y_mid)), len(y) - 1) + 1

        # crop x, y, v, data
        cropped_data = fill_data[v_lo:v_hi, y_lo:y_hi, x_lo:x_hi]
        cropped_v = v[v_lo: v_hi]
        cropped_y = y[y_lo: y_hi]
        cropped_x = x[x_lo: x_hi]

        return cropped_x, cropped_y, cropped_v, cropped_data

    def __filter_and_crop(
            self, 
            filter_stds: float | int | None, 
            filter_beam: bool, 
            verbose: bool
        ) -> tuple[DataArray3D, DataArray3D, DataArray3D, DataArray3D]:
        """
        Filter and crop data as specified.

        Parameters
        ----------
        filter_stds : float, int, or None
            Number of standard deviations to filter by, or None.
        filter_beam : bool
            If True, apply beam filtering.
        verbose : bool
            If True, print progress.

        Returns
        -------
        X, Y, V : DataArray3D
            Meshgrids of velocity space coordinates.
        cropped_data : DataArray3D
            Cropped and filtered data array.
        """
        if filter_stds is not None:
            if verbose:
                print("Filtering data...")
            data = self.get_filtered_data(filter_stds)
            if filter_beam:
                if verbose:
                    print("Applying beam filter...")
                data = self.beam_filter(data)
        else:
            data = self.data

        cropped_x, cropped_y, cropped_v, cropped_data = self.__crop_data(self.X,self.Y,self.V, data)

        if verbose:  
            print(f"Data cropped to shape {cropped_data.shape}")


        V, Y, X = np.meshgrid(cropped_v, cropped_y, cropped_x, indexing = "ij")
        return X, Y, V, cropped_data
    
    def __fast_interpolation(self, points: tuple, x_bounds: tuple, y_bounds: tuple, z_bounds: tuple, data: DataArray3D, v_func: VelocityModel | None, num_points: int) -> tuple[DataArray1D, DataArray1D, DataArray1D, DataArray3D]:
        """
        Interpolate the data onto a regular grid in (X, Y, Z) space.

        Parameters
        ----------
        points : tuple
            Tuple of (v, y, x) small coordinate arrays.
        x_bounds, y_bounds, z_bounds : tuple
            Bounds for the new grid in each dimension.
        data : DataArray3D
            Data array to interpolate, aligned with points.
        v_func : VelocityModel or None
            Velocity law function.
        num_points : int
            Number of points in each dimension for the new grid.

        Returns
        -------
        X, Y, Z : DataArray1D
            Flattened meshgrids of new coordinates.
        interp_data : DataArray3D
            Interpolated data array.
        """
        # points = (V, X, Y)
        new_shape = (data.shape[0] + 2, data.shape[1], data.shape[2])
        new_data = np.full(new_shape, np.nan)
        new_data[1:-1, :, :] = data.copy()  # padded on both sides with nan

        # extend v array to have out-of-range values
        v_array = points[0]
        delta_v = v_array[1] - v_array[0]
        new_v_array = np.zeros(len(v_array) + 2)
        new_v_array[1:-1] = v_array
        new_v_array[0] = new_v_array[1] - delta_v
        new_v_array[-1] = new_v_array[-2] + delta_v
        new_points = (new_v_array, points[1], points[2])

        # get points to interpolate at
        x_even = np.linspace(x_bounds[0], x_bounds[1], num=num_points)
        y_even = np.linspace(y_bounds[0], y_bounds[1], num=num_points)
        z_even = np.linspace(z_bounds[0], z_bounds[1], num=num_points)

        X, Y, Z = np.meshgrid(x_even, y_even, z_even, indexing="ij")

        # build velocities
        V = self.__to_velocity_space(X, Y, Z, v_func)

        # reset out of range values
        V[V < np.min(v_array)] = np.min(new_v_array)
        V[(V > np.max(v_array)) | ~np.isfinite(V)] = np.max(new_v_array)


        shape = V.shape
        # flatten arrays
        V = V.ravel()
        Y = Y.ravel()
        X = X.ravel()
        Z = Z.ravel()
        interp_points = np.column_stack((V, Y, X))
        interp_data = interpn(new_points, new_data, interp_points)

        interp_data[V < np.min(v_array)] = np.nan 
        interp_data[V > np.max(v_array)] = np.nan

        interp_data = interp_data.reshape(shape)

        return X, Y, Z, interp_data

    # ---- COORDINATE CHANGE ----

    def __radius_from_vel_space_coords(self, x: ndarray, y: ndarray, v: ndarray, v_func: VelocityModel) -> ndarray:
        """
        Compute the physical radius corresponding to velocity-space coordinates (x, y, v)
        using the provided velocity law.

        Parameters
        ----------
        x : ndarray
            Array of x-coordinates in AU.
        y : ndarray
            Array of y-coordinates in AU.
        v : ndarray
            Array of velocity coordinates in km/s.
        v_func : VelocityModel
            Callable velocity law, v_func(r), returning velocity in km/s for given radius in AU.

        Returns
        -------
        r : ndarray
            Array of radii in AU corresponding to the input (x, y, v) coordinates.

        Notes
        -----
        Solves for r in the equation:
            r**2 * (1 - v**2 / v_func(r)**2) = x**2 + y**2
        for each (x, y, v) triplet.
        """
        #
        assert x.shape == y.shape, f"Arrays x and y should have the same shape, instead {x.shape = }, {y.shape = }"
        assert x.shape == v.shape, f"Arrays x and v should have the same shape, instead {x.shape = }, {v.shape = }"

        shape = x.shape

        x, y, v = x.ravel(), y.ravel(), v.ravel()

        def radius_eqn(r: ndarray, x: ndarray, y: ndarray, v: ndarray):
            return r**2 * (1 - v**2/(v_func(r)**2)) - x**2 - y**2
        
        # initial bracket guess
        r_lower = np.sqrt(x**2 + y**2)  # r must be greater than sqrt(x^2 + y^2)

        # find bracket
        bracket_result = bracket_root(radius_eqn, r_lower, xmin = r_lower, args = (x, y, v))
        r_lower, r_upper = bracket_result.bracket
        result = find_root(radius_eqn, (r_lower, r_upper), args=(x, y, v))

        r: ndarray = result.x
        
        return r.reshape(shape)
        
    def __cartesian_transform(self, X: DataArray3D, Y: DataArray3D, V: DataArray3D, v_func: VelocityModel | None = None) -> tuple[DataArray3D, DataArray3D, DataArray3D]:
        """
        Transform velocity space coordinates to spatial (cartesian) coordinates.

        Parameters
        ----------
        X, Y, V : DataArray3D
            Meshgrids of coordinates in velocity space.
        v_func : VelocityModel or None, optional
            Velocity law function.

        Returns
        -------
        X, Y, Z : DataArray3D
            Meshgrids of spatial coordinates.
        """
        if v_func is None:
            # assume constant velocity of v_exp
            Z = np.sqrt(X**2+Y**2)*V/np.sqrt(self.v_exp**2-V**2)  # calculate z from x, y, v
            
        elif v_func is not None:
            # we are given the velocity in terms of the radius
            R = self.__radius_from_vel_space_coords(X, Y, V, v_func)
            Z = np.sqrt(R**2 - X**2 - Y**2) * np.sign(V)

        return X, Y, Z

    def __to_velocity_space(self, X: ndarray, Y: ndarray, Z: ndarray, v_func: VelocityModel | None) -> ndarray:
        """
        Convert spatial coordinates to velocity space using the velocity law.

        Parameters
        ----------
        X, Y, Z : array_like
            Spatial coordinates.
        v_func : VelocityModel or None
            Velocity law function.

        Returns
        -------
        V : array_like
            Velocity at each spatial coordinate.
        """
        # build velocities
        if v_func is None:
            V = self.v_exp*Z/np.sqrt(X**2 + Y**2 + Z**2)
        else:
            V = v_func(np.sqrt(X**2 + Y**2 + Z**2))*Z/np.sqrt(X**2 + Y**2 + Z**2)

        return V

    # ---- EXPANSION OVER TIME ----
    def __get_new_radius(self, curr_radius: ndarray, years: float | int, v_func: VelocityModel | None) -> ndarray:
        """
        Compute the new radius after a given time, using the velocity law.

        Parameters
        ----------
        curr_radius : ndarray
            Initial radii in AU.
        years : float or int
            Time interval in years.
        v_func : VelocityModel or None
            Velocity law function, or None (uses constant velocity).

        Returns
        -------
        new_rad : ndarray
            New radii after the specified time interval.

        Notes
        -----
        Setting v_func = None speeds this up significantly, and is a close approximation.
        """
        t = u.yr.to(u.s, years)  # t is the time in seconds
        rad_km = u.au.to(u.km, curr_radius)

        if v_func is None: 
            new_rad = u.km.to(u.au, rad_km + self.v_exp*t)
        else:

            def dr_dt(t, r):
                # need to convert r back to AU
                vals = v_func(u.km.to(u.au, r))
                vals[~np.isfinite(vals)] = 0

                return vals
            
            # flatten
            shape = rad_km.shape
            rad_km = rad_km.ravel()

            # remove nans
            nan_idxs = ~(np.isfinite(rad_km) & np.isfinite(dr_dt(0, rad_km)) & (rad_km > 0))
            valid_rad = np.min(rad_km[~nan_idxs])
            rad_km[nan_idxs] = valid_rad

            # solve
            solution = integrate.solve_ivp(dr_dt,(0,t), rad_km, vectorized=True)
            new_rad = u.km.to(u.au, solution.y[:,-1]) # r is evaluated at different time points

            # include nans and unflatten
            new_rad[nan_idxs] = np.nan
            new_rad = new_rad.reshape(shape)

        return new_rad

    def __time_expansion_transform(self, x: DataArray1D, y: DataArray1D, v: DataArray1D, data: DataArray3D, years: float | int, v_func: VelocityModel | None, crop: bool = True) -> tuple[DataArray1D, DataArray1D, DataArray1D, DataArray3D, tuple]:
        """
        Transform coordinates and data to account for expansion over time.

        Parameters
        ----------
        x, y, v : DataArray1D
            Small coordinate arrays.
        data : DataArray3D
            Data array.
        years : float or int
            Time interval in years.
        v_func : VelocityModel or None
            Velocity law function.
        crop : bool, optional
            If True, crop to finite values (default is True).

        Returns
        -------
        new_X, new_Y, new_V : DataArray1D
            Transformed coordinate arrays (flattened meshgrid).
        data : DataArray3D
            Data array (possibly cropped). Remains unchanged if crop is False.
        points : tuple
            Tuple of original (v, y, x) arrays, cropped if crop is True.
        """
        if crop:
            x, y, v, data = self.__crop_data(x, y, v, data, fill_data=data)
        
        V, X, Y = np.meshgrid(v, y, x, indexing="ij")


        if v_func is None:
            def v_func_mod(r):
                return self.v_exp
        else:
            v_func_mod = v_func

        # get R0 and R1 arrays
        R0 = self.__radius_from_vel_space_coords(X, Y, V, v_func_mod)
        R1 = self.__get_new_radius(R0, years, v_func)

        R1[R1 < 0] = np.inf  # deal with neg radii

        new_X = (X*R1/R0).ravel()
        new_Y = (Y*R1/R0).ravel()
        if v_func is None:
            new_V = V.ravel()
        else:
            new_V = (V*v_func(R1)/v_func(R0)).ravel()


        if crop:
            finite_idxs = np.isfinite(new_X) & np.isfinite(new_Y) & np.isfinite(new_V) & np.isfinite(data).ravel()
            new_X = new_X[finite_idxs]
            new_Y = new_Y[finite_idxs]
            new_V = new_V[finite_idxs]

        return new_X, new_Y, new_V, data, (v, y, x)

    def get_expansion(self, years: float | int, v_func: VelocityModel | None = None, remove_centre: float | int | None = 2, new_shape: tuple = (50, 250, 250), verbose: bool = False) -> CondensedData:
        """
        Compute the expanded data cube after a given time interval.

        Parameters
        ----------
        years : float or int
            Time interval in years.
        v_func : VelocityModel or None
            Velocity law function or None (default is None, which uses constant expansion velocity).
        remove_centre : float or int or None, optional
            If not None, remove all points within this many beam widths of the centre (default is 2).
        new_shape : tuple, optional
            Shape of the output grid (default is (50, 250, 250)).
        verbose : If True, print progress (default is False).
        
        Returns
        -------
        info : CondensedData
            CondensedData object containing the expanded data and metadata.
        """
        
        use_data = self.data.copy()
        if remove_centre is not None:
            if verbose:
                print("Removing centre...")
            # get centre coords
            y_idx = np.argmin(self.Y**2)
            x_idx = np.argmin(self.X**2)
            
            # proportion of the radius that the beam takes up
            beam_rad_au = (((self.beam_maj + self.beam_min)/2)*np.pi/180)*self.distance_to_star
            beam_prop = beam_rad_au/self.radius
            v_axis_removal = remove_centre*beam_prop*self.v_exp
            v_idxs = np.arange(len(self.V))[np.abs(self.V) < v_axis_removal]
            relevant_vs = self.V[np.abs(self.V) < v_axis_removal]
            proportions = remove_centre * np.sqrt(1 - (relevant_vs/v_axis_removal)**2)
            
            # removing centre
            for i in range(len(v_idxs)):
                v_idx = v_idxs[i]
                prop = proportions[i]
                beam = self.__multiply_beam(prop)
                for x_offset, y_offset in beam:
                    use_data[v_idx][y_idx + y_offset][x_idx + x_offset] = np.nan
        
        if verbose:
            print("Transforming coordinates...")
        X, Y, V, data, points = self.__time_expansion_transform(self.X, self.Y, self.V, use_data, years, v_func)
        v_num, y_num, x_num = new_shape

        if verbose:
            print("Generating grid for new object...")
        gridv, gridy, gridx = np.mgrid[
            np.min(V):np.max(V):v_num*1j, 
            np.min(Y):np.max(Y):y_num*1j,
            np.min(X):np.max(X):x_num*1j
        ] 


        # get preimage of grid
        small_gridx = gridx[0, 0, :]
        small_gridy = gridy[0, :, 0]
        small_gridv = gridv[:, 0, 0]

        # go backwards with negative years
        if verbose:
            print("Shrinking grid to original data bounds...")
        prev_X, prev_Y, prev_V, _, _ = self.__time_expansion_transform(small_gridx, small_gridy, small_gridv, use_data,  -years, v_func, crop = False)
        
        
        bad_idxs = (prev_V < np.min(points[0])) | (prev_V > np.max(points[0])) | \
                (prev_Y < np.min(points[1])) | (prev_Y > np.max(points[1])) | \
                (prev_X < np.min(points[2])) | (prev_X > np.max(points[2])) | \
                np.isnan(prev_V) | np.isnan(prev_X) | np.isnan(prev_Y)
        
        prev_V[bad_idxs] = 0
        prev_X[bad_idxs] = 0
        prev_Y[bad_idxs] = 0

        # interpolate regular data at these points
        if verbose:
            print("Interpolating...")
        interp_points = np.column_stack((prev_V, prev_Y, prev_X))
        interp_data = interpn(points, data, interp_points)
        interp_data[bad_idxs] = np.nan
        new_data = interp_data.reshape(gridx.shape)

        non_nans = len(new_data[np.isfinite(new_data)])
        if verbose:
            print(f"{non_nans} non-nan values remaining out of {np.size(new_data)}")

        info = CondensedData(
            small_gridx, 
            small_gridy, 
            small_gridv, 
            new_data, 
            self.star_name, 
            self.distance_to_star, 
            self.v_exp, 
            self.v_sys,
            self.beta,
            self.r_dust,
            self.beam_maj, 
            self.beam_min, 
            self.beam_angle,
            self._header,
            self.mean, 
            self.std
        )

        if verbose:
            print("Time expansion process complete!")
        return info


    # ---- PLOTTING ----

    def plot_velocity_vs_intensity(self, fit_parabola: bool = True) -> None:
        """
        Plot velocity vs. intensity at the center of the xy plane.

        Parameters
        ----------
        fit_parabola : bool, optional
            If True, fit and plot a parabola (default is True).

        Notes
        -----
        The well-fittedness of the parabola can help you visually determine 
        the accuracy of the calculated systemic and expansion velocity.
        """
        self.__get_star_and_exp_velocity(self.V, plot=True, fit_parabola=fit_parabola)

    def plot_radius_vs_intensity(self) -> None:
        """
        Plot radius vs. intensity at the center of the xy plane.
        """
        self.__get_beta_law(plot_intensities=True)

    def plot_radius_vs_velocity(self, fit_beta_law: bool = True) -> None:
        """
        Plot radius vs. velocity at the center of the xy plane.

        Parameters
        ----------
        fit_beta_law : bool, optional
            If True, fit and plot the beta law (default is True).

        Notes
        -----
        The well-fittedness of the beta law curve can help you visually determine 
        the accuracy of the calculated beta law parameters.
        """
        self.__get_beta_law(plot_velocities=True, plot_beta_law=fit_beta_law)

    def plot_channel_maps(self, 
        filter_stds: float | int | None = None, 
        filter_beam: bool = False, 
        dimensions: None | tuple[int,int] = None, 
        start: int = 0, 
        end: None | int = None, 
        include_beam: bool = True, 
        text_pos: None | tuple[float,float] = None, 
        beam_pos: None | tuple[float,float] = None, 
        title: str | None = None, 
        cmap: str = "viridis"
    ) -> None:
        """
        Plot the data cube as a set of 2D channel maps.

        Parameters
        ----------
        filter_stds : float or int or None, optional
            Number of standard deviations to filter by (default is None).
        filter_beam : bool, optional
            If True, apply beam filtering (default is False).
        dimensions : tuple of int or None, optional
            Grid dimensions (nrows, ncols) for subplots (default is None).
        start : int, optional
            Starting velocity channel index (default is 0).
        end : int or None, optional
            Ending velocity channel index (default is None).
        include_beam : bool, optional
            If True, plot the beam ellipse (default is True).
        text_pos : tuple of float or None, optional
            Position for velocity text annotation (default is None).
        beam_pos : tuple of float or None, optional
            Position for beam ellipse (default is None).
        title : str or None, optional
            Plot title (default is None, which uses the name of the star).
        cmap : str, optional
            Colormap for the plot (default is "viridis").
        """

        if end is None:
            end = self.data.shape[0]-1
        else:
            if end < start: #invalid so set to the end of the data
                end = self.data.shape[0]-1 
            if end >= self.data.shape[0]: #invalid so set to the end of the data
                end = self.data.shape[0]-1 

        if filter_stds is not None:
            data = self.get_filtered_data(filter_stds)
            if filter_beam:
                data = self.beam_filter(data)
        else:
            data = self.data
        
        if start >= data.shape[0]: #invalid so set to the start of the data
            start = 0

        if title is None:
            title = self.star_name + " channel maps"

        if dimensions is not None:
            nrows, ncols = dimensions
        else:
            nrows = int(np.ceil(np.sqrt(end-start)))
            ncols = int(np.ceil((end-start+1)/nrows))

        fig, axes = plt.subplots(nrows,ncols)
        viridis = colormaps[cmap]
        fig.suptitle(title)
        fig.supxlabel("Right Ascension (Arcseconds)")
        fig.supylabel("Declination (Arcseconds)")

        i = start
        extents = u.radian.to(u.arcsec,np.array([np.min(self.X),np.max(self.X),np.min(self.Y),np.max(self.Y)])/self.distance_to_star)
        
        done = False
        for ax in axes.flat:
            if not done:
                im = ax.imshow(data[i],vmin = self.mean, vmax = np.max(data[~np.isnan(data)]), extent=extents, cmap = cmap)

                ax.set_facecolor(viridis(0))
                ax.set_aspect("equal")

                if text_pos is None:
                    ax.text(extents[0]*5/6,extents[3]*1/2,f"{self.V[i]:.1f} km/s",size="x-small",c="white")
                else:
                    ax.text(text_pos[0],text_pos[1],f"{self.V[i]:.1f} km/s",size="x-small",c="white")

                if include_beam:
                    bmaj = u.deg.to(u.arcsec,self.beam_maj)
                    bmin = u.deg.to(u.arcsec,self.beam_min)
                    bpa = self.beam_angle

                    if beam_pos is None:
                        ellipse_artist = Ellipse(xy=(extents[0]*1/2,extents[2]*1/2),width=bmaj,height=bmin,angle=bpa,color = "white")
                    else:
                        ellipse_artist = Ellipse(xy=(beam_pos[0],beam_pos[1]),width=bmaj,height=bmin,angle=bpa, color = "white")
                    ax.add_artist(ellipse_artist)
                i += 1
                if (i >= data.shape[0]) or (i > end): done = True
            else:
                ax.axis("off")
        cbar = fig.colorbar(im, ax=axes.ravel().tolist())
        cbar.set_label("Flux Density (Jy/Beam)")
        plt.show()

    def create_mask(self, filter_stds: float | int | None = None, savefile: str | None = None, initial_crop: tuple | None = None):
        """
        Launch an interactive mask creator for the data cube.

        Parameters
        ----------
        filter_stds : float or int or None, optional
            Number of standard deviations to initially filter by (default is None).
        savefile : str or None, optional
            Filename to save the selected mask (default is None). Should end in .npy.
        initial_crop : tuple or None, optional
            Initial crop region as (v_lo, v_hi, y_lo, y_hi, x_lo, x_hi), using channel indices (default is None).
        """
        if filter_stds is not None:
            data = self.get_filtered_data(filter_stds)
        else:
            data = self.data

        if initial_crop is not None:
            v_lo, v_hi, y_lo, y_hi, x_lo, x_hi = initial_crop
            new_data = data[v_lo:v_hi, y_lo:y_hi, x_lo:x_hi]
            selector = _PointsSelector(new_data)
            plt.show()
            mask = np.full(data.shape, np.nan)
            mask[v_lo:v_hi, y_lo:y_hi, x_lo:x_hi] = selector.mask

        else:
            selector = _PointsSelector(data)
            plt.show()
        
            # mask is complete now
            mask = selector.mask
        
        # save mask
        if savefile is not None:
            np.save(savefile, mask)

    def plot_3D(
        self, 
        filter_stds: float | int | None = None, 
        filter_beam: bool = False, 
        z_cutoff: float | None = None,
        num_points: int = 50,
        num_surfaces: int = 50,
        opacity: float | int = 0.5,
        opacityscale: list[list[float]] = [[0, 0], [1, 1]],
        colorscale: str = "Reds",
        v_func: VelocityModel | None = None, 
        verbose: bool = False,
        title: str | None = None,
        folder: str | None = None,
        num_angles: int = 24,
        camera_dist: float | int = 2
    ) -> None:
        """
        Plot a 3D volume rendering of the data cube using Plotly.

        Parameters
        ----------
        filter_stds : float or int or None, optional
            Number of standard deviations to filter by (default is None).
        filter_beam : bool, optional
            If True, apply beam filtering (default is False).
        z_cutoff : float or None, optional
            Cutoff for extreme z values as a proportion of the largest x, y values (default is None).
        num_points : int, optional
            Number of points in each dimension for the grid (default is 50).
        num_surfaces : int, optional
            Number of surfaces to draw when rendering the plot (default is 50).
        opacity : float or int, optional
            Opacity of the volume rendering (default is 0.5).
        opacityscale : list of list of float, optional
            Opacity scale, see https://plotly.com/python-api-reference/generated/plotly.graph_objects.Volume.html (default is [[0, 0], [1, 1]]).
        colorscale : str, optional
            Colormap for the plot, see https://plotly.com/python/builtin-colorscales/ (default is "Reds").
        v_func : VelocityModel or None, optional
            Velocity law function (default is None, which uses constant expansion velocity).
        verbose : bool, optional
            If True, print progress (default is False).
        title : str or None, optional
            Plot title (default is None, which uses the star name).
        folder : str or None, optional
            If provided, generates successive frames and saves as png files to this folder (default is None).
        num_angles : int, optional
            Number of angles for saving images (default is 24). Greater values give smoother animation.
        camera_dist : float or int, optional
            Camera radius to use if generating frames (default is 2).
        """
        if verbose:
            print("Initial filter and crop...")
        X, Y, V, data = self.__filter_and_crop(filter_stds, filter_beam, verbose)
        
        if title is None:
            title = self.star_name

        # get small 1d arrays
        x_small = X[0, 0, :]
        y_small = Y[0, :, 0]
        v_small = V[:, 0, 0]

        if verbose:
            print("Transforming to spatial coordinates...")

        X, Y, Z = self.__cartesian_transform(X, Y, V, v_func)

        if verbose:
            print(f"Filtering z values. Found {len(Z[~np.isfinite(Z)])} invalid calculations.")
        X = X[np.isfinite(Z)]
        Y = Y[np.isfinite(Z)]
        Z = Z[np.isfinite(Z)]


        # cut off values of z if they are unwieldy
        if z_cutoff is not None:
        # filter values of z that are too high or low
            bd_hi = z_cutoff * np.maximum(np.max(X[np.isfinite(X)]), np.max(Y[np.isfinite(Y)]))
            bd_lo = z_cutoff * np.minimum(np.min(X[np.isfinite(X)]), np.min(Y[np.isfinite(Y)]))

            if verbose:
                print(f"Cutting off extreme z-values. Found {len(Z[~((bd_lo < Z) & (Z < bd_hi))])} extreme values.")

            # adjusting values
            X = X[(bd_lo < Z) & (Z < bd_hi)]
            Y = Y[(bd_lo < Z) & (Z < bd_hi)]
            Z = Z[(bd_lo < Z) & (Z < bd_hi)]


        # interpolate to grid
        if verbose:
            print("Interpolating to grid...")
        x_lo, x_hi, y_lo, y_hi, z_lo, z_hi = np.min(X), np.max(X), np.min(Y), np.max(Y), np.min(Z), np.max(Z)
        gridx, gridy, gridz, out = self.__fast_interpolation((v_small, y_small, x_small), (x_lo, x_hi), (y_lo, y_hi), (z_lo, z_hi), data, v_func, num_points)

        out[np.isnan(out)] = 0  # Plotly cant deal with nans

        # filter by standard deviation
        if filter_stds is not None:
            out[out < filter_stds*self.std] = 0

        if verbose:
            print(f"Found {len(out[out > 0])} non-nan points.")

        out = out.ravel()
        min_value = np.min(out[np.isfinite(out) & (out > 0)])

        if verbose:
            print("Plotting figure...")

        
        fig = go.Figure(
            data=go.Volume(
                x=gridx,
                y=gridy,
                z=gridz,
                value=out,
                isomin = min_value,
                colorscale= colorscale,
                colorbar = dict(title = "Flux Density (Jy/beam)"),
                opacityscale=opacityscale,
                opacity=opacity, # needs to be small to see through all surfaces
                surface_count=num_surfaces, # needs to be a large number for good volume rendering
            ),
            layout=go.Layout(
                title = {
                    "text":title,
                    "x":0.5,
                    "y":0.95,
                    "xanchor":"center",
                    "font":{"size":24}
                },
                scene = dict(
                      xaxis=dict(
                          title=dict(
                              text='X (AU)'
                          )
                      ),
                      yaxis=dict(
                          title=dict(
                              text='Y (AU)'
                          )
                      ),
                      zaxis=dict(
                          title=dict(
                              text='Z (AU)'
                          )
                      ),
                      aspectmode = "cube"
                    ),
            )
        )



        if folder is not None:
            if verbose:
                print("Generating frames...")
            angles = np.linspace(0,360,num_angles)
            for a in angles:
                b = a*np.pi/180
                eye = dict(x=camera_dist*np.cos(b),y=camera_dist*np.sin(b),z=1.25)
                fig.update_layout(scene_camera_eye = eye)
                if folder:
                    fig.write_image(f"{folder}/angle{int(a)}.png")
                else:
                    fig.write_image(f"{int(a)}.png")
                if verbose:
                    print(f"Generating frames: {a/360}% complete.")
        else:
            fig.show()
                




class _PointsSelector:

    """
    Interactive tool for selecting and masking points in a 3D data cube using matplotlib.
    """

    def __init__(self, data: DataArray3D):
        """
        Initialize the _PointsSelector with a data cube.

        Parameters
        ----------
        data : DataArray3D
            3D data array to select points from.
        """
        self.idx: int | None = None
        self.data: DataArray3D = data
        self.mask: DataArray3D = np.ones(data.shape)
        self.mask[np.isnan(data)] = np.nan
        self.num_plots: int = self.data.shape[0]
        ys = np.arange(self.data.shape[1])
        xs = np.arange(self.data.shape[2])
        X, Y = np.meshgrid(xs, ys, indexing = "ij")
        self.xys = np.column_stack((X.ravel(), Y.ravel()))
        self.width = int(np.sqrt(self.num_plots) + 1)  # ceiling of square root
        self.fig, axs = plt.subplots(self.width, self.width)

        axs = axs.flatten()
        for i in range(len(axs)):
            if i >= self.num_plots:
                axs[i].axis("off")  # turn off unnecessary axes

        self.axs = axs[:self.num_plots]

        cmap = mpl.colormaps.get_cmap('viridis').copy()
        cmap.set_bad(color='white')

        self.collections: list[AxesImage] = [None]*self.num_plots  # type: ignore
        upper = np.max(self.data[np.isfinite(self.data)])
        lower = np.min(self.data[np.isfinite(self.data)])
        for i in range(self.num_plots):
            self.collections[i] = self.axs[i].imshow(self.data[i], vmin= lower, vmax = upper, cmap = cmap)

        self.canvas = self.fig.canvas

        self.ind = []
        self.awaiting_keypress = False
        self.fig.suptitle("Double click on a subplot to start lassoing points.")
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect("key_press_event", self.key_press)

    def onclick(self, event: MouseEvent):
        """
        Handle double-click events on subplots to start lasso selection.

        Parameters
        ----------
        event : MouseEvent
            Matplotlib mouse event.
        """
        if event.dblclick:
            if event.inaxes is None:
                return
            else:
                for idx in range(len(self.axs)):
                    if event.inaxes is self.axs[idx]:
                        self.idx = idx
                        self.create_lasso()
                        return

    def key_press(self, event):
        """
        Handle key press events after lasso selection.

        Parameters
        ----------
        event : KeyEvent
            Matplotlib key event.
        """
        if self.awaiting_keypress:
            self.awaiting_keypress = False
            if event.key == "a":
                self.unmask_selection()
            elif event.key == "r":
                self.mask_selection()
            else:
                self.disconnect()

    def onselect(self, verts):
        """
        Callback for when the lasso selection is completed.

        Parameters
        ----------
        verts : list of tuple
            Vertices of the lasso path.
        """
        path = Path(verts)
        
        self.ind = self.xys[path.contains_points(self.xys)]
        self.temp_mask = np.zeros(self.data[self.idx].shape)
        for idx_pair in self.ind:
            i, j = idx_pair[0], idx_pair[1]
            self.temp_mask[j][i] = 1

        alpha = np.ones(self.temp_mask.shape)
        alpha *= 0.2
        alpha[self.temp_mask == 1] = 1
        self.collections[self.idx].set_alpha(alpha)
        self.fig.suptitle("Press R to mask points, A to mask all other points, any other key to escape.")
        self.awaiting_keypress = True
        self.fig.canvas.draw_idle()


    def create_lasso(self):
        """
        Start the lasso selector on the currently active subplot.
        """
        self.fig.suptitle("Selecting points...")
        self.fig.canvas.draw_idle()
        self.lasso = LassoSelector(self.axs[self.idx], onselect=self.onselect)

    def mask_selection(self):
        """
        Mask (set to NaN) the selected points in the current subplot.
        """
        self.mask[self.idx][self.temp_mask == 1] = np.nan
        self.collections[self.idx].set(data = self.data[self.idx]*self.mask[self.idx])
        self.disconnect()

    def unmask_selection(self):
        """
        Mask (set to NaN) all points except the selected points in the current subplot.
        """
        self.mask[self.idx][self.temp_mask != 1] = np.nan
        self.collections[self.idx].set(data = self.data[self.idx]*self.mask[self.idx])
        self.disconnect()
        

    def disconnect(self):
        """
        Disconnect the lasso selector and reset the subplot state.
        """
        self.lasso.disconnect_events()
        self.fig.suptitle("Double click on a subplot to start lassoing points.")
        alpha = np.ones(self.data[self.idx].shape)
        self.collections[self.idx].set_alpha(alpha)
        self.idx = None
        self.ind = []
        self.canvas.draw_idle()
