#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

import math
from typing import Optional

import numpy as np
from scipy import signal, stats
from scipy.fft import fft2, fftn, ifftn, ifftshift
from scipy.interpolate import CubicSpline, interp1d
from scipy.ndimage import median_filter
from scipy.optimize import minimize
from scipy.signal import find_peaks, savgol_filter


def hist_bins(values: np.ndarray, bin_size: float) -> tuple:
    """Return the bins to be used for the passed values and bin size.

    Parameters
    ----------

    values: np.ndarray
        One-dimensional array of values for which to determine the ideal histogram bins.

    bin_size: float
        Bin size to use.

    Returns
    -------

    bin_edges: np.ndarray
        Array of bin edges (to use with np.histogram()).

    bin_centers: np.ndarray
        Array of bin centers.

    bin_width:
        Bin width.
    """

    if len(values) == 0:
        raise ValueError("No data.")

    # Find an appropriate min value that keeps the bins nicely centered
    min_value = bin_size * int(np.min(values) / bin_size)

    # Max value
    max_value = np.max(values)

    # Pathological case where bin_width is 0.0
    if bin_size <= 0.0:
        raise ValueError("`bin_size` must be a positive number!")

    # Calculate number of bins
    num_bins = math.floor((max_value - min_value) / bin_size) + 1

    # Center the first bin around the min value
    half_width = bin_size / 2
    bin_edges = np.arange(
        min_value - half_width, min_value + num_bins * bin_size, bin_size
    )
    bin_centers = (bin_edges[0:-1] + bin_edges[1:]) / 2

    return bin_edges, bin_centers, bin_size


def ideal_hist_bins(values: np.ndarray, scott: bool = False):
    """Calculate the ideal histogram bins using the Freedman-Diaconis rule.

    See: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule

    Parameters
    ----------

    values: np.ndarray
        One-dimensional array of values for which to determine the ideal histogram bins.

    scott: bool
        Whether to use Scott's normal reference rule (if the data is normally distributed).

    Returns
    -------

    bin_edges: np.ndarray
        Array of bin edges (to use with np.histogram()).

    bin_centers: np.ndarray
        Array of bin centers.

    bin_size:
        Bin width.
    """

    if len(values) == 0:
        raise ValueError("No data.")

    # Pathological case, all values are the same
    if np.all(np.diff(values) == 0):
        bin_edges = (values[0] - 5e-7, values[0] + 5e-7)
        bin_centers = (values[0],)
        bin_size = 1e-6
        return bin_edges, bin_centers, bin_size

    # Calculate bin width
    factor = 2.0
    if scott:
        factor = 2.59
    iqr = stats.iqr(values, rng=(25, 75), scale=1.0, nan_policy="omit")
    num_values = np.sum(np.logical_not(np.isnan(values)))
    crn = np.power(num_values, 1 / 3)
    bin_size = (factor * iqr) / crn

    # Get min and max values
    min_value = np.min(values)
    max_value = np.max(values)

    # Pathological case where bin_size is 0.0
    if bin_size == 0.0:
        bin_size = 0.5 * (min_value + max_value)

    # Calculate number of bins
    num_bins = math.floor((max_value - min_value) / bin_size) + 1

    # Center the first bin around the min value
    half_width = bin_size / 2
    bin_edges = np.arange(
        min_value - half_width, min_value + num_bins * bin_size, bin_size
    )
    bin_centers = (bin_edges[0:-1] + bin_edges[1:]) / 2
    if len(bin_edges) >= 2:
        bin_size = bin_edges[1] - bin_edges[0]

    return bin_edges, bin_centers, bin_size


def get_robust_threshold(values: np.ndarray, factor: float = 2.0):
    """Calculate a robust threshold for the array of values.

    The threshold is defines as `median + thresh * median absolute deviation`.

    The median absolute deviation is divided by 0.67449 to bring it in the
    same scale as the (non-robust) standard deviation.

    Parameters
    ----------

    values: np.ndarray
        Array of values. It may contain NaNs.

    factor: float
        Factor by which to multiply the median absolute deviation.

    Returns
    -------

    upper_threshold: float
        Upper threshold.

    lower_threshold: float
        Lower threshold.

    med: float
        Median of the array of values.

    mad: float
        Scaled median absolute deviation of the array of values.
    """

    # Remove NaNs
    work_values = values.copy()
    work_values = work_values[np.logical_not(np.isnan(work_values))]
    if len(work_values) == 0:
        return None, None, None, None

    # Calculate robust statistics and threshold
    med = np.median(work_values)
    mad = stats.median_abs_deviation(work_values, scale=0.67449)
    step = factor * mad
    upper_threshold = med + step
    lower_threshold = med - step

    return upper_threshold, lower_threshold, med, mad


def prepare_histogram(
    values: np.ndarray,
    normalize: bool = True,
    auto_bins: bool = True,
    scott: bool = False,
    bin_size: float = 0.0,
):
    """Return histogram counts and bins for given values with provided or automatically calculated bin number.

    Parameters
    ----------

    values: np.ndarray
        Array of values. It may contain NaNs.

    normalize: bool
        Whether to normalize the histogram to a probability mass function (PMF). The integral of the PMF is 1.0.

    auto_bins: bool
        Whether to automatically calculate the bin size from the data.

    scott: bool
        Whether to use Scott's normal reference rule (the data should be normally distributed). This is used only
        if `auto_bins` is True.

    bin_size: float
        Bin size to use if `auto_bins` is False. It will be ignored if `auto_bins` is True.

    Returns
    -------

    n: np.ndarray
        Histogram counts (optionally normalized to sum to 1.0).

    bin_edges: np.ndarray
        Array of bin edges (to use with np.histogram()).

    bin_centers: np.ndarray
        Array of bin centers.

    bin_width:
        Bin width.

    """
    if auto_bins:
        bin_edges, bin_centers, bin_width = ideal_hist_bins(values, scott=scott)
    else:
        if bin_size == 0.0:
            raise Exception(
                f"Please provide a valid value for `bin_size` if `auto_bins` is False."
            )
        bin_edges, bin_centers, bin_width = hist_bins(values, bin_size=bin_size)

    n, _ = np.histogram(values, bins=bin_edges, density=False)
    if normalize:
        n = n / n.sum()
    return n, bin_edges, bin_centers, bin_width


