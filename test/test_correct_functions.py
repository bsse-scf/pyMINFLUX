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

from pyminflux.correct import (
    drift_correction_time_windows_2d,
    drift_correction_time_windows_3d,
)


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


def test_estimate_drift_2d_mat(extract_raw_npy_data_files):
    """Test the drift_correction_time_windows_2d() (.mat file)."""

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
    t = minflux["t"][0][0].ravel()
    tid = minflux["id"][0][0].ravel()
    pos = minflux["pos"][0][0][:, :2]
    x = pos[:, 0]
    y = pos[:, 1]

    # Spatial ranges
    rx = (-372.5786, 318.8638)
    ry = (-1148.8, 1006.6)

    # Resolution
    sxy = 2

    # Run the 2D drift correction
    dx, dy, dxt, dyt, ti, T = drift_correction_time_windows_2d(
        x, y, t, sxy=sxy, rx=rx, ry=ry, T=None, tid=tid
    )

    # Expected values
    expected_dx_first = -2.205576196850738
    expected_dx_last = -2.6063570587906
    expected_dx_mean = -0.5332977272042978
    expected_dx_std = 1.127749604233301
    expected_dy_first = 0.5048935277587024
    expected_dy_last = -6.146428606993543
    expected_dy_mean = -0.7935001517529221
    expected_dy_std = 2.1620576306028627
    expected_dxt_first = -1.1380796890409761
    expected_dxt_last = -0.2583248964485968
    expected_dxt_mean = --3.700743415417188e-17
    expected_dxt_std = 1.0506986401293645
    expected_dyt_first = 0.6992655740052406
    expected_dyt_last = -1.8600154629624202
    expected_dyt_mean = 0.0
    expected_dyt_std = 1.3286547294365443
    expected_ti_first = 408.04229843745696
    expected_ti_last = 2323.9221509099357
    expected_ti_mean = 1369.5979313605085
    expected_ti_std = 782.1713888409313
    expected_T = 931.95612141632

    # Test
    assert np.isclose(expected_dx_first, dx[0]), "Unexpected value for dx[0]."
    assert np.isclose(expected_dx_last, dx[-1]), "Unexpected value for dx[-1]."
    assert np.isclose(expected_dx_mean, dx.mean()), "Unexpected value for dx.mean()."
    assert np.isclose(expected_dx_std, dx.std()), "Unexpected value for dx.std()."
    assert len(dx) == len(x), "Unexpected length of vector x."
    assert np.isclose(expected_dy_first, dy[0]), "Unexpected value for dy[0]."
    assert np.isclose(expected_dy_last, dy[-1]), "Unexpected value for dy[-1]."
    assert np.isclose(expected_dy_mean, dy.mean()), "Unexpected value for dy.mean()."
    assert np.isclose(expected_dy_std, dy.std()), "Unexpected value for dy.std()."
    assert len(dy) == len(y), "Unexpected length of vector y."
    assert np.isclose(expected_dxt_first, dxt[0]), "Unexpected value for dxt[0]."
    assert np.isclose(expected_dxt_last, dxt[-1]), "Unexpected value for dxt[-1]."
    assert np.isclose(expected_dxt_mean, dxt.mean()), "Unexpected value for dxt.mean()."
    assert np.isclose(expected_dxt_std, dxt.std()), "Unexpected value for dxt.std()."
    assert len(dxt) == 3, "Unexpected length of vector dxt."
    assert np.isclose(expected_dyt_first, dyt[0]), "Unexpected value for dyt[0]."
    assert np.isclose(expected_dyt_last, dyt[-1]), "Unexpected value for dyt[-1]."
    assert np.isclose(expected_dyt_mean, dyt.mean()), "Unexpected value for dyt.mean()."
    assert np.isclose(expected_dyt_std, dyt.std()), "Unexpected value for dyt.std()."
    assert len(dyt) == 3, "Unexpected length of vector dyt."
    assert np.isclose(expected_ti_first, ti[0]), "Unexpected value for ti[0]."
    assert np.isclose(expected_ti_last, ti[-1]), "Unexpected value for ti[-1]."
    assert np.isclose(expected_ti_mean, ti.mean()), "Unexpected value for ti.mean()."
    assert np.isclose(expected_ti_std, ti.std()), "Unexpected value for ti.std()."
    assert len(ti) == 3, "Unexpected length of vector ti."
    assert np.isclose(expected_T, T), "Unexpected value for T."


