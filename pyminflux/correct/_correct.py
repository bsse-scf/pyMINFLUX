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
from typing import Optional

import numpy as np
from numpy.fft import ifftshift
from scipy.fft import fftn, ifftn
from scipy.interpolate import interp1d
from scipy.optimize import minimize

from pyminflux.render import render_xy, render_xyz


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

    # Apply to the time points used to estimate the correction
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

    # Apply to the time points used to estimate the correction
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
