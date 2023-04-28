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

import numpy as np

from pyminflux.analysis import ideal_hist_bins


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
