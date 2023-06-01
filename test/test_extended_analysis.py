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

import zipfile
from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pyminflux.analysis import (
    get_localization_boundaries,
    img_fourier_ring_correlation,
    render_xy,
)
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.state import State


@pytest.fixture(autouse=False)
def extract_raw_npy_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    npy_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy"
    zip_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    npy_file_name = Path(__file__).parent / "data" / "3D_ValidOnly.npy"
    zip_file_name = Path(__file__).parent / "data" / "3D_ValidOnly.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_data_boundaries(extract_raw_npy_data_files):
    """Test the analysis.get_localization_boundaries() function."""

    # Initialize State
    state = State()

    #
    # 2D_Only.npy
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Get boundaries at default alpha and min_range
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
    )

    # Test
    assert np.isclose(rx[0], 1744.43303535), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 5492.12179283), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -15538.14183461), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -11702.99913876), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], 0.0), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 0.0), "Unexpected upper boundary for z."

    # Get boundaries at alpha=0.2 and default min_range
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.2,
    )

    # Test
    assert np.isclose(rx[0], 2290.12936281), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 4720.17628345), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -15065.18736499), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -12315.87321753), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], 0.0), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 0.0), "Unexpected upper boundary for z."

    # Get boundaries at alpha=0.49 and default min_range
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.49,
    )

    # Test
    assert np.isclose(rx[0], 3276.73966011), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 3476.73966011), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -13981.9058782), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -13781.9058782), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], 0.0), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 0.0), "Unexpected upper boundary for z."
    assert np.isclose(rx[1] - rx[0], 200.0), "Unexpected range for x."
    assert np.isclose(ry[1] - ry[0], 200.0), "Unexpected range for y."

    # Get boundaries at default alpha and min_range=5000
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        min_range=5000,
    )

    # Test
    assert np.isclose(rx[0], 1118.27741409), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 6118.27741409), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -16120.57048668), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -11120.57048668), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], 0.0), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 0.0), "Unexpected upper boundary for z."
    assert np.isclose(rx[1] - rx[0], 5000.0), "Unexpected range for x."
    assert np.isclose(ry[1] - ry[0], 5000.0), "Unexpected range for y."

    #
    # 3D_Only.npy
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Get boundaries at default alpha and min_range
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
    )

    # Test
    assert np.isclose(rx[0], 1610.71322264), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 5439.30190298), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -10610.38121423), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -6882.35098526), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], -216.75738013), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 129.18317291), "Unexpected upper boundary for z."

    # Get boundaries at alpha=0.2 and default min_range
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.2,
    )

    # Test
    assert np.isclose(rx[0], 2311.1744342), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 4519.76543671), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -9910.17370305), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -7415.93602781), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], -111.89731079), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 88.10268921), "Unexpected upper boundary for z."
    assert np.isclose(rz[1] - rz[0], 200.0)

    # Get boundaries at alpha=0.49 and default min_range
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.49,
    )

    # Test
    assert np.isclose(rx[0], 3357.27017594), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 3557.27017594), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -8976.91805543), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -8776.91805543), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], -107.14343652), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 92.85656348), "Unexpected upper boundary for z."
    assert np.isclose(rx[1] - rx[0], 200.0), "Unexpected range for x."
    assert np.isclose(ry[1] - ry[0], 200.0), "Unexpected range for y."
    assert np.isclose(rz[1] - rz[0], 200.0), "Unexpected range for z."

    # Get boundaries at default alpha and min_range=5000
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        min_range=5000,
    )

    # Test
    assert np.isclose(rx[0], 1025.00756281), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 6025.00756281), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -11246.36609975), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -6246.36609975), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], -2543.78710361), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 2456.21289639), "Unexpected upper boundary for z."
    assert np.isclose(rx[1] - rx[0], 5000.0), "Unexpected range for x."
    assert np.isclose(ry[1] - ry[0], 5000.0), "Unexpected range for y."
    assert np.isclose(rz[1] - rz[0], 5000.0), "Unexpected range for z."