def find_first_peak_bounds(
    counts: np.ndarray,
    bins: np.ndarray,
    min_rel_prominence: float = 0.01,
    med_filter_support: int = 5,
):
    """Finds the first peak in the histogram and return the lower and upper bounds.

    Parameters
    ----------

    counts: np.ndarray
        Array of histogram counts.

    bins: np.ndarray
        Array of histogram bins.

    min_rel_prominence: float
        Minimum relative prominences (relative to range of filtered counts) for peaks to be considered valid.

    med_filter_support: int
        Support for the median filter to suppress some spurious noisy peaks in the counts.

    Returns
    -------

    lower_bound: float
        Lower bound of the first peak.

    upper_bound: float
        Upper bound of the first peak.
    """

    # Filter the signal
    x = median_filter(counts, footprint=np.ones(med_filter_support))

    # Absolute minimum prominence
    min_prominence = min_rel_prominence * (x.max() - x.min())

    # Find maxima
    peaks, properties = find_peaks(x, prominence=(min_prominence, None))

    # Find minima
    x_inv = x.max() - x
    peaks_inv, properties_inv = find_peaks(x_inv, prominence=(min_prominence, None))

    # If we did not find any local maxima, we return failure
    if len(peaks) == 0:
        return None, None

    # First peak position
    first_peak = peaks[0]

    # If we do not have any local minima, we return the beginning and end of the bins range
    if len(peaks_inv) == 0:
        return bins[0], bins[-1]

    # Do we have a minimum on the left of the first peak?
    candidates_left = peaks_inv[peaks_inv < first_peak]
    if len(candidates_left) == 0:
        lower_bound = bins[0]
    else:
        lower_bound = bins[candidates_left[-1]]

    # Do we have a minimum on the right of the first peak?
    candidates_right = peaks_inv[peaks_inv > first_peak]
    if len(candidates_right) == 0:
        upper_bound = bins[-1]
    else:
        upper_bound = bins[candidates_right[0]]

    return lower_bound, upper_bound


def find_cutoff_near_value(
    counts: np.ndarray,
    bins: np.ndarray,
    expected_value: float,
):
    """Finds the first peak in the histogram and return the lower and upper bounds.

    Parameters
    ----------

    counts: np.ndarray
        Array of histogram counts.

    bins: np.ndarray
        Array of histogram bins.

    expected_value: float
        The cutoff is expected to be close to the expected value.

    Returns
    -------

    cutoff: float
        Estiated cutoff frequency.
    """

    # Absolute minimum prominence
    min_prominence = 0.05 * (counts.max() - counts.min())

    # Find minima
    counts_inv = counts.max() - counts
    peaks_inv, properties_inv = find_peaks(
        counts_inv, prominence=(min_prominence, None)
    )

    # Which is the local minimum closest to the expected value
    cutoff_pos = peaks_inv[np.argmin(np.abs(bins[peaks_inv] - expected_value))]

    # Extract the corresponding frequency
    cutoff = bins[cutoff_pos]

    # Return the obtained cutoff frequency
    return cutoff


def calculate_density_map(
    x: np.ndarray,
    y: np.ndarray,
    x_bin_edges: Optional[np.ndarray] = None,
    y_bin_edges: Optional[np.ndarray] = None,
    auto_bins: bool = True,
    scott: bool = False,
    bin_size: Optional[float] = None,
) -> np.ndarray:
    """Create density map for 2D data.

    Parameters
    ----------

    x: np.ndarray
        1D array of X values.

    y: np.ndarray
        1D array of Y values.

    x_bin_edges: np.ndarray
        1D array of bin edge values for the X array. If omitted, it will be calculated automatically
        (see `pyminflux.analysis.prepare_histogram`.)

    y_bin_edges: np.ndarray
        1D array of bin edge values for the X array. If omitted, it will be calculated automatically
        (see `pyminflux.analysis.prepare_histogram`.)

    auto_bins: bool
        Whether to automatically calculate the bin size from the data. Only used if either `x_bin_edges`
        or `y_bin_edges` are None.

    scott: bool
        Whether to use Scott's normal reference rule (the data should be normally distributed).
        This is only used if either `x_bin_edges` or `y_bin_edges` are None and `auto_bins` is True.

    bin_size: float
        Bin size to use if either `x_bin_edges` or `y_bin_edges` are None and `auto_bins` is False.
        It will be ignored if `auto_bins` is True.

    Returns
    -------

    density: np.ndarray
        2D density maps.
    """

    # Calculate bin edges if needed
    if x_bin_edges is None:
        _, x_bin_edges, _, _ = prepare_histogram(
            x, auto_bins=auto_bins, scott=scott, bin_size=bin_size
        )

    if y_bin_edges is None:
        _, y_bin_edges, _, _ = prepare_histogram(
            y, auto_bins=auto_bins, scott=scott, bin_size=bin_size
        )

    # Create density map
    xx, yy = np.meshgrid(x_bin_edges, y_bin_edges)
    positions = np.vstack([xx.ravel(), yy.ravel()])
    values = np.vstack([x, y])
    kernel = stats.gaussian_kde(values)
    density = np.reshape(kernel(positions).T, xx.shape)

    # Return density map
    return density


def calculate_2d_histogram(
    x: np.ndarray,
    y: np.ndarray,
    x_bin_edges: Optional[np.ndarray] = None,
    y_bin_edges: Optional[np.ndarray] = None,
    x_auto_bins: bool = True,
    y_auto_bins: bool = True,
    scott: bool = False,
    x_bin_size: float = 0.0,
    y_bin_size: float = 0.0,
) -> np.ndarray:
    """Create density map for 2D data.

    Parameters
    ----------

    x: np.ndarray
        1D array of X values.

    y: np.ndarray
        1D array of Y values.

    x_bin_edges: np.ndarray
        1D array of bin edge values for the X array. If omitted, it will be calculated automatically
        (see `pyminflux.analysis.prepare_histogram`.)

    y_bin_edges: np.ndarray
        1D array of bin edge values for the X array. If omitted, it will be calculated automatically
        (see `pyminflux.analysis.prepare_histogram`.)

    x_auto_bins: bool
        Whether to automatically calculate the bin size for `x` from the data. Only used if `x_bin_edges`
        is None.

    y_auto_bins: bool
        Whether to automatically calculate the bin size for `y` from the data. Only used if `y_bin_edges`
        is None.

    scott: bool
        Whether to use Scott's normal reference rule (the data should be normally distributed).
        This is only used if either `x_bin_edges` or `y_bin_edges` are None and `auto_bins` is True.

    x_bin_size: float
        Bin size to use for `x` if `x_bin_edges` is None and `x_auto_bins` is False.
        It will be ignored if `x_auto_bins` is True.

    y_bin_size: float
        Bin size to use for `y` if `y_bin_edges` is None and `y_auto_bins` is False.
        It will be ignored if `y_auto_bins` is True.

    Returns
    -------

    density: np.ndarray
        2D density maps.
    """

    # Calculate bin edges if needed
    if x_bin_edges is None:
        _, x_bin_edges, _, _ = prepare_histogram(
            x, auto_bins=x_auto_bins, scott=scott, bin_size=x_bin_size
        )

    if y_bin_edges is None:
        _, y_bin_edges, _, _ = prepare_histogram(
            y, auto_bins=y_auto_bins, scott=scott, bin_size=y_bin_size
        )

    # Create 2D histogram
    histogram = np.histogram2d(y, x, bins=(y_bin_edges, x_bin_edges))

    # Return histogram
    return histogram[0]


