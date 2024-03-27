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
#   limitations under the License.
#

import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.io import loadmat

from pyminflux.fourier import (
    estimate_resolution_by_frc,
    get_localization_boundaries,
    img_fourier_ring_correlation,
)
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.render import render_xy, render_xyz


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

    #
    # 2D_Only.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

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
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

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
    """Test the render.render_xy() function."""

    #
    # 2D_Only.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

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
    assert np.isclose(
        img.sum(), len(processor.filtered_dataframe["x"].values)
    ), "Unexpected signal integral."
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
    assert np.isclose(img.sum(), 256291.22), "Unexpected signal integral."
    assert np.isclose(xi.min(), 1648.111058125942), "Unexpected x grid (min value)."
    assert np.isclose(xi.max(), 5677.111058125942), "Unexpected x grid (max) value)."
    assert np.isclose(yi.min(), -15658.73531581803), "Unexpected y grid (min value)."
    assert np.isclose(yi.max(), -11623.73531581803), "Unexpected y grid (max value)."
    assert m.sum() == 12566.0, "Unexpected number of considered elements."
    assert m.sum() < len(
        processor.filtered_dataframe["x"].values
    ), "Unexpected number of considered elements."


def test_render_xyz(extract_raw_npy_data_files):
    """Test the render.render_xyz() function."""

    #
    # 3D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 3D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Get boundaries at alpha = 0.0 and min_range = 500: this gives all data back.
    rx, ry, rz = get_localization_boundaries(
        processor.filtered_dataframe["x"],
        processor.filtered_dataframe["y"],
        processor.filtered_dataframe["z"],
        alpha=0.0,
        min_range=500,
    )

    # Test
    assert np.isclose(rx[0], 1508.14087089), "Unexpected lower boundary for x."
    assert np.isclose(rx[1], 5471.75772354), "Unexpected upper boundary for x."
    assert np.isclose(ry[0], -10781.08977624), "Unexpected lower boundary for y."
    assert np.isclose(ry[1], -6761.66793333), "Unexpected upper boundary for y."
    assert np.isclose(rz[0], -358.31916504), "Unexpected lower boundary for z."
    assert np.isclose(rz[1], 147.03635254), "Unexpected upper boundary for z."

    # Rendering resolution (in nm)
    sx = 5.0
    sy = 5.0
    sz = 5.0

    # Render the 3D image as simple histogram
    img, xi, yi, zi, m = render_xyz(
        processor.filtered_dataframe["x"].values,
        processor.filtered_dataframe["y"].values,
        processor.filtered_dataframe["z"].values,
        sx=sx,
        sy=sy,
        sz=sz,
        rx=None,
        ry=None,
        rz=None,
    )

    # Check the returned values
    assert np.isclose(img.sum(), 5810.0), "Unexpected signal integral."
    assert np.isclose(xi.min(), 1510.6408708914191), "Unexpected x grid (min value)."
    assert np.isclose(xi.max(), 5470.640870891419), "Unexpected x grid (max) value)."
    assert np.isclose(yi.min(), -10778.589776239387), "Unexpected y grid (min value)."
    assert np.isclose(yi.max(), -6763.589776239387), "Unexpected y grid (max value)."
    assert np.isclose(zi.min(), -355.8191650390625), "Unexpected z grid (min value)."
    assert np.isclose(zi.max(), 149.1808349609375), "Unexpected z grid (max value)."
    assert m.sum() == 5810.0, "Unexpected number of considered elements."

    #
    # Fig2_U2OS_Tom70-Dreiklang_ATP5B_AB_Minflux3D.mat -> csv
    #
    # From:
    #   * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    #   * [code]  https://zenodo.org/record/6563100

    df = pd.read_csv(
        Path(__file__).parent
        / "data"
        / "Fig2_U2OS_Tom70-Dreiklang_ATP5B_AB_Minflux3D.csv",
    )
    pos = df[["x", "y", "z"]].values

    # Rendering resolution (in nm)
    sx = 3.0
    sy = 3.0
    sz = 3.0

    # Spatial ranges
    rx = (-434.5609880335669, 367.8659119806681)
    ry = (-1419.260678440071, 1801.300331041331)
    rz = (-298.8539888427734, 90.5609084228519)

    # Render the 3D image as a Gaussian fit
    img, xi, yi, si, m = render_xyz(
        pos[:, 0],
        pos[:, 1],
        pos[:, 2],
        sx=sx,
        sy=sy,
        sz=sz,
        rx=rx,
        ry=ry,
        rz=rz,
        render_type="fixed_gaussian",
        fwhm=15.0,
    )

    # Check the returned values
    assert np.isclose(img.sum(), 1704868.5), "Unexpected signal integral."
    assert np.isclose(xi.min(), -433.0609880335669), "Unexpected x grid (min value)."
    assert np.isclose(xi.max(), 367.9390119664331), "Unexpected x grid (max) value)."
    assert np.isclose(yi.min(), -1417.760678440071), "Unexpected y grid (min value)."
    assert np.isclose(yi.max(), 1801.239321559929), "Unexpected y grid (max value)."
    assert np.isclose(zi.min(), -355.8191650390625), "Unexpected z grid (min value)."
    assert np.isclose(zi.max(), 149.1808349609375), "Unexpected z grid (max value)."
    assert m.sum() == 11308.0, "Unexpected number of considered elements."