def test_estimate_drift_3d_mat(extract_raw_npy_data_files):
    """Test the drift_correction_time_windows_3d() (.mat file)."""

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

    # Extract tid, x and y coordinates
    tid = df["tid"].values
    t = df["t"].values
    pos = df[["x", "y", "z"]].values
    x = pos[:, 0]
    y = pos[:, 1]
    z = pos[:, 2]

    # Spatial ranges
    rx = (-434.5609880335669, 367.8659119806681)
    ry = (-1419.260678440071, 1801.300331041331)
    rz = (-298.8539888427734, 90.5609084228519)

    # Resolution
    sxyz = 5

    # Run the 3D drift correction
    dx, dy, dz, dxt, dyt, dzt, ti, T = drift_correction_time_windows_3d(
        x, y, z, t, sxyz=sxyz, rx=rx, ry=ry, rz=rz, T=None, tid=tid
    )

    # Expected values
    expected_dx_first = -12.460331273589698
    expected_dx_last = 8.009857008956743
    expected_dx_mean = 0.12864066343930008
    expected_dx_std = 6.589954694613107
    expected_dy_first = -16.152128169189766
    expected_dy_last = -1.152773064395448
    expected_dy_mean = -0.37461486256391596
    expected_dy_std = 6.095210550804399
    expected_dz_first = 13.232820104945795
    expected_dz_last = -2.9932534950048657
    expected_dz_mean = 0.041667510696429745
    expected_dz_std = 4.2692515907552275
    expected_dxt_first = -9.95465834929504
    expected_dxt_last = 2.972418827846476
    expected_dxt_mean = -1.4802973661668753e-16
    expected_dxt_std = 7.2929282507913955
    expected_dyt_first = -5.7636122896077016
    expected_dyt_last = 0.942048756110978
    expected_dyt_mean = -8.881784197001252e-16
    expected_dyt_std = 7.635781016019981
    expected_dzt_first = 7.7740114838398675
    expected_dzt_last = -0.6201522141642668
    expected_dzt_mean = 2.9605947323337506e-16
    expected_dzt_std = 4.080956847532348
    expected_ti_first = 304.6190898888952
    expected_ti_last = 3318.4362150106745
    expected_ti_mean = 1800.214133149516
    expected_ti_std = 1042.0108734263977
    expected_T = 600.0

    # Test
    assert np.isclose(expected_dx_first, dx[0]), "Unexpected value for dx[0]."
    assert np.isclose(expected_dx_last, dx[-1]), "Unexpected value for dx[-1]."
    assert np.isclose(expected_dx_mean, dx.mean()), "Unexpected value for dx.mean()."
    assert np.isclose(expected_dx_std, dx.std()), "Unexpected value for dx.std()."
    assert len(dx) == len(x), "Unexpected length of vector x."
    assert np.isclose(expected_dy_first, dy[0]), "Unexpected value for dy[0]."
    assert np.isclose(expected_dy_last, dy[-1]), "Unexpected value for dy[-1]."
    assert np.isclose(expected_dy_mean, dy.mean()), "Unexpected value for dy.mean()."
    assert np.isclose(expected_dy_std, dy.std()), "Unexpected value for dy.std()."
    assert len(dy) == len(y), "Unexpected length of vector y."
    assert np.isclose(expected_dz_first, dz[0]), "Unexpected value for dz[0]."
    assert np.isclose(expected_dz_last, dz[-1]), "Unexpected value for dz[-1]."
    assert np.isclose(expected_dz_mean, dz.mean()), "Unexpected value for dz.mean()."
    assert np.isclose(expected_dz_std, dz.std()), "Unexpected value for dz.std()."
    assert len(dz) == len(z), "Unexpected length of vector z."
    assert np.isclose(expected_dxt_first, dxt[0]), "Unexpected value for dxt[0]."
    assert np.isclose(expected_dxt_last, dxt[-1]), "Unexpected value for dxt[-1]."
    assert np.isclose(expected_dxt_mean, dxt.mean()), "Unexpected value for dxt.mean()."
    assert np.isclose(expected_dxt_std, dxt.std()), "Unexpected value for dxt.std()."
    assert len(dxt) == 6, "Unexpected length of vector dxt."
    assert np.isclose(expected_dyt_first, dyt[0]), "Unexpected value for dyt[0]."
    assert np.isclose(expected_dyt_last, dyt[-1]), "Unexpected value for dyt[-1]."
    assert np.isclose(expected_dyt_mean, dyt.mean()), "Unexpected value for dyt.mean()."
    assert np.isclose(expected_dyt_std, dyt.std()), "Unexpected value for dyt.std()."
    assert len(dyt) == 6, "Unexpected length of vector dyt."
    assert np.isclose(expected_dzt_first, dzt[0]), "Unexpected value for dzt[0]."
    assert np.isclose(expected_dzt_last, dzt[-1]), "Unexpected value for dzt[-1]."
    assert np.isclose(expected_dzt_mean, dzt.mean()), "Unexpected value for dzt.mean()."
    assert np.isclose(expected_dzt_std, dzt.std()), "Unexpected value for dzt.std()."
    assert len(dyt) == 6, "Unexpected length of vector dyt."
    assert np.isclose(expected_ti_first, ti[0]), "Unexpected value for ti[0]."
    assert np.isclose(expected_ti_last, ti[-1]), "Unexpected value for ti[-1]."
    assert np.isclose(expected_ti_mean, ti.mean()), "Unexpected value for ti.mean()."
    assert np.isclose(expected_ti_std, ti.std()), "Unexpected value for ti.std()."
    assert len(ti) == 6, "Unexpected length of vector ti."
    assert np.isclose(expected_T, T), "Unexpected value for T."


