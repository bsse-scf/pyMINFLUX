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
