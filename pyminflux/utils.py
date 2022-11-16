import numpy as np
from scipy import stats


def ideal_hist_bins(values, scott=False):
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

    bin_width:
        Bin width.
    """

    if len(values) == 0:
        raise ValueError("No data.")

    # Calculate bin width
    factor = 2.0
    if scott:
        factor = 2.59
    iqr = stats.iqr(values, rng=(25, 75), scale=1.0, nan_policy="omit")
    num_values = np.sum(np.logical_not(np.isnan(values)))
    crn = np.power(num_values, 1 / 3)
    bin_width = (factor * iqr) / crn

    # Get min and max values
    min_value = np.min(values)
    max_value = np.max(values)

    # Pathological case where bin_width is 0.0
    if bin_width == 0.0:
        bin_width = 0.5 * (min_value + max_value)

    # Calculate number of bins
    num_bins = int(np.round((max_value - min_value) / bin_width))

    half_width = bin_width / 2

    bin_edges = np.linspace(min_value - half_width, max_value, num_bins)
    bin_centers = (bin_edges[0:-1] + bin_edges[1:]) / 2
    if len(bin_edges) >= 2:
        bin_width = bin_edges[1] - bin_edges[0]

    return bin_edges, bin_centers, bin_width


def calculate_common_bins(first_array_values, second_array_values):
    """Calculate bins commons to both sets of values.

    Parameters
    ----------

    first_array_values: np.ndarray
        First array of values. It may contain NaNs.

    second_array_values: np.ndarray
        Second array of values. It may contain NaNs.

    Returns
    -------

    bin_edges: np.ndarray
        Array of bin edges (compatible with NumPy.histogram())

    bin_centers: np.ndarray
        Array of bin centers

    bin_width: float
        Bin width.
    """
    num_first = np.sum(np.logical_not(np.isnan(first_array_values)))
    num_second = np.sum(np.logical_not(np.isnan(second_array_values)))
    if num_first == 0 and num_second == 0:
        raise ValueError("No usable data.")
    elif num_first >= num_second:
        bin_edges, bin_centers, bin_width = ideal_hist_bins(first_array_values)
    elif num_first < num_second:
        bin_edges, bin_centers, bin_width = ideal_hist_bins(second_array_values)
    else:
        raise ValueError("Unexpected case.")

    return bin_edges, bin_centers, bin_width


def get_robust_threshold(values: np.ndarray, factor: float = 2.0):
    """Calculate a robust threshold for the array of values.

    The threshold is defines as median + thresh * median absolute deviation.

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

    threshold: float
        Calculate threshold.

    med: float
        Median of the array of values.

    mad: float
        Scaled median absolute deviation of the array of values.
    """

    # Remove NaNs
    work_values = values.copy()
    work_values = work_values[np.logical_not(np.isnan(work_values))]
    if len(work_values) == 0:
        return None, None, None

    # Calculate robust statistics and threshold
    med = np.median(work_values)
    mad = stats.median_abs_deviation(work_values, scale=0.67449)
    threshold = med + factor * mad

    return threshold, med, mad


def print_summary_statistics(values: np.ndarray):
    """Prints summary statistics.

    Parameters
    ----------

    values: np.ndarray
        Array of values. It may contain NaNs.
    """

    # Count number of valid entries
    num_valid = np.logical_not(np.isnan(values)).sum()

    if num_valid == 0:
        print("Nothing to summarize.")
        return

    print(
        f"Num valid entries = {num_valid}/{len(values)} ({100 * num_valid / len(values):.2f}%)\n"
        f"Min               = {np.nanmin(values)}\n"
        f"25% percentile    = {np.nanpercentile(values, 25)}\n"
        f"Median            = {np.nanmedian(values)}\n"
        f"Mean              = {np.nanmean(values):.2f}\n"
        f"75% percentile    = {np.nanpercentile(values, 75)}\n"
        f"Max               = {np.nanmax(values)}"
    )
