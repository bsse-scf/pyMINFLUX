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
    crn = np.power(num_values, 1/3)
    bin_width = (factor * iqr) / crn

    # Pathological case where all values are identical
    if bin_width == 0.0:
        bin_width = 1.0

    # Get min and max values
    min_value = np.min(values)
    max_value = np.max(values)

    # Calculate number of bins
    num_bins = int(np.round((max_value - min_value) / bin_width))

    half_width = bin_width / 2

    bin_edges = np.linspace(min_value - half_width, max_value, num_bins)
    bin_centers = (bin_edges[0:-1] + bin_edges[1:]) / 2

    return bin_edges, bin_centers, bin_edges[1] - bin_edges[0]
