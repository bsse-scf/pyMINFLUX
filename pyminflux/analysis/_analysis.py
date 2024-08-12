#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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
#  limitations under the License.

import math
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats
from scipy.ndimage import median_filter
from scipy.signal import find_peaks
from sklearn.mixture import BayesianGaussianMixture


def calculate_time_steps(df: pd.DataFrame, unit_factor: float = 1e3):
    """Calculate time resolution of acquisition.

    Parameters
    ----------

    df: pd.DataFrame
        Processed dataframe as returned by `MinFluxReader.processed_dataframe`.
        The dataframe is expected to contain the columns "tid" and "tim".

    unit_factor: float (default = 1e3)
        Factor by which the time resolution is multiplied. By default, `unit_factor`
        is 1e3, to return the resolution in milliseconds.

    Returns
    -------
    tim_diff: pd.DataFrame
        Dataframe with all time differences between consecutive localizations. Columns are "tid" and "tif_diff"

    med: float
        Median time resolution of tim_diff

    mad: float
        Median absolute deviation of the time resolution from tim_diff (divided by 0.67449 to bring it to the
        scale of the standard deviation)
    """

    # Work on a shallow copy
    df_copy = df[["tid", "tim"]].copy()

    # Calculate time differences and apply unit factor
    df_copy.loc[:, "tim_diff"] = df_copy.groupby("tid")["tim"].diff() * unit_factor

    # Calculate the median and the mad
    med = np.nanmedian(df_copy["tim_diff"].to_numpy())
    mad = stats.median_abs_deviation(
        df_copy["tim_diff"].to_numpy(), scale=0.67449, nan_policy="omit"
    )

    return df_copy[["tid", "tim_diff"]], med, mad


def calculate_trace_time(df: pd.DataFrame, unit_factor: float = 1e3):
    """Calculate total trace time.

    Parameters
    ----------

    df: pd.DataFrame
        Processed dataframe as returned by `MinFluxReader.processed_dataframe`.
        The dataframe is expected to contain the columns "tid" and "tim".

    unit_factor: float (default = 1e3)
        Factor by which the time resolution is multiplied. By default, `unit_factor`
        is 1e3, to return the resolution in milliseconds.

    Returns
    -------

    tim_tot: pd.DataFrame
        Dataframe with total time per trace. Columns are "tid" and "tim_tot"

    med_tot: float
        Median time resolution of tot_tim

    mad_tot: float
        Median absolute deviation of the time resolution from tot_tim (divided by 0.67449 to bring it to the
        scale of the standard deviation)
    """

    # Get the time steps
    tim_diff, _, _ = calculate_time_steps(df, unit_factor)

    # Calculate total time per trace
    tim_tot = tim_diff.groupby("tid")["tim_diff"].sum().reset_index(name="tim_tot")

    # Calculate median and mad per trace
    med_tot = np.nanmedian(tim_tot["tim_tot"].to_numpy())
    mad_tot = stats.median_abs_deviation(
        tim_tot["tim_tot"].to_numpy(), scale=0.67449, nan_policy="omit"
    )

    return tim_tot, med_tot, mad_tot


def calculate_displacements(df: pd.DataFrame, is_3d: Optional[bool] = None):
    """Calculate displacement resolution.

    Parameters
    ----------

    df: pd.DataFrame
        The MinFluxProcessor.filtered_dataframe.

    is_3d: bool
        Set to True for 3D datasets, False for 2D datasets.

    Return
    ------

    displacements: pd.DataFrame
        All individual displacements.

    med_displ: float
        Median displacement (step).

    mad_displ: float
        Median absolute deviation of the displacements (steps), divided by 0.67449 to bring it to the scale of the
        standard deviation.
    """

    # Determine if 3D calculations are needed
    if is_3d is None:
        is_3d = bool(np.any(df["z"] != 0))

    # Selecting columns based on whether the data is 3D
    cols = ["tid", "x", "y", "z"] if is_3d else ["tid", "x", "y"]
    df_subset = df[cols].copy()

    # Calculate translations per tid
    diffs = df_subset.groupby("tid").diff()

    # Calculate displacements per tid
    df_subset.loc[:, "displacement"] = np.linalg.norm(diffs.to_numpy(), axis=1)

    # Do we have data?
    if len(df_subset.index) == 0 or "displacement" not in df_subset.columns:
        df_subset["displacement"] = []
    med = float(np.nanmedian(df_subset["displacement"].to_numpy()))
    mad = float(
        stats.median_abs_deviation(
            df_subset["displacement"].to_numpy(), scale=0.67449, nan_policy="omit"
        )
    )

    return df_subset[["tid", "displacement"]], med, mad