def get_localization_boundaries(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    alpha: float = 0.01,
    min_range: float = 200.0,
):
    """Return x, y, and z localization boundaries for analysis.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100


    Parameters
    ----------

    x: np.ndarray
        Array of localization x coordinates.

    y: np.ndarray
        Array of localization y coordinates.

    z: np.ndarray
        Array of localization z coordinates.

    alpha: float (default = 0.01)
        Quantile to remove outliers. Must be 0.0 <= alpha <= 0.5.

    min_range: float (default = 200.0)
        Absolute minimum range in nm.

    Returns
    -------

    rx: tuple
        (min, max) boundaries for the x coordinates.

    ry: float
        (min, max) boundaries for the y coordinates.

    rz: float
        (min, max) boundaries for the z coordinates.
    """

    if alpha < 0 or alpha >= 0.5:
        raise ValueError("alpha must be 0 < alpha < 0.5.")

    # Make sure we are working with NumPy arrays
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    # Get boundaries at the given alpha level
    rx = np.quantile(x, (alpha, 1 - alpha))
    ry = np.quantile(y, (alpha, 1 - alpha))
    rz = np.quantile(z, (alpha, 1 - alpha))

    # Minimal boundaries in case of drift correction
    d_rx = float(np.diff(rx)[0])
    if d_rx < min_range:
        rx = rx + (min_range - d_rx) / 2 * np.array([-1, 1])

    d_ry = float(np.diff(ry)[0])
    if d_ry < min_range:
        ry = ry + (min_range - d_ry) / 2 * np.array([-1, 1])

    d_rz = float(np.diff(rz)[0])
    if min_range > d_rz > 1e-6:  # Only in the 3D case
        rz = rz + (min_range - d_rz) / 2 * np.array([-1, 1])

    return rx, ry, rz


def render_xy(
    x,
    y,
    sx: float = 1.0,
    sy: float = 1.0,
    rx: Optional[tuple] = None,
    ry: Optional[tuple] = None,
    render_type: Optional[str] = "histogram",
    fwhm: Optional[float] = None,
):
    """Renders the localizations as a 2D image with given resolution.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    x: np.ndarray
        Array of localization x coordinates.

    y: np.ndarray
        Array of localization y coordinates.

    sx: float (Default = 1.0)
        Resolution of the render in the x direction.

    sy: float (Default = 1.0)
        Resolution of the render in the y direction.

    rx: tuple (Optional)
        (min, max) boundaries for the x coordinates. If omitted, it will default to (x.min(), x.max()).

    ry: float (Optional)
        (min, max) boundaries for the y coordinates. If omitted, it will default to (y.min(), y.max()).

    render_type: str (Default = "histogram")
        Type of render to be generated. It must be one of:
            "histogram": simple 2D histogram of localization falling into each bin of size (sx, sy).
            "fixed_gaussian": sub-pixel resolution Gaussian fit. The Gaussian full-width half maximum is required
            (see below).

    fwhm: float (Optional)
        Requested full-width half maximum (FWHM) of the Gaussian kernel. If omitted, it is set to be
        3 * np.sqrt(np.power(sx, 2) + np.power(sy, 2)).

    Returns
    -------

    h: np.ndarray
        Rendered image (as float32 2D NumPy array)
    xi: np.ndarray
        Array of x coordinates for the output x, y grid
    yi: np.ndarray
        Array of x coordinates for the output x, y grid
    m: np.ndarray
        Logical array with the positions that were considered. The False entries were rejected because they were
        outside the rx, ry ranges (with the additional constraint of the edge effect of the Gaussian support for
        the "fixed_gaussian" render type.
    """

    if render_type is None:
        render_type = "histogram"

    render_type = render_type.lower()
    if render_type not in ["histogram", "fixed_gaussian"]:
        raise ValueError("plot_type must be one of 'histogram' or 'fixed_gaussian'.'")

    if render_type == "fixed_gaussian" and fwhm is None:
        sxy = np.sqrt(np.power(sx, 2) + np.power(sy, 2))
        fwhm = 3 * sxy

    # Make sure we are working with NumPy arrays
    x = np.array(x)
    y = np.array(y)

    # Make sure rx and ry are defined
    if rx is None:
        rx = (x.min(), x.max())
    if ry is None:
        ry = (y.min(), y.max())

    # Get dimensions and allocate output array
    Nx = int(np.ceil((rx[1] - rx[0]) / sx))
    Ny = int(np.ceil((ry[1] - ry[0]) / sy))
    h = np.zeros((Ny, Nx), dtype=np.float32)

    # Get position in pixels
    px = (x - rx[0]) / sx
    py = (y - ry[0]) / sy

    # Convert absolute position to image indices
    ix = np.round(px).astype(int)
    iy = np.round(py).astype(int)

    # Remove positions outside the image
    m = (ix >= 0) & (ix < Nx) & (iy >= 0) & (iy < Ny)
    px = px[m]
    py = py[m]
    ix = ix[m]
    iy = iy[m]

    # Plot requested image type
    if render_type == "histogram":
        # Fill in histogram
        for i in range(len(ix)):
            xi = ix[i]
            yi = Ny - iy[i] - 1  # Images have y = 0 at the top
            try:
                h[yi, xi] += 1
            except IndexError as e:
                print(
                    f"Tried to access (y={yi}, x={xi}) in image of size (Ny={Ny}, Nx={Nx})."
                )

    elif render_type == "fixed_gaussian":
        # Gaussian with subpixel accuracy
        wx = fwhm / sx
        wy = fwhm / sy
        L = int(np.ceil(2 * max(wx, wy)))

        # Small grid
        g = np.arange(-L, L + 1)
        yk, xk = np.meshgrid(g, g)

        # Remove close to borders
        m = (ix >= L) & (ix < Nx - L) & (iy >= L) & (iy < Ny - L)
        px = px[m]
        py = py[m]
        ix = ix[m]
        iy = iy[m]

        for i in range(len(ix)):
            xi = ix[i]
            yi = iy[i]
            dx = px[i] - xi
            dy = py[i] - yi
            gx = xi + g
            gy = yi + g

            # Calculate the Gaussian kernel using the requested FWHM.
            k = np.exp(
                -4 * np.log(2) * ((xk - dx) ** 2 / wx**2 + (yk - dy) ** 2 / wy**2)
            )

            # Add it to the image
            my, mx = np.meshgrid(
                gy, gx, indexing="ij"
            )  # We need to create meshgrid to add the k matrix
            my = Ny - my - 1  # Images have y = 0 at the top
            try:
                h[my, mx] = h[my, mx] + k
            except IndexError as e:
                print(
                    f"Tried to access (y={yi}, x={xi}) in image of size (Ny={Ny}, Nx={Nx})."
                )

    else:
        raise ValueError("Unknown type")

    # Define output xy grid
    xi = rx[0] + (np.arange(Nx)) * sx + sx / 2
    yi = ry[0] + (np.arange(Ny)) * sy + sy / 2

    return h, xi, yi, m