def test_fourier_ring_correlation_all_pos(extract_raw_npy_data_files):
    """Test the analysis.img_fourier_ring_correlation() function on all positions."""

    #
    # 2D_Only.npy
    #
    # min_trace_length = 1 (do not filter anything)

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

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
        [7.45222930e-09, 7.21934713e-09, 7.23952096e-09, 7.19072165e-09, 7.18644739e-09]
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

        # Store the estimated resolution, qis and cis
        resolutions[r] = estimated_resolution

    # Test
    assert np.allclose(
        resolutions, expected_resolutions
    ), "Calculated resolutions do not match the expected ones."


def test_fourier_ring_correlation_all_pos_mat(extract_raw_npy_data_files):
    """Test the analysis.img_fourier_ring_correlation() function on all positions (.mat file)."""

    #
    # Fig1a_Tom70-Dreiklang_Minflux.mat
    #
    # From:
    #   * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    #   * [code]  https://zenodo.org/record/6563100

    minflux = loadmat(
        str(Path(__file__).parent / "data" / "Fig1a_Tom70-Dreiklang_Minflux.mat")
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
        [5.48722467e-09, 5.67730173e-09, 5.72426471e-09, 5.82600561e-09, 5.68248175e-09]
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


def test_fourier_ring_correlation_per_tid(extract_raw_npy_data_files):
    """Test the analysis.img_fourier_ring_correlation() function on average positions per TID."""

    #
    # 2D_Only.npy
    #
    # min_trace_length = 1 (do not to filter anything)

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

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

    # Work on averaged 2D data
    x = processor.filtered_dataframe_stats["mx"].values
    y = processor.filtered_dataframe_stats["my"].values

    # Initialize the random number generator
    rng = np.random.default_rng(2023)

    N = 5
    expected_resolutions = np.array(
        [1.69882904e-08, 2.05962521e-08, 1.92618163e-08, 1.73457676e-08, 1.92413793e-08]
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


def test_fourier_ring_correlation_per_tid_mat(extract_raw_npy_data_files):
    """Test the analysis.img_fourier_ring_correlation() function on average positions per TID (.mat file)."""

    #
    # Fig1a_Tom70-Dreiklang_Minflux.mat
    #
    # From:
    #   * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    #   * [code]  https://zenodo.org/record/6563100

    minflux = loadmat(
        str(Path(__file__).parent / "data" / "Fig1a_Tom70-Dreiklang_Minflux.mat")
    )
    minflux = minflux["minflux"]

    # Extract tid, x and y coordinates
    tid = minflux["id"][0][0].ravel()
    pos = minflux["pos"][0][0][:, :2]

    # Calculate per-TID averages
    u_tid = np.unique(tid)
    m_pos = np.zeros((len(u_tid), 2), dtype=float)
    for i, t in enumerate(u_tid):
        m_pos[i, :] = pos[tid == t, :].mean(axis=0)

    # Now extract the mean x and y localizations
    x = m_pos[:, 0]
    y = m_pos[:, 1]

    # Ranges
    rx = (-372.5786, 318.8638)
    ry = (-1148.8, 1006.6)

    # Initialize the random number generator
    rng = np.random.default_rng(2023)

    N = 5
    expected_resolutions = np.array(
        [1.17647059e-08, 1.21212121e-08, 1.14942529e-08, 1.18343195e-08, 1.16279070e-08]
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


def test_fourier_ring_correlation_per_tid_mat_2(extract_raw_npy_data_files):
    """Test the analysis.img_fourier_ring_correlation() function on average positions per TID (.mat file)."""

    #
    # Fig1b_U2OS_Zyxin-rsEGFP2_Minflux.mat
    #
    # From:
    #   * [paper] Ostersehlt, L.M., Jans, D.C., Wittek, A. et al. DNA-PAINT MINFLUX nanoscopy. Nat Methods 19, 1072-1075 (2022). https://doi.org/10.1038/s41592-022-01577-1
    #   * [code]  https://zenodo.org/record/6563100

    minflux = loadmat(
        str(Path(__file__).parent / "data" / "Fig1b_U2OS_Zyxin-rsEGFP2_Minflux.mat")
    )
    minflux = minflux["minflux"]

    # Extract tid, x and y coordinates
    tid = minflux["id"][0][0].ravel()
    pos = minflux["pos"][0][0][:, :2]

    # Calculate per-TID averages
    u_tid = np.unique(tid)
    m_pos = np.zeros((len(u_tid), 2), dtype=float)
    for i, t in enumerate(u_tid):
        m_pos[i, :] = pos[tid == t, :].mean(axis=0)

    # Now extract the mean x and y localizations
    x = m_pos[:, 0]
    y = m_pos[:, 1]

    # Ranges
    rx = (-384.1294, 373.2787)
    ry = (-1142.8, 1068.0)

    # Initialize the random number generator
    rng = np.random.default_rng(2023)

    N = 5
    expected_resolutions = np.array(
        [4.83091787e-09, 4.79616307e-09, 4.72813239e-09, 5.26315789e-09, 5.10204082e-09]
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


def test_estimate_resolution(extract_raw_npy_data_files):
    """Test the estimate_resolution_frc() function on average positions per TID."""

    #
    # 2D_Only.npy
    #
    # min_trace_length = 1 (do not filter anything)

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

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

    # Work on averaged 2D data
    x = processor.filtered_dataframe_stats["mx"].values
    y = processor.filtered_dataframe_stats["my"].values

    # Expected values
    expected_resolution = 1.3880534697293937e-08
    expected_resolutions = np.array(
        [1.32450331e-08, 1.43884892e-08, 1.40845070e-08, 1.39860140e-08, 1.36986301e-08]
    )
    expected_qi = np.arange(0.0, 565500000.0 + 1.0, 500000.0)
    expected_ci_start = np.array(
        [
            0.93367428,
            0.91211924,
            0.8905642,
            0.86900916,
            0.8392228,
        ]
    )
    expected_ci_end = np.array(
        [
            -0.00959567,
            -0.00590168,
            -0.00505576,
            -0.00420984,
            -0.00336392,
        ]
    )
    expected_cis_start = np.array(
        [0.9341944, 0.93529632, 0.93558797, 0.93663346, 0.92665925]
    )
    expected_cis_end = np.array(
        [-0.02141162, -0.01228952, 0.01380745, -0.00017335, 0.00324745]
    )

    # Run the resolution estimation
    resolution, qi, ci, resolutions, cis = estimate_resolution_by_frc(
        x, y, rx=rx, ry=ry, num_reps=5, seed=2023, return_all=True
    )

    # Test
    assert np.isclose(resolution, expected_resolution), "Unexpected resolution."
    assert np.allclose(
        resolutions, expected_resolutions
    ), "Unexpected array of resolutions."
    assert np.isclose(
        expected_resolutions.mean(), expected_resolution
    ), "Unexpected resolution."
    assert np.allclose(expected_qi, qi), "Unexpected array of qis."
    assert np.allclose(expected_ci_start, ci[:5]), "Unexpected beginning of ci."
    assert np.allclose(expected_ci_end, ci[-5:]), "Unexpected end of ci."
    assert np.allclose(expected_cis_start, cis[0, :]), "Unexpected array of cis."
    assert np.allclose(expected_cis_end, cis[-1, :]), "Unexpected array of cis."