def calculate_total_distance_traveled(df: pd.DataFrame, is_3d: Optional[bool] = None):
    """Calculate total distance traveled for each tid in a dataframe.

    Parameters
    ----------

    df: pd.DataFrame
        The MinFluxProcessor.filtered_dataframe.

    is_3d: bool
        Set to True for 3D datasets, False for 2D datasets.

    Return
    ------

    total_distance: pd.DataFrame
        Total distance traveled per tid.

    med_tot: float
        Median total distance traveled across all tids.

    mad_tot: float
        Median absolute deviation of the distances traveled across all tids,divided by 0.67449 to bring it to the
        scale of the standard deviation.
    """

    # Get the displacements
    displacements, _, _ = calculate_displacements(df)

    # Calculate total distance per tid
    total_distance = displacements.groupby("tid")["displacement"].sum().reset_index()

    # Calculate median and mad of the total distance
    med = float(np.nanmedian(total_distance["displacement"].to_numpy()))
    mad = float(
        stats.median_abs_deviation(
            total_distance["displacement"].to_numpy(), scale=0.67449, nan_policy="omit"
        )
    )

    return total_distance, med, mad


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
    min_value = bin_size * int(np.nanmin(values) / bin_size)

    # Max value
    max_value = np.nanmax(values)

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
    if np.all(np.diff(values[np.logical_not(np.isnan(values))]) == 0):
        bin_edges = np.array([values[0] - 5e-7, values[0] + 5e-7])
        bin_centers = np.array(
            [
                values[0],
            ]
        )
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
    min_value = np.nanmin(values)
    max_value = np.nanmax(values)

    # Pathological case where bin_size is 0.0
    if bin_size == 0.0:
        bin_size = 0.5 * (max_value - min_value)

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
        Estimated cutoff frequency.
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


def assign_data_to_clusters(
    x: np.ndarray, num_clusters: int = 2, seed: Optional[int] = None
):
    """Use Gaussian Mixture Model fitting to assign data to the requested number of clusters.

    Parameters
    ----------

    x: np.ndarray
        Array of values to cluster.

    num_clusters: int (Default = 2)
        Number of clusters to be assigned.

    seed: int (Optional)
        Seed for the random number generator.

    Returns
    -------

    ids: np.ndarray
        Array of cluster ids for each value in x. The first cluster has ID 1.
    """

    # Make sure to work with a NumPy array
    x = np.array(x)

    # Make sure to work with a column vector
    x = x.reshape(-1, 1)

    # Fit a Bayesian Gaussian Mixture Model with self.state.num_fluorophores components
    model = BayesianGaussianMixture(
        n_components=num_clusters,
        init_params="k-means++",
        covariance_type="full",
        max_iter=1000,
        random_state=seed,
    ).fit(x)

    # Predict with the selected model
    y_pred = model.predict(x)

    # If num_clusters is > 1, sort the indices by mean values of x,
    # from low to high (to match the assignment of the manual thresholding)
    if num_clusters > 1:
        means = [np.mean(x[y_pred == f_id]) for f_id in np.unique(y_pred)]
        sorted_f = np.argsort(means)
        for f in range(num_clusters):
            if np.isnan(means[f]):
                continue
            n = sorted_f[f] + num_clusters
            y_pred[y_pred == f] = n
        y_pred -= num_clusters

    # Now make the clusters ID start from 1 instead of 0.
    ids = y_pred + 1

    # Return
    return ids


def reassign_fluo_ids_by_majority_vote(fluo_ids: np.ndarray, tids: np.ndarray):
    """Reassign IDs of fluorophores by majority so that TIDs have only one fluorophore ID assigned.

    Parameters
    ----------
    fluo_ids: np.ndarray
        Array of fluorophores IDs.

    tids : np.ndarray
        Array of trace IDs.
    """

    # Work on a copy of fluo_ids
    work_fluo_ids = fluo_ids.copy()

    # Find the unique tids and their indices
    _, indices = np.unique(tids, return_index=True)

    # Split the fluo_ids array into sub-arrays corresponding to each unique ID.
    # Note: np.split() returns views into the original array, so the code below
    # will update work_fluo_ids in place!
    split_fluo_ids = np.split(work_fluo_ids, indices[1:])

    # Reassign by majority vote
    for i, s in enumerate(split_fluo_ids):
        if not np.all(s == s[0]):
            # Only process TIDs that have more than one fluo_id associated to them
            majority_class = np.argmax(np.bincount(s))
            split_fluo_ids[i][:] = majority_class

    # We can now return work_fluo_ids, that has been modified in place by the split_fluo_ids views
    return work_fluo_ids