def render_xyz(
    x,
    y,
    z,
    sx: float = 1.0,
    sy: float = 1.0,
    sz: float = 1.0,
    rx: Optional[tuple] = None,
    ry: Optional[tuple] = None,
    rz: Optional[tuple] = None,
    render_type: Optional[str] = "histogram",
    fwhm: Optional[float] = None,
):
    """Renders the localizations as a 3D stack with given resolution.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    x: np.ndarray
        Array of localization x coordinates.

    y: np.ndarray
        Array of localization y coordinates.

    z: np.ndarray
        Array of localization z coordinates.

    sx: float (Default = 1.0)
        Resolution of the render in the x direction.

    sy: float (Default = 1.0)
        Resolution of the render in the y direction.

    sz: float (Default = 1.0)
        Resolution of the render in the z direction.

    rx: tuple (Optional)
        (min, max) boundaries for the x coordinates. If omitted, it will default to (x.min(), x.max()).

    ry: float (Optional)
        (min, max) boundaries for the y coordinates. If omitted, it will default to (y.min(), y.max()).

    rz: float (Optional)
        (min, max) boundaries for the z coordinates. If omitted, it will default to (z.min(), z.max()).

    render_type: str (Default = "histogram")
        Type of render to be generated. It must be one of:
            "histogram": simple 2D histogram of localization falling into each bin of size (sx, sy).
            "fixed_gaussian": sub-pixel resolution Gaussian fit. The Gaussian full-width half maximum is required
            (see below).

    fwhm: float (Optional)
        Requested full-width half maximum (FWHM) of the Gaussian kernel. If omitted, it is set to be
        3 * np.sqrt(np.power(sx, 2) + np.power(sy, 2)).

    Returns
    -------

    h: np.ndarray
        Rendered image (as float32 2D NumPy array)
    xi: np.ndarray
        Array of x coordinates for the output x, y grid
    yi: np.ndarray
        Array of x coordinates for the output x, y grid
    m: np.ndarray
        Logical array with the positions that were considered. The False entries were rejected because they were
        outside the rx, ry ranges (with the additional constraint of the edge effect of the Gaussian support for
        the "fixed_gaussian" render type.
    """

    if render_type is None:
        render_type = "histogram"

    render_type = render_type.lower()
    if render_type not in ["histogram", "fixed_gaussian"]:
        raise ValueError("plot_type must be one of 'histogram' or 'fixed_gaussian'.'")

    if render_type == "fixed_gaussian" and fwhm is None:
        sxyz = np.sqrt(np.power(sx, 2) + np.power(sy, 2) + np.power(sz, 2))
        fwhm = 3 * sxyz

    # Make sure we are working with NumPy arrays
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    # Make sure rx and ry are defined
    if rx is None:
        rx = (x.min(), x.max())
    if ry is None:
        ry = (y.min(), y.max())
    if rz is None:
        rz = (z.min(), z.max())

    # Get dimensions and allocate output array
    Nx = int(np.ceil((rx[1] - rx[0]) / sx))
    Ny = int(np.ceil((ry[1] - ry[0]) / sy))
    Nz = int(np.ceil((rz[1] - rz[0]) / sz))
    h = np.zeros((Nz, Ny, Nx), dtype=np.float32)

    # Get position in pixels
    px = (x - rx[0]) / sx
    py = (y - ry[0]) / sy
    pz = (z - rz[0]) / sz

    # Convert absolute position to image indices
    ix = np.round(px).astype(int)
    iy = np.round(py).astype(int)
    iz = np.round(pz).astype(int)

    # Remove positions outside the image
    m = (ix >= 0) & (ix < Nx) & (iy >= 0) & (iy < Ny) & (iz >= 0) & (iz < Nz)
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Plot requested image type
    if render_type == "histogram":
        # Fill in histogram
        for i in range(len(ix)):
            xi = ix[i]
            yi = Ny - iy[i] - 1  # Images have y = 0 at the top
            zi = iz[i]
            try:
                h[zi, yi, xi] += 1
            except IndexError as e:
                print(
                    f"Tried to access (z={zi}, y={yi}, x={xi}) in image of size (Nz={Nz}, Ny={Ny}, Nx={Nx})."
                )

    elif render_type == "fixed_gaussian":
        # Gaussian with subpixel accuracy
        wx = fwhm / sx
        wy = fwhm / sy
        wz = fwhm / sz
        L = int(np.ceil(2 * max(wx, wy, wz)))

        # Small grid
        g = np.arange(-L, L + 1)
        zk, yk, xk = np.meshgrid(g, g, g, indexing="ij")

        # Remove close to borders
        m = (
            (ix >= L)
            & (ix < Nx - L)
            & (iy >= L)
            & (iy < Ny - L)
            & (iz >= L)
            & (iz < Nz - L)
        )
        px = px[m]
        py = py[m]
        pz = pz[m]
        ix = ix[m]
        iy = iy[m]
        iz = iz[m]

        for i in range(len(ix)):
            xi = ix[i]
            yi = iy[i]
            zi = iz[i]
            dx = px[i] - xi
            dy = py[i] - yi
            dz = pz[i] - zi
            gx = xi + g
            gy = yi + g
            gz = zi + g

            # Calculate the Gaussian kernel using the requested FWHM.
            k = np.exp(
                -4
                * np.log(2)
                * (
                    (xk - dx) ** 2 / wx**2
                    + (yk - dy) ** 2 / wy**2
                    + (zk - dz) ** 2 / wz**2
                )
            )

            # Add it to the image
            mz, my, mx = np.meshgrid(
                gz, gy, gx, indexing="ij"
            )  # We need to create meshgrid to add the k matrix
            my = Ny - my - 1  # Images have y = 0 at the top
            try:
                h[mz, my, mx] = h[mz, my, mx] + k
            except IndexError as e:
                print(
                    f"Tried to access (y={yi}, x={xi}) in image of size (Ny={Ny}, Nx={Nx})."
                )

    else:
        raise ValueError("Unknown type")

    # Define output xy grid
    xi = rx[0] + (np.arange(Nx)) * sx + sx / 2
    yi = ry[0] + (np.arange(Ny)) * sy + sy / 2
    zi = rz[0] + (np.arange(Nz)) * sz + sz / 2

    return h, xi, yi, zi, m