def test_coordinate_processing():
    """Test the way coordinates are processed."""

    # Coordinates
    x = np.arange(1, 100, 5).astype(np.float32)
    y = np.arange(1, 100, 5).astype(np.float32)
    z = np.arange(1, 100, 5).astype(np.float32)

    # Range to consider
    rx = (10.0, 90.0)
    ry = (10.0, 90.0)
    rz = (10.0, 90.0)

    #
    # First resolution, no kernel
    #

    # Resolution (nm)
    sx = 2.0
    sy = 2.0
    sz = 5.0

    # Get target image dimension
    nx = int(np.ceil((rx[1] - rx[0]) / sx))
    ny = int(np.ceil((ry[1] - ry[0]) / sy))
    nz = int(np.ceil((rz[1] - rz[0]) / sz))

    # Get position in pixels
    px = (x - rx[0]) / sx
    py = (y - ry[0]) / sy
    pz = (z - rz[0]) / sz

    # Convert absolute position to image indices
    ix = np.round(px).astype(int)
    iy = np.round(py).astype(int)
    iz = np.round(pz).astype(int)

    # Remove positions outside the image
    m = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny) & (iz >= 0) & (iz < nz)
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Flip iy to have 0 at the top
    f_iy = ny - iy - 1

    # Try placing all entries in the image
    success = True
    h = np.zeros((nz, ny, nx), dtype=np.float32)
    for i in range(len(ix)):
        xi = ix[i]
        yi = f_iy[i]  # Images have y = 0 at the top
        zi = iz[i]
        try:
            h[zi, yi, xi] += 1
        except IndexError as _:
            success = False
            break

    # Expected values
    expected_success = True
    expected_x = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_y = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_z = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_nx = 40
    expected_ny = 40
    expected_nz = 16
    expected_px = np.array(
        [
            0.5,
            3.0,
            5.5,
            8.0,
            10.5,
            13.0,
            15.5,
            18.0,
            20.5,
            23.0,
            25.5,
            28.0,
            30.5,
            33.0,
            35.5,
            38.0,
        ]
    )
    expected_py = np.array(
        [
            0.5,
            3.0,
            5.5,
            8.0,
            10.5,
            13.0,
            15.5,
            18.0,
            20.5,
            23.0,
            25.5,
            28.0,
            30.5,
            33.0,
            35.5,
            38.0,
        ]
    )
    expected_pz = np.array(
        [
            0.2,
            1.2,
            2.2,
            3.2,
            4.2,
            5.2,
            6.2,
            7.2,
            8.2,
            9.2,
            10.2,
            11.2,
            12.2,
            13.2,
            14.2,
            15.2,
        ]
    )
    expected_ix = np.array([0, 3, 6, 8, 10, 13, 16, 18, 20, 23, 26, 28, 30, 33, 36, 38])
    expected_iy = np.array([0, 3, 6, 8, 10, 13, 16, 18, 20, 23, 26, 28, 30, 33, 36, 38])
    expected_iz = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    expected_f_iy = np.array(
        [[39, 36, 33, 31, 29, 26, 23, 21, 19, 16, 13, 11, 9, 6, 3, 1]]
    )
    expected_m = np.array(
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
    ).astype(bool)

    # Test
    assert expected_success == success, "Could not write all pixels in the image."
    assert np.allclose(expected_x, x), "Unexpected array y."
    assert np.allclose(expected_y, x), "Unexpected array y."
    assert np.allclose(expected_z, x), "Unexpected array y."
    assert expected_nx == nx, "Unexpected value for nx."
    assert expected_ny == ny, "Unexpected value for ny."
    assert expected_nz == nz, "Unexpected value for nZ."
    assert np.allclose(expected_px, px), "Unexpected array px."
    assert np.allclose(expected_py, py), "Unexpected array py."
    assert np.allclose(expected_pz, pz), "Unexpected array pz."
    assert np.allclose(expected_ix, ix), "Unexpected array ix."
    assert np.allclose(expected_iy, iy), "Unexpected array iy."
    assert np.allclose(expected_iz, iz), "Unexpected array iz."
    assert np.allclose(expected_f_iy, f_iy), "Unexpected array f_iy."
    assert np.allclose(expected_m, m), "Unexpected array y."

    #
    # Second resolution, no kernel
    #

    # Resolution (nm)
    sx = 2.5
    sy = 2.5
    sz = 5.0

    # Get target image dimension
    nx = int(np.ceil((rx[1] - rx[0]) / sx))
    ny = int(np.ceil((ry[1] - ry[0]) / sy))
    nz = int(np.ceil((rz[1] - rz[0]) / sz))

    # Get position in pixels
    px = (x - rx[0]) / sx
    py = (y - ry[0]) / sy
    pz = (z - rz[0]) / sz

    # Convert absolute position to image indices
    ix = np.round(px).astype(int)
    iy = np.round(py).astype(int)
    iz = np.round(pz).astype(int)

    # Remove positions outside the image
    m = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny) & (iz >= 0) & (iz < nz)
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Flip iy to have 0 at the top
    f_iy = ny - iy - 1

    # Try placing all entries in the image
    success = True
    h = np.zeros((nz, ny, nx), dtype=np.float32)
    for i in range(len(ix)):
        xi = ix[i]
        yi = f_iy[i]  # Images have y = 0 at the top
        zi = iz[i]
        try:
            h[zi, yi, xi] += 1
        except IndexError as _:
            success = False
            break

    # Expected values
    expected_success = True
    expected_x = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_y = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_z = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_nx = 32
    expected_ny = 32
    expected_nz = 16
    expected_px = np.array(
        [
            0.4,
            2.4,
            4.4,
            6.4,
            8.4,
            10.4,
            12.4,
            14.4,
            16.4,
            18.4,
            20.4,
            22.4,
            24.4,
            26.4,
            28.4,
            30.4,
        ]
    )
    expected_py = np.array(
        [
            0.4,
            2.4,
            4.4,
            6.4,
            8.4,
            10.4,
            12.4,
            14.4,
            16.4,
            18.4,
            20.4,
            22.4,
            24.4,
            26.4,
            28.4,
            30.4,
        ]
    )
    expected_pz = np.array(
        [
            0.2,
            1.2,
            2.2,
            3.2,
            4.2,
            5.2,
            6.2,
            7.2,
            8.2,
            9.2,
            10.2,
            11.2,
            12.2,
            13.2,
            14.2,
            15.2,
        ]
    )
    expected_ix = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])
    expected_iy = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])
    expected_iz = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    expected_f_iy = np.array(
        [31, 29, 27, 25, 23, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1]
    )
    expected_m = np.array(
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
    ).astype(bool)

    # Test
    assert expected_success == success, "Could not write all pixels in the image."
    assert np.allclose(expected_x, x), "Unexpected array y."
    assert np.allclose(expected_y, x), "Unexpected array y."
    assert np.allclose(expected_z, x), "Unexpected array y."
    assert expected_nx == nx, "Unexpected value for nx."
    assert expected_ny == ny, "Unexpected value for ny."
    assert expected_nz == nz, "Unexpected value for nZ."
    assert np.allclose(expected_px, px), "Unexpected array px."
    assert np.allclose(expected_py, py), "Unexpected array py."
    assert np.allclose(expected_pz, pz), "Unexpected array pz."
    assert np.allclose(expected_ix, ix), "Unexpected array ix."
    assert np.allclose(expected_iy, iy), "Unexpected array iy."
    assert np.allclose(expected_iz, iz), "Unexpected array iz."
    assert np.allclose(expected_f_iy, f_iy), "Unexpected array f_iy."
    assert np.allclose(expected_m, m), "Unexpected array y."

    #
    # Third resolution with kernel
    #

    # Resolution (nm)
    sx = 2.0
    sy = 2.0
    sz = 5.0

    # Kernel half-size
    L = 3

    # Get target image dimension
    nx = int(np.ceil((rx[1] - rx[0]) / sx))
    ny = int(np.ceil((ry[1] - ry[0]) / sy))
    nz = int(np.ceil((rz[1] - rz[0]) / sz))

    # Get position in pixels
    px = (x - rx[0]) / sx
    py = (y - ry[0]) / sy
    pz = (z - rz[0]) / sz

    # Convert absolute position to image indices
    ix = np.round(px).astype(int)
    iy = np.round(py).astype(int)
    iz = np.round(pz).astype(int)

    # Remove positions outside the image
    m = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny) & (iz >= 0) & (iz < nz)
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Now apply the kernel filter (as a subsequent step to replicate the use in pymnflux.analysis)
    m = (
        (ix >= L)
        & (ix < nx - L)
        & (iy >= L)
        & (iy < ny - L)
        & (iz >= L)
        & (iz < nz - L)
    )
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Flip iy to have 0 at the top
    f_iy = ny - iy - 1

    # Try placing all entries in the image
    success = True
    h = np.zeros((nz, ny, nx), dtype=np.float32)
    for i in range(len(ix)):
        xi = ix[i]
        yi = f_iy[i]  # Images have y = 0 at the top
        zi = iz[i]
        try:
            h[zi, yi, xi] += 1
        except IndexError as _:
            success = False
            break

    # Expected values
    expected_success = True
    expected_x = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_y = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_z = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_nx = 40
    expected_ny = 40
    expected_nz = 16
    expected_px = np.array([8.0, 10.5, 13.0, 15.5, 18.0, 20.5, 23.0, 25.5, 28.0, 30.5])
    expected_py = np.array([8.0, 10.5, 13.0, 15.5, 18.0, 20.5, 23.0, 25.5, 28.0, 30.5])
    expected_pz = np.array([3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2, 12.2])
    expected_ix = np.array([8, 10, 13, 16, 18, 20, 23, 26, 28, 30])
    expected_iy = np.array([8, 10, 13, 16, 18, 20, 23, 26, 28, 30])
    expected_iz = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    expected_f_iy = np.array([31, 29, 26, 23, 21, 19, 16, 13, 11, 9])
    expected_m = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]).astype(bool)

    # Test
    assert expected_success == success, "Could not write all pixels in the image."
    assert np.allclose(expected_x, x), "Unexpected array y."
    assert np.allclose(expected_y, x), "Unexpected array y."
    assert np.allclose(expected_z, x), "Unexpected array y."
    assert expected_nx == nx, "Unexpected value for nx."
    assert expected_ny == ny, "Unexpected value for ny."
    assert expected_nz == nz, "Unexpected value for nZ."
    assert np.allclose(expected_px, px), "Unexpected array px."
    assert np.allclose(expected_py, py), "Unexpected array py."
    assert np.allclose(expected_pz, pz), "Unexpected array pz."
    assert np.allclose(expected_ix, ix), "Unexpected array ix."
    assert np.allclose(expected_iy, iy), "Unexpected array iy."
    assert np.allclose(expected_iz, iz), "Unexpected array iz."
    assert np.allclose(expected_f_iy, f_iy), "Unexpected array f_iy."
    assert np.allclose(expected_m, m), "Unexpected array y."

    #
    # Fourth resolution with kernel
    #

    # Resolution (nm)
    sx = 2.5
    sy = 2.5
    sz = 5.0

    # Kernel half-size
    L = 3

    # Get target image dimension
    nx = int(np.ceil((rx[1] - rx[0]) / sx))
    ny = int(np.ceil((ry[1] - ry[0]) / sy))
    nz = int(np.ceil((rz[1] - rz[0]) / sz))

    # Get position in pixels
    px = (x - rx[0]) / sx
    py = (y - ry[0]) / sy
    pz = (z - rz[0]) / sz

    # Convert absolute position to image indices
    ix = np.round(px).astype(int)
    iy = np.round(py).astype(int)
    iz = np.round(pz).astype(int)

    # Remove positions outside the image
    m = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny) & (iz >= 0) & (iz < nz)
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Now apply the kernel filter (as a subsequent step to replicate the use in pymnflux.analysis)
    m = (
        (ix >= L)
        & (ix < nx - L)
        & (iy >= L)
        & (iy < ny - L)
        & (iz >= L)
        & (iz < nz - L)
    )
    px = px[m]
    py = py[m]
    pz = pz[m]
    ix = ix[m]
    iy = iy[m]
    iz = iz[m]

    # Flip iy to have 0 at the top
    f_iy = ny - iy - 1

    # Try placing all entries in the image
    success = True
    h = np.zeros((nz, ny, nx), dtype=np.float32)
    for i in range(len(ix)):
        xi = ix[i]
        yi = f_iy[i]  # Images have y = 0 at the top
        zi = iz[i]
        try:
            h[zi, yi, xi] += 1
        except IndexError as _:
            success = False
            break

    # Expected values
    expected_success = True
    expected_x = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_y = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_z = np.array(
        [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61, 66, 71, 76, 81, 86, 91, 96]
    )
    expected_nx = 32
    expected_ny = 32
    expected_nz = 16
    expected_px = np.array([6.4, 8.4, 10.4, 12.4, 14.4, 16.4, 18.4, 20.4, 22.4, 24.4])
    expected_py = np.array([6.4, 8.4, 10.4, 12.4, 14.4, 16.4, 18.4, 20.4, 22.4, 24.4])
    expected_pz = np.array([3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2, 12.2])
    expected_ix = np.array([6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    expected_iy = np.array([6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    expected_iz = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    expected_f_iy = np.array([25, 23, 21, 19, 17, 15, 13, 11, 9, 7])
    expected_m = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]).astype(bool)

    # Test
    assert expected_success == success, "Could not write all pixels in the image."
    assert np.allclose(expected_x, x), "Unexpected array y."
    assert np.allclose(expected_y, x), "Unexpected array y."
    assert np.allclose(expected_z, x), "Unexpected array y."
    assert expected_nx == nx, "Unexpected value for nx."
    assert expected_ny == ny, "Unexpected value for ny."
    assert expected_nz == nz, "Unexpected value for nZ."
    assert np.allclose(expected_px, px), "Unexpected array px."
    assert np.allclose(expected_py, py), "Unexpected array py."
    assert np.allclose(expected_pz, pz), "Unexpected array pz."
    assert np.allclose(expected_ix, ix), "Unexpected array ix."
    assert np.allclose(expected_iy, iy), "Unexpected array iy."
    assert np.allclose(expected_iz, iz), "Unexpected array iz."
    assert np.allclose(expected_f_iy, f_iy), "Unexpected array f_iy."
    assert np.allclose(expected_m, m), "Unexpected array y."