def test_render_xy(extract_raw_npy_data_files):
    """Test the analysis.render_xy() function."""

    # Initialize State
    state = State()

    #
    # 2D_Only.npy
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Get boundaries at alpha = 0.0 and min_range = 500: this gives all data back.
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.0,
        min_range=500,
    )

    # Test
    assert np.isclose(rx[0], 1647.61105813), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 5677.04500607), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -15659.23531582), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -11623.81911211), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], 0.0), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 0.0), "Unexpected upper boundary for z."

    # Rendering resolution (in nm)
    sx = 1.0
    sy = 1.0

    # Render the 2D image as simple histogram
    img, xi, yi, m = render_xy(
        processor.filtered_dataframe["x"].values,
        processor.filtered_dataframe["y"].values,
        sx=sx,
        sy=sy,
        rx=None,
        ry=None,
    )

    # Check the returned values
    assert np.isclose(img.sum(), 12580.0), "Unexpected signal integral."
    assert np.isclose(xi.min(), 1648.111058125942), "Unexpected x grid (min value)."
    assert np.isclose(xi.max(), 5677.111058125942), "Unexpected x grid (max) value)."
    assert np.isclose(yi.min(), -15658.73531581803), "Unexpected y grid (min value)."
    assert np.isclose(yi.max(), -11623.73531581803), "Unexpected y grid (max value)."
    assert m.sum() == 12580.0, "Unexpected number of considered elements."
    assert m.sum() == len(
        processor.filtered_dataframe["x"].values
    ), "Unexpected number of considered elements."

    # Render the 2D image as a Gaussian fit
    img, xi, yi, m = render_xy(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        sx=sx,
        sy=sy,
        rx=None,
        ry=None,
        render_type="fixed_gaussian",
    )

    # Check the returned values
    assert np.isclose(img.sum(), 256250.47), "Unexpected signal integral."
    assert np.isclose(xi.min(), 1648.111058125942), "Unexpected x grid (min value)."
    assert np.isclose(xi.max(), 5677.111058125942), "Unexpected x grid (max) value)."
    assert np.isclose(yi.min(), -15658.73531581803), "Unexpected y grid (min value)."
    assert np.isclose(yi.max(), -11623.73531581803), "Unexpected y grid (max value)."
    assert m.sum() == 12564.0, "Unexpected number of considered elements."
    assert m.sum() < len(
        processor.filtered_dataframe["x"].values
    ), "Unexpected number of considered elements."


def test_fourier_ring_correlation(extract_raw_npy_data_files):
    """Test the analysis.img_fourier_ring_correlation() function."""

    # Initialize State
    state = State()

    #
    # 2D_Only.npy
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Get boundaries at alpha = 0.0 and min_range = 500: this gives all data back.
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.0,
        min_range=500,
    )

    # Test
    assert np.isclose(rx[0], 1647.61105813), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 5677.04500607), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -15659.23531582), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -11623.81911211), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], 0.0), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 0.0), "Unexpected upper boundary for z."

    # Work on 2D data
    x = processor.filtered_dataframe["x"].values
    y = processor.filtered_dataframe["y"].values

    # Initialize the random number generator
    rng = np.random.default_rng(2023)

    N = 5
    expected_resolutions = np.array(
        [7.19424460e-09, 6.99300699e-09, 6.75675676e-09, 6.99300699e-09, 6.99300699e-09]
    )
    resolutions = np.zeros(N)
    for r in range(N):

        # Partition the data
        ix = rng.random(size=x.shape) < 0.5
        c_ix = np.logical_not(ix)

        # Create two images from (complementary) subsets of coordinates (x, y) using the "histogram"
        # mode and a rendering resolution of sxy = 1.0 nm.
        sxy = 1.0
        h1 = render_xy(x[ix], y[ix], sxy, sxy, rx, ry)[0]
        h2 = render_xy(x[c_ix], y[c_ix], sxy, sxy, rx, ry)[0]

        # Estimate the resolution using Fourier Ring Correlation
        estimated_resolution, fc, qi, ci = img_fourier_ring_correlation(
            h1, h2, sx=sxy, sy=sxy
        )

        # Store the estimated resolution
        resolutions[r] = estimated_resolution

    # Test
    assert np.allclose(
        resolutions, expected_resolutions
    ), "Calculated resolutions do not match the expected ones."

    #
    # Fig1a_Tom70-Dreiklang_Minflux.mat
    #
    # From:
    #   * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    #   * [code]  https://zenodo.org/record/6563100

    minflux = loadmat(
        Path(__file__).parent / "data" / "Fig1a_Tom70-Dreiklang_Minflux.mat"
    )
    minflux = minflux["minflux"]

    # x and y coordinates
    pos = minflux["pos"][0][0]
    x = pos[:, 0]
    y = pos[:, 1]

    # Ranges
    rx = (-372.5786, 318.8638)
    ry = (-1148.8, 1006.6)

    # Initialize the random number generator
    rng = np.random.default_rng(2023)

    N = 5
    expected_resolutions = np.array(
        [5.44959128e-09, 5.46448087e-09, 5.66572238e-09, 5.61797753e-09, 5.49450549e-09]
    )
    resolutions = np.zeros(N)
    for r in range(N):

        # Partition the data
        ix = rng.random(size=x.shape) < 0.5
        c_ix = np.logical_not(ix)

        # Create two images from (complementary) subsets of coordinates (x, y) using the "histogram"
        # mode and a rendering resolution of sxy = 1.0 nm.
        sxy = 1.0
        h1 = render_xy(x[ix], y[ix], sxy, sxy, rx, ry)[0]
        h2 = render_xy(x[c_ix], y[c_ix], sxy, sxy, rx, ry)[0]

        # Estimate the resolution using Fourier Ring Correlation
        estimated_resolution, fc, qi, ci = img_fourier_ring_correlation(
            h1, h2, sx=sxy, sy=sxy
        )

        # Store the estimated resolution
        resolutions[r] = estimated_resolution

    # Test
    assert np.allclose(
        resolutions, expected_resolutions
    ), "Calculated resolutions do not match the expected ones."