def img_fourier_grid(dims, dtype=float):
    """This grid has center of mass at (0, 0): if used to perform convolution via fft2, it will not produce any shift!

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    dims: tuple
        Size in each dimension.
        For 1D, dims = [nx]
        For 2D, dims = [nx, ny]
        For 3D, dims = [nx, ny, nz]

    dtype: np.dtype (Optional, default float = np.float64)
        Data type of the grid.

    Returns

    x: np.ndarray
        Linear grid of coordinates if ndims == 1.
        2D mesh grid of coordinates if ndims == 2.
        3D mesh grid of coordinates if ndims == 3.

    y: np.ndarray
        2D mesh grid of coordinates if ndims == 2.
        3D mesh grid of coordinates if ndims == 3.

    z: np.ndarray
        3D mesh grid of coordinates if ndims == 3.
    """

    number_dimensions = len(dims)

    if number_dimensions == 1:
        gx = np.arange(1, dims[0] + 1).astype(dtype)
        xi = ifftshift(gx)
        xi = xi - xi[0]
        return xi

    elif number_dimensions == 2:
        gx = np.arange(1, dims[0] + 1).astype(dtype)
        gy = np.arange(1, dims[1] + 1).astype(dtype)
        xi, yi = np.meshgrid(gx, gy, indexing="ij")
        xi = ifftshift(xi)
        xi = xi - xi[0, 0]
        yi = ifftshift(yi)
        yi = yi - yi[0, 0]
        return xi, yi

    elif number_dimensions == 3:
        gx = np.arange(1, dims[0] + 1).astype(dtype)
        gy = np.arange(1, dims[1] + 1).astype(dtype)
        gz = np.arange(1, dims[2] + 1).astype(dtype)
        xi, yi, zi = np.meshgrid(gx, gy, gz, indexing="ij")
        xi = ifftshift(xi)
        xi = xi - xi[0, 0, 0]
        yi = ifftshift(yi)
        yi = yi - yi[0, 0, 0]
        zi = ifftshift(zi)
        zi = zi - zi[0, 0, 0]
        return xi, yi, zi

    else:
        raise ValueError("Unsupported dimensionality!")


def img_fourier_ring_correlation(
    image1, image2, sx: float = 1.0, sy: float = 1.0, frc_smoothing_kernel=None
):
    """Perform Fourier ring correlation analysis on two images and returns the estimated resolution in m.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    image1: np.ndarray
        First image, possibly generated by `pyminflux.analysis.render_xy()`.

    image2: np.ndarray
        Second image, possibly generated by `pyminflux.analysis.render_xy()`.

    physical_image_size: tuple (sy, sz)
        Physical size of the image.

    sx: float (Default = 1.0 nm)
        Resolution in nm of the rendered image in the x direction.

    sy: float (Default = 1.0 nm)
        Resolution in nm of the rendered image in the y direction.

    render_type: np.ndarray (Optional)
        2D kernel for low-pass filtering the FRC. If omitted, a 31x31 Gaussian kernel with sigma = 1.0 will be used.

    Returns
    -------

    estimated_resolution: float
        Estimated image resolution in m.

    fc: np.ndarray
        @TODO Add description

    qi: np.ndarray
        Array of frequencies.

    ci: np.ndarray
        Array of Fourier Ring Correlations (corresponding to the frequencies in qi)
    """

    def bin_data(qi, data):
        """Perform binning operation."""
        real = np.bincount(qi, weights=data.flatten().real)
        imag = np.bincount(qi, weights=data.flatten().imag)
        return real + 1j * imag

    if frc_smoothing_kernel is None:
        frc_smoothing_kernel = np.outer(
            signal.gaussian(31, std=1), signal.gaussian(31, std=1)
        )

    # Physical size of the image (in meters!)
    physical_image_size = (image1.shape[0] * sy * 1e-9, image1.shape[1] * sx * 1e-9)

    # Calculate Fourier transforms
    f1 = fft2(image1)
    f2 = fft2(image2)

    # Calculate derived quantities for correlation
    a = f1 * np.conj(f2)
    b = f1 * np.conj(f1)
    c = f2 * np.conj(f2)

    # 2D image representation (first smooth, then real/absolute value)
    a_sm = signal.fftconvolve(ifftshift(a), frc_smoothing_kernel, mode="same")
    b_sm = signal.fftconvolve(ifftshift(b), frc_smoothing_kernel, mode="same")
    c_sm = signal.fftconvolve(ifftshift(c), frc_smoothing_kernel, mode="same")
    fc = a_sm / np.sqrt(b_sm * c_sm)
    fc = np.real(fc)

    # Calculate frequency space grid
    qx, qy = img_fourier_grid(image1.shape)
    qx = qx / physical_image_size[0]
    qy = qy / physical_image_size[1]
    q = np.sqrt(qx**2 + qy**2)

    # Calculate bin a, b, c in dependence of q
    B = 5e5  # bin size (in pixel in fourier space)  # @TODO must be adapted to physical stack size (this is in m)!!
    qi = np.round(q / B).astype(int)
    idx = qi.flatten()  # + 1
    qi = np.arange(0, np.max(qi) + 1) * B
    aj = bin_data(idx, a)
    bj = bin_data(idx, b)
    cj = bin_data(idx, c)
    ci = np.real(aj / np.sqrt(bj * cj))
    idx = qi < np.max(qi) * 0.8  # cut a bit
    qi = qi[idx]
    ci = ci[idx]

    # Additional smoothing
    ci = savgol_filter(ci, 7, 1)

    # Determine image resolution (in m)
    q_critical = qi[np.where(ci < 1 / 7)[0][0]] if np.any(ci < 1 / 7) else qi[-1]
    estimated_resolution = 1 / q_critical

    return estimated_resolution, fc, qi, ci


