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

from typing import Optional, Tuple, Union

import numpy as np


def fit_plane_least_squares(
    pos: np.ndarray, eps: float = 1e-10
) -> Tuple[float, float, float, float]:
    """Calculate the equation of the plane that best fits a set of 3D coordinates.

    The plane is defined by the equation Ax + By + Cz + D = 0.

    Parameters
    ----------
    pos: np.ndarray
        Array of 3D point coordinates with shape (N, 3) where each row is [x, y, z].

    eps: float, default=1e-10
        Tolerance for numerical comparisons and stability checks.

    Returns
    -------
    params: Tuple[float, float, float, float]
        The parameters of the plane equation [A, B, C, D] where Ax + By + Cz + D = 0.
        The normal vector [A, B, C] is guaranteed to be a unit vector.

    Raises
    ------
    ValueError
        If the input array doesn't have the correct shape, is empty, or if the points
        are nearly collinear (making plane fitting unreliable).
    """
    # Validate input
    if not isinstance(pos, np.ndarray):
        pos = np.array(pos, dtype=float)

    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError(f"Input array must have shape (N, 3), got {pos.shape}")

    if pos.shape[0] < 3:
        raise ValueError(
            f"At least 3 non-collinear points are required to fit a plane, got {pos.shape[0]}"
        )

    # Center the data
    centroid = np.mean(pos, axis=0)
    centered = pos - centroid

    try:
        # Calculate the normal vector using SVD
        # The right singular vectors (rows of Vt) are the principal directions
        # The last row corresponds to the direction of least variance (normal to the plane)
        _, s, Vt = np.linalg.svd(centered, full_matrices=False)

        # Check if points are nearly collinear by examining singular values
        if s[1] < eps * s[0]:
            raise ValueError("Points are nearly collinear, cannot fit a unique plane")

        # The normal vector is the last row of Vt
        normal = Vt[-1, :]

        # Ensure the normal has unit length
        normal /= np.linalg.norm(normal)
        A, B, C = normal

        # Compute D such that the plane passes through the centroid
        # For a plane Ax + By + Cz + D = 0 passing through point (x0, y0, z0):
        # D = -(A*x0 + B*y0 + C*z0)
        D = -np.dot(normal, centroid)

        # Ensure C is positive for consistency when converting to z = f(x,y) form
        if C < 0:
            A, B, C, D = -A, -B, -C, -D

        return A, B, C, D

    except np.linalg.LinAlgError:
        raise ValueError("SVD computation failed, check if points are valid")


