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

import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.analysis import (
    find_first_peak_bounds,
    get_robust_threshold,
    prepare_histogram,
)


@pytest.fixture(autouse=False)
def extract_bounds_extraction_data_archive(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    npy_file_names = [
        Path(__file__).parent / "data" / "2d_only_cfr.npy",
        Path(__file__).parent / "data" / "2d_only_efo.npy",
        Path(__file__).parent / "data" / "3d_only_cfr.npy",
        Path(__file__).parent / "data" / "3d_only_efo.npy",
        Path(__file__).parent / "data" / "3d_only_overlabeled_efo.npy",
        Path(__file__).parent / "data" / "3d_only_overlabeled_cfr.npy",
    ]

    # Make sure to extract the test data if it is not already there
    need_to_extract = False
    for npy_file_name in npy_file_names:
        if not npy_file_name.is_file():
            need_to_extract = True
            break

    if need_to_extract:
        archive_filename = Path(__file__).parent / "data" / "bounds_extraction.zip"
        with zipfile.ZipFile(archive_filename, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_efo_cfr_bounds_extraction(extract_bounds_extraction_data_archive):
    #
    # 2D_only_efo.npy
    #

    # Load data
    efo = np.load(Path(__file__).parent / "data" / "2d_only_efo.npy")
    assert efo is not None, "Could not load file."
    assert len(efo) == 11903, "Wrong dimensions for 2d_only_efo."

    # Calculate the normalized histogram

    # Use 1kHz bins
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=False, bin_size=1000.0)
    assert len(n_efo) == 420
    assert b_efo[1] - b_efo[0] == 1000.0
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Use automatic bin_size determination
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=True)
    assert len(n_efo) == 377
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Check defaults
    n_efo, _, b_efo, _ = prepare_histogram(efo)
    assert len(n_efo) == 377
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == 13821.63722748869
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 48225.758832542466
    ), "The upper bound is wrong!"

    #
    # 2D_only_cfr.npy
    #

    # Load data
    cfr = np.load(Path(__file__).parent / "data" / "2d_only_cfr.npy")
    assert cfr is not None, "Could not load file."
    assert len(cfr) == 11903, "Wrong dimensions for 2d_only_cfr."

    # Get robust thresholds
    upper_bound, lower_bound, med, mad = get_robust_threshold(cfr, factor=2.0)
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.015163637960486809
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.2715112942104868
    ), "The median value is wrong!"
    assert pytest.approx(med, 1e-4) == 0.128173828125, "The lower bound is wrong!"
    assert (
        pytest.approx(mad, 1e-4) == 0.0716687330427434
    ), "The median absolute difference value is wrong!"

    #
    # 3D_only_efo.npy
    #

    # Load data
    efo = np.load(Path(__file__).parent / "data" / "3d_only_efo.npy")
    assert efo is not None, "Could not load file."
    assert len(efo) == 5492, "Wrong dimensions for 3d_only_efo."

    # Calculate the normalized histogram

    # Use 1kHz bins
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=True)
    assert len(n_efo) == 126
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Use automatic bin_size determination
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=False, bin_size=1000.0)
    assert len(n_efo) == 284
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5
    )
    assert pytest.approx(lower_bound, 1e-4) == 12000.0, "The lower bound is wrong!"
    assert pytest.approx(upper_bound, 1e-4) == 23000.0, "The upper bound is wrong!"

    #
    # 3D_only_cfr.npy
    #

    # Load data
    cfr = np.load(Path(__file__).parent / "data" / "3d_only_cfr.npy")
    assert cfr is not None, "Could not load file."
    assert len(cfr) == 5492, "Wrong dimensions for 3d_only_cfr."

    # Get robust thresholds
    upper_bound, lower_bound, med, mad = get_robust_threshold(cfr, factor=2.0)
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.0006192938657819114
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.7052091376157819
    ), "The median value is wrong!"
    assert pytest.approx(med, 1e-4) == 0.352294921875, "The lower bound is wrong!"
    assert (
        pytest.approx(mad, 1e-4) == 0.17645710787039096
    ), "The median absolute difference value is wrong!"

    #
    # 3D_only_overlabeled_efo.npy
    #

    # Load data
    efo = np.load(Path(__file__).parent / "data" / "3d_only_overlabeled_efo.npy")
    assert efo is not None, "Could not load file."
    assert len(efo) == 81888, "Wrong dimensions for 3d_only_overlabeled_efo."

    # Calculate the normalized histogram

    # Use 1kHz bins
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=False, bin_size=1000.0)
    assert len(n_efo) == 2125
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Use automatic bin_size determination
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=True)
    assert len(n_efo) == 1281
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5
    )
    assert pytest.approx(lower_bound, 1e-4) == 11600, "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 44760.60183679485
    ), "The upper bound is wrong!"

    #
    # 3D_only_overlabeled_cfr.npy
    #

    # Load data
    cfr = np.load(Path(__file__).parent / "data" / "3d_only_overlabeled_cfr.npy")
    assert cfr is not None, "Could not load file."
    assert len(cfr) == 81888, "Wrong dimensions for 3d_only_overlabeled_cfr."

    # Get robust thresholds
    upper_bound, lower_bound, med, mad = get_robust_threshold(cfr, factor=2.0)
    assert (
        pytest.approx(lower_bound, 1e-4) == 0.45367502494940626
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.8646843500505937
    ), "The median value is wrong!"
    assert pytest.approx(med, 1e-4) == 0.6591796875, "The lower bound is wrong!"
    assert (
        pytest.approx(mad, 1e-4) == 0.10275233127529688
    ), "The median absolute difference value is wrong!"