def estimate_resolution_by_frc(
    x: np.ndarray,
    y: np.ndarray,
    num_reps: int = 5,
    sx: float = 1.0,
    sy: float = 1.0,
    rx: Optional[tuple] = None,
    ry: Optional[tuple] = None,
    render_type: str = "histogram",
    fwhm: Optional[float] = None,
    seed: Optional[int] = None,
    return_all: bool = False,
):
    """Estimates signal resolution by averaging the results of Fourier Ring Correlation the required number of times.

    Parameters
    ----------

    x: np.ndarray
        Array of localization x coordinates.

    y: np.ndarray
        Array of localization y coordinates.

    num_reps: int (Default = 5)
        Number of time Fourier Ring Correlation analysis is run. The returned result will be  the average of the runs.

    sx: float (Default = 1.0)
        Resolution of the render in the x direction.

    sy: float (Default = 1.0)
        Resolution of the render in the y direction.

    rx: tuple (Optional)
        (min, max) boundaries for the x coordinates. If omitted, it will default to (x.min(), x.max()).

    ry: float (Optional)
        (min, max) boundaries for the y coordinates. If omitted, it will default to (y.min(), y.max()).

    render_type: str (Default = "histogram")
        Type of render to be generated. It must be one of:
            "histogram": simple 2D histogram of localization falling into each bin of size (sx, sy).
            "fixed_gaussian": sub-pixel resolution Gaussian fit. The Gaussian full-width half maximum is required
            (see below).

    fwhm: float (Optional)
        Requested full-width half maximum (FWHM) of the Gaussian kernel. If omitted, it is set to be
        3 * np.sqrt(np.power(sx, 2) + np.power(sy, 2)).

    seed: Optional[int]
        Seed for the random number generator if comparable runs are needed.

    return_all: bool (Default = False)
        Set to True to return all measurements along with their averages.

    Returns
    -------

    resolution: float
        Estimated resolution in nm (average over `num_reps`).

    qi: np.ndarray
        Array of frequencies.

    ci: np.ndarray
        Array of Fourier Ring Correlations (corresponding to the frequencies in qi)

    resolutions: np.ndarray (num_reps, )
        Each of the estimated `n_reps` resolutions. Only returned if `return_all` is True.

    cis: np.ndarray (:, n_reps)
        Array of Fourier Ring Correlations (corresponding to the frequencies in qi) for each of the `n_reps` runs.
        Only returned if `return_all` is True.
    """

    if seed is not None:
        # Initialize the random number generator
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    # Make sure we are working with NumPy arrays
    x = np.array(x)
    y = np.array(y)

    # Make sure to have the same ranges rx and ry bot both images
    if rx is None or ry is None:
        rx = (x.min(), x.max())
        ry = (y.min(), y.max())

    resolutions = np.zeros(num_reps)
    cis = None
    qi = None
    for r in range(num_reps):
        # Partition the data
        ix = rng.random(size=x.shape) < 0.5
        c_ix = np.logical_not(ix)

        # Create two images from (complementary) subsets of coordinates (x, y)
        h1 = render_xy(
            x[ix], y[ix], sx=sx, sy=sy, rx=rx, ry=ry, render_type=render_type, fwhm=fwhm
        )[0]
        h2 = render_xy(
            x[c_ix],
            y[c_ix],
            sx=sx,
            sy=sy,
            rx=rx,
            ry=ry,
            render_type=render_type,
            fwhm=fwhm,
        )[0]

        # Estimate the resolution using Fourier Ring Correlation
        estimated_resolution, fc, qi, ci = img_fourier_ring_correlation(
            h1, h2, sx=sx, sy=sy
        )

        # Store the estimated resolution, qis and cis
        resolutions[r] = estimated_resolution
        if cis is None:
            cis = np.zeros((len(ci), num_reps), dtype=float)
        cis[:, r] = ci

    # Now calculate average values
    resolution = np.mean(resolutions)
    ci = np.mean(cis, axis=1)

    # Return
    if return_all:
        return resolution, qi, ci, resolutions, cis
    else:
        return resolution, qi, ci