def align_to_plane(
    pos: np.ndarray,
    plane_eq: Optional[Tuple[float, float, float, float]] = None,
    x_shift: Optional[float] = None,
    y_shift: Optional[float] = None,
    z_shift: Optional[float] = None,
    align_to_zero: bool = False,
    eps: float = 1e-10,
) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, Tuple[float, float, float, float]
]:
    """
    Aligns a 3D point cloud so that a specified or best-fitting plane becomes parallel to the xy-plane.
    The transformation rotates the point cloud around its center of mass.

    Parameters
    ----------
    pos: np.ndarray (N, 3)
        Input 3D points as an Nx3 array.

    plane_eq: tuple (A, B, C, D), optional
        If provided, defines the plane Ax + By + Cz + D = 0 to be aligned with the xy-plane.
        If not provided, the best-fitting plane is estimated via SVD.

    x_shift: float, optional
        If provided, this value is added to the x-coordinates of the aligned points.
        If None, the original x-coordinate of the centroid is preserved.

    y_shift: float, optional
        If provided, this value is added to the y-coordinates of the aligned points.
        If None, the original y-coordinate of the centroid is preserved.

    z_shift: float, optional
        If provided, this value is added to the z-coordinates of the aligned points.
        If None, the original z-coordinate of the centroid is preserved.

    align_to_zero: bool, default=False
        If True, the z-coordinate of the centroid will be set to 0 after alignment.
        This overrides the z_shift parameter.

    eps: float, default=1e-10
        Tolerance for numerical comparisons.

    Returns
    -------
    aligned: np.ndarray (N, 3)
        The transformed 3D points, where the plane is aligned with z = constant.

    R: np.ndarray (3, 3)
        The rotation matrix used to align the plane normal with the z-axis.

    centroid: np.ndarray (3,)
        The center of mass of the input point cloud (used as rotation origin).

    normal: np.ndarray (3,)
        The unit normal vector of the plane.

    plane_eq: tuple (A, B, C, D)
        The equation of the plane in the form Ax + By + Cz + D = 0.

    Raises
    ------
    ValueError
        If the input array doesn't have the correct shape or is empty.
    """
    # Validate input
    if not isinstance(pos, np.ndarray):
        pos = np.array(pos, dtype=float)

    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError(f"Input array must have shape (N, 3), got {pos.shape}")

    if pos.shape[0] < 1:
        raise ValueError("Input array must contain at least one point")

    # Calculate centroid once
    centroid = np.mean(pos, axis=0)

    # Estimate or use provided plane
    if plane_eq is not None:
        A, B, C, D = plane_eq
        normal = np.array([A, B, C], dtype=float)
        norm = np.linalg.norm(normal)
        if norm < eps:
            raise ValueError("Provided plane equation has a zero normal vector")
        normal /= norm
    else:
        # For plane estimation, we need at least 3 points
        if pos.shape[0] < 3:
            raise ValueError(
                f"At least 3 points are required to estimate a plane, got {pos.shape[0]}"
            )

        # Center the data for SVD
        centered = pos - centroid

        # Use SVD to find the normal vector (smallest singular value)
        try:
            _, s, Vt = np.linalg.svd(centered, full_matrices=False)
            # Check if the points are nearly collinear
            if s[1] < eps * s[0]:
                raise ValueError(
                    "Points are nearly collinear, cannot fit a unique plane"
                )

            normal = Vt[-1, :]
            # Ensure the normal has unit length
            normal /= np.linalg.norm(normal)
            A, B, C = normal
            D = -np.dot(normal, centroid)
        except np.linalg.LinAlgError:
            raise ValueError("SVD computation failed, check if points are valid")

    # Compute rotation to align normal to z-axis
    target = np.array([0, 0, 1])
    dot_product = np.dot(normal, target)

    # Check if normal is already aligned with target or its opposite
    if np.abs(dot_product) > 1 - eps:
        if dot_product > 0:
            # Already aligned with z-axis
            R = np.eye(3)
        else:
            # Aligned with -z-axis, rotate 180° around x-axis
            R = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    else:
        # Use the stable version of Rodrigues' rotation formula
        axis = np.cross(normal, target)
        axis /= np.linalg.norm(axis)

        cos_theta = dot_product
        sin_theta = np.linalg.norm(np.cross(normal, target))

        # Rodrigues' rotation formula
        K = np.array(
            [[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]]
        )
        R = np.eye(3) + sin_theta * K + (1 - cos_theta) * (K @ K)

    # Rotate around centroid
    centered = pos - centroid
    aligned = (R @ centered.T).T

    # Apply shifts
    if x_shift is not None:
        aligned[:, 0] += x_shift
    else:
        aligned[:, 0] += centroid[0]

    if y_shift is not None:
        aligned[:, 1] += y_shift
    else:
        aligned[:, 1] += centroid[1]

    if align_to_zero:
        # Set z to 0 (plane will be exactly at z=0)
        pass  # Don't add any z offset
    elif z_shift is not None:
        aligned[:, 2] += z_shift
    else:
        aligned[:, 2] += centroid[2]

    # Return the plane equation in the form Ax + By + Cz + D = 0
    plane_eq = (A, B, C, D)

    return aligned, R, centroid, normal, plane_eq


def recenter_xy(
    pos: np.ndarray, new_center: Union[Tuple[float, float], np.ndarray]
) -> np.ndarray:
    """
    Recenters the x and y coordinates of a point cloud to a new center.

    Parameters
    ----------
    pos : np.ndarray
        Input 3D points as an (N, 3) array.

    new_center : tuple or array-like
        The target (x, y) center for the point cloud.

    Returns
    -------
    shifted : np.ndarray
        Recentered point cloud as an (N, 3) array.

    Raises
    ------
    ValueError
        If the input array doesn't have the correct shape or is empty.
    """
    # Validate input
    if not isinstance(pos, np.ndarray):
        pos = np.array(pos, dtype=float)

    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError(f"Input array must have shape (N, 3), got {pos.shape}")

    if pos.shape[0] < 1:
        raise ValueError("Input array must contain at least one point")

    if len(new_center) != 2:
        raise ValueError(
            f"new_center must have 2 elements (x, y), got {len(new_center)}"
        )

    # Calculate current center
    current_center = np.mean(pos[:, :2], axis=0)

    # Calculate shift
    shift = np.array(new_center, dtype=float) - current_center

    # Create output array
    pos_shifted = pos.copy()

    # Apply shift to x and y coordinates
    pos_shifted[:, 0] += shift[0]
    pos_shifted[:, 1] += shift[1]

    return pos_shifted