def drift_correction_time_windows_2d(
    x: np.ndarray,
    y: np.ndarray,
    t: np.ndarray,
    sxy: float,
    rx: Optional[tuple] = None,
    ry: Optional[tuple] = None,
    T: Optional[float] = None,
    tid: Optional[np.ndarray] = None,
):
    """Estimate 2D drift correction based on auto-correlation.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    x: np.ndarray
        Array of localization x coordinates.

    y: np.ndarray
        Array of localization y coordinates.

    t: np.ndarray
        Array of localization time points.

    sxy: float (Default = 1.0)
        Resolution in nm in both the x and y direction.

    rx: tuple (Optional)
        (min, max) boundaries for the x coordinates. If omitted, it will default to (x.min(), x.max()).

    ry: float (Optional)
        (min, max) boundaries for the y coordinates. If omitted, it will default to (y.min(), y.max()).

    T: float (Optional)
        Time window for analysis.

    tid: np.ndarray (Optional)
        Only used if T is None. The unique trace IDs are used to calculate the time window for
        analysis using some heuristics.
    """

    if T is None and tid is None:
        raise ValueError("If T is not defined, the array of TIDs must be provided.")

    # Make sure we are working with NumPy arrays
    x = np.array(x)
    y = np.array(y)
    t = np.array(t)
    if tid is not None:
        tid = np.array(tid)

    # Make sure we have valid ranges
    if rx is None:
        rx = (x.min(), x.max())

    if ry is None:
        ry = (y.min(), y.max())

    # Heuristics to define the length of the time window
    if T is None:
        rt = (t[0], t[-1])
        T = len(np.unique(tid)) * np.diff(rx)[0] * np.diff(ry)[0] / 3e6
        T = np.min([T, np.diff(rt)[0] / 2, 3600])  # At least two time windows
        T = max([T, 600])  # And at least 10 minutes long

    # Number of time windows to use
    Rt = [t[0], t[-1]]
    Ns = int(np.floor((Rt[1] - Rt[0]) / T))  # total number of time windows
    assert Ns > 1, "At least two time windows are needed, please reduce T"

    # Center of mass
    CR = 10

    # Maximum number of frames in the cross-correlation
    D = Ns

    # Weight with distance
    w = np.linspace(1, 0.5, D)

    # Regularization term (roughness)
    l = 0.1

    # get dimensions
    Nx = int(np.ceil((rx[1] - rx[0]) / sxy))
    Ny = int(np.ceil((ry[1] - ry[0]) / sxy))
    c = np.round(np.array([Ny, Nx]) / 2)

    # Create all the histograms
    h = [None] * Ns
    ti = np.zeros(Ns)  # Average times of the snapshots
    for j in range(Ns):
        t0 = Rt[0] + j * T
        idx = (t >= t0) & (t < t0 + T)
        ti[j] = np.mean(t[idx])
        hj, _, _, _ = render_xy(
            x[idx],
            y[idx],
            sx=sxy,
            sy=sxy,
            rx=rx,
            ry=ry,
            render_type="fixed_gaussian",
            fwhm=3 * sxy,
        )
        h[j] = hj

    # Compute fourier transform of every histogram
    for j in range(Ns):
        h[j] = fftn(h[j])

    # Compute cross-correlations
    dx = np.zeros((Ns, Ns))
    dy = np.zeros((Ns, Ns))
    dm = np.zeros((Ns, Ns), dtype=bool)
    dx0 = np.zeros(Ns - 1)
    dy0 = np.zeros(Ns - 1)

    for i in range(Ns - 1):
        hi = np.conj(h[i])
        for j in range(i + 1, min(Ns, i + D)):  # Either to Ns or maximally D more
            hj = ifftshift(np.real(ifftn(hi * h[j])))
            yc = c[0]
            xc = c[1]

            # Centroid estimation
            gy = np.arange(yc - 2 * CR, yc + 2 * CR + 1).astype(int)
            gx = np.arange(xc - 2 * CR, xc + 2 * CR + 1).astype(int)
            gy, gx = np.meshgrid(gy, gx, indexing="ij")
            d = hj[gy, gx]
            gy = gy.flatten()
            gx = gx.flatten()
            d = d.flatten() - np.min(d)
            d = d / np.sum(d)
            for k in range(20):
                wc = np.exp(
                    -4 * np.log(2) * ((xc - gx) ** 2 + (yc - gy) ** 2) / CR**2
                )
                n = np.sum(wc * d)
                xc = np.sum(gx * d * wc) / n
                yc = np.sum(gy * d * wc) / n
            sh = np.array([-1.0, 1.0]) * (np.array([yc, xc]) - c)
            dy[i, j] = sh[0]
            dx[i, j] = sh[1]
            dm[i, j] = True
            if j == i + 1:
                dy0[i] = sh[0]
                dx0[i] = sh[1]

    a, b = np.nonzero(dm)
    dx = dx[dm]
    dy = dy[dm]
    sx0 = np.cumsum(dx0)
    sy0 = np.cumsum(dy0)

    # Minimize cost function with some kind of regularization
    options = {"disp": False, "maxiter": 1e5}

    minimizer = lambda x: lse_distance(x, a, b, dx, w, l)
    res = minimize(minimizer, sx0, options=options, method="BFGS")
    sx = np.concatenate(([0], res.x))

    minimizer = lambda x: lse_distance(x, a, b, dy, w, l)
    res = minimize(minimizer, sy0, options=options, method="BFGS")
    sy = np.concatenate(([0], res.x))

    # Reduce by mean (so shift is minimal)
    sx = sx - np.mean(sx)
    sy = sy - np.mean(sy)

    # Multiply by pixel size
    sx = sx * sxy
    sy = sy * sxy

    # Create interpolants
    fx = interp1d(ti, sx, kind="slinear", fill_value="extrapolate")
    fy = interp1d(ti, sy, kind="slinear", fill_value="extrapolate")

    # Correct drift
    dx = fx(t)
    dy = fy(t)

    # Apply to every frame
    ti = np.arange(Rt[0], Rt[1], T / 10)
    dxt = fx(ti)
    dyt = fy(ti)

    return dx, dy, dxt, dyt, ti, T


def drift_correction_time_windows_3d(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    t: np.ndarray,
    sxyz: float,
    rx: Optional[tuple] = None,
    ry: Optional[tuple] = None,
    rz: Optional[tuple] = None,
    T: Optional[float] = None,
    tid: Optional[np.ndarray] = None,
):
    """Estimate 3D drift correction based on auto-correlation.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    x: np.ndarray
        Array of localization x coordinates.

    y: np.ndarray
        Array of localization y coordinates.

    z: np.ndarray
        Array of localization z coordinates.

    t: np.ndarray
        Array of localization time points.

    sxyz: float (Default = 1.0)
        Resolution in nm in x, y and z direction.

    rx: tuple (Optional)
        (min, max) boundaries for the x coordinates. If omitted, it will default to (x.min(), x.max()).

    ry: float (Optional)
        (min, max) boundaries for the y coordinates. If omitted, it will default to (y.min(), y.max()).

    rz: float (Optional)
        (min, max) boundaries for the z coordinates. If omitted, it will default to (z.min(), z.max()).

    T: float (Optional)
        Time window for analysis.

    tid: np.ndarray (Optional)
        Only used if T is None. The unique trace IDs are used to calculate the time window for
        analysis using some heuristics.
    """

    if T is None and tid is None:
        raise ValueError("If T is not defined, the array of TIDs must be provided.")

    # Make sure we are working with NumPy arrays
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    t = np.array(t)
    if tid is not None:
        tid = np.array(tid)

    # Make sure we have valid ranges
    if rx is None:
        rx = (x.min(), x.max())

    if ry is None:
        ry = (y.min(), y.max())

    if rz is None:
        rz = (z.min(), z.max())

    # Heuristics to define the length of the time window
    if T is None:
        rt = (t[0], t[-1])
        T = len(np.unique(tid)) * np.diff(rx)[0] * np.diff(ry)[0] / 3e6
        T = np.min([T, np.diff(rt)[0] / 2, 3600])  # At least two time windows
        T = max([T, 600])  # And at least 10 minutes long

    # Number of time windows to use
    Rt = [t[0], t[-1]]
    Ns = int(np.floor((Rt[1] - Rt[0]) / T))  # total number of time windows
    assert Ns > 1, "At least two time windows are needed, please reduce T"

    # Center of mass
    CR = 8

    # Maximum number of frames in the cross-correlation
    D = Ns

    # Weight with distance
    w = np.linspace(1, 0.2, D)

    # Regularization term (roughness)
    l = 0.01

    # get dimensions
    Nx = int(np.ceil((rx[1] - rx[0]) / sxyz))
    Ny = int(np.ceil((ry[1] - ry[0]) / sxyz))
    Nz = int(np.ceil((rz[1] - rz[0]) / sxyz))
    c = np.round(np.array([Nz, Ny, Nx]) / 2)

    # Create all the histograms
    h = [None] * Ns
    ti = np.zeros(Ns)  # Average times of the snapshots
    for j in range(Ns):
        t0 = Rt[0] + j * T
        idx = (t >= t0) & (t < t0 + T)
        ti[j] = np.mean(t[idx])
        hj, _, _, _, _ = render_xyz(
            x[idx],
            y[idx],
            z[idx],
            sx=sxyz,
            sy=sxyz,
            sz=sxyz,
            rx=rx,
            ry=ry,
            rz=rz,
            render_type="fixed_gaussian",
            fwhm=3 * sxyz,
        )
        h[j] = hj

    # Compute fourier transform of every histogram
    for j in range(Ns):
        h[j] = fftn(h[j])

    # Compute cross-correlations
    dx = np.zeros((Ns, Ns))
    dy = np.zeros((Ns, Ns))
    dz = np.zeros((Ns, Ns))
    dm = np.zeros((Ns, Ns), dtype=bool)
    dx0 = np.zeros(Ns - 1)
    dy0 = np.zeros(Ns - 1)
    dz0 = np.zeros(Ns - 1)

    for i in range(Ns - 1):
        hi = np.conj(h[i])
        for j in range(i + 1, min(Ns, i + D)):  # either to Ns or maximally D more
            hj = ifftshift(np.real(ifftn(hi * h[j])))
            zc = c[0]
            yc = c[1]
            xc = c[2]

            # Centroid estimation
            gz = np.arange(zc - 2 * CR, zc + 2 * CR + 1).astype(int)
            gy = np.arange(yc - 2 * CR, yc + 2 * CR + 1).astype(int)
            gx = np.arange(xc - 2 * CR, xc + 2 * CR + 1).astype(int)
            gz, gy, gx = np.meshgrid(gz, gy, gx, indexing="ij")
            d = hj[gz, gy, gx]
            gz = gz.flatten()
            gy = gy.flatten()
            gx = gx.flatten()
            d = d.flatten() - np.min(d)
            d = d / np.sum(d)
            for k in range(20):
                wc = np.exp(
                    -4
                    * np.log(2)
                    * ((xc - gx) ** 2 + (yc - gy) ** 2 + (zc - gz) ** 2)
                    / CR**2
                )
                n = np.sum(wc * d)
                xc = np.sum(gx * d * wc) / n
                yc = np.sum(gy * d * wc) / n
                zc = np.sum(gz * d * wc) / n
            sh = np.array([1.0, -1.0, 1.0]) * (np.array([zc, yc, xc]) - c)
            dz[i, j] = sh[0]
            dy[i, j] = sh[1]
            dx[i, j] = sh[2]
            dm[i, j] = True
            if j == i + 1:
                dz0[i] = sh[0]
                dy0[i] = sh[1]
                dx0[i] = sh[2]

    a, b = np.nonzero(dm)
    dx = dx[dm]
    dy = dy[dm]
    dz = dz[dm]
    sx0 = np.cumsum(dx0)
    sy0 = np.cumsum(dy0)
    sz0 = np.cumsum(dz0)

    # Minimize cost function with some kind of regularization
    options = {"disp": False, "maxiter": 1e5}

    minimizer = lambda x: lse_distance(x, a, b, dx, w, l)
    res = minimize(minimizer, sx0, options=options, method="BFGS")
    sx = np.concatenate(([0], res.x))

    minimizer = lambda x: lse_distance(x, a, b, dy, w, l)
    res = minimize(minimizer, sy0, options=options, method="BFGS")
    sy = np.concatenate(([0], res.x))

    minimizer = lambda x: lse_distance(x, a, b, dz, w, l)
    res = minimize(minimizer, sz0, options=options, method="BFGS")
    sz = np.concatenate(([0], res.x))

    # Reduce by mean (so shift is minimal)
    sx = sx - np.mean(sx)
    sy = sy - np.mean(sy)
    sz = sz - np.mean(sz)

    # Multiply by voxel size
    sx = sx * sxyz
    sy = sy * sxyz
    sz = sz * sxyz

    # Create interpolants
    fx = interp1d(ti, sx, kind="slinear", fill_value="extrapolate")
    fy = interp1d(ti, sy, kind="slinear", fill_value="extrapolate")
    fz = interp1d(ti, sz, kind="slinear", fill_value="extrapolate")

    # Correct drift
    dx = fx(t)
    dy = fy(t)
    dz = fz(t)

    # Apply to every frame
    ti = np.arange(Rt[0], Rt[1], T / 10)
    dxt = fx(ti)
    dyt = fy(ti)
    dzt = fz(ti)

    return dx, dy, dz, dxt, dyt, dzt, ti, T


def lse_distance(x, a, b, s, w, l):
    """Calculate Least Squares Error (LSE) with regularization.

    Reimplemented (with modifications) from:

    * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    * [code]  https://zenodo.org/record/6563100

    Parameters
    ----------

    x: np.ndarray

    a: np.ndarray
        Array of indices to be used (with b) to calculate the predicted shifts (x[b] - x[a]).

    b: np.ndarray
        Array of indices to be used (with a) to calculate the predicted shifts (x[b] - x[a]).

    s: np.ndarray
        Array of shifts to be compared.

    w: float
        Weighting factor.

    l: float
        Regularization term.
    """

    # Add shift 0 for the first frame
    x = np.concatenate(([0], x))
    dx = x[b] - x[a]
    y = w[b - a] * (dx - s) ** 2
    y = np.mean(y)

    # Add regularization term (roughness)
    r = l * np.sum(np.diff(x) ** 2)
    y = y + r

    return y
