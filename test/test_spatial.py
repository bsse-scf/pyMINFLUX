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

import numpy as np

from pyminflux.spatial import align_to_plane, fit_plane_least_squares, recenter_xy


def test_fitting_points_to_plane_and_projecting():

    #
    # All points are on the z=0 plane
    #

    # Prepare data (x, y, z)
    pos = np.array([[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]])

    # Center of mass
    cm = np.mean(pos, axis=0)

    # Find the parameters of the plane equation
    A, B, C, D = fit_plane_least_squares(pos)
    assert np.isclose(A, 0.0), "Unexpected value for A."
    assert np.isclose(B, 0.0), "Unexpected value for B."
    assert np.isclose(C, 1.0), "Unexpected value for C."
    assert np.isclose(D, 0.0), "Unexpected value for D."

    # Align pos to the extracted plane
    aligned, R, est_centroid, normal, plane_eq_out = align_to_plane(
        pos, plane_eq=(A, B, C, D)
    )

    assert np.allclose(aligned, pos), "Unexpected transformation."
    assert np.allclose(R, np.eye(3)), "Unexpected transformation matrix."
    assert np.allclose(est_centroid, cm), "Unexpected centroid."
    assert np.allclose(plane_eq_out, (A, B, C, D)), "Unexpected plane equation."

    #
    # All points are on the z=0 plane, shifted in x
    #

    # Prepare data (x, y, z)
    pos = np.array([[10, 0, 0], [10, 1, 0], [11, 1, 0], [11, 0, 0]])

    # Center of mass
    cm = np.mean(pos, axis=0)

    # Find the parameters of the plane equation
    A, B, C, D = fit_plane_least_squares(pos)
    assert np.isclose(A, 0.0), "Unexpected value for A."
    assert np.isclose(B, 0.0), "Unexpected value for B."
    assert np.isclose(C, 1.0), "Unexpected value for C."
    assert np.isclose(D, 0.0), "Unexpected value for D."

    # Align pos to the extracted plane
    aligned, R, est_centroid, normal, plane_eq_out = align_to_plane(
        pos, plane_eq=(A, B, C, D)
    )

    assert np.allclose(aligned, pos), "Unexpected transformation."
    assert np.allclose(R, np.eye(3)), "Unexpected transformation matrix."
    assert np.allclose(est_centroid, cm), "Unexpected origin."
    assert np.allclose(plane_eq_out, (A, B, C, D)), "Unexpected plane equation."

    #
    # Points are on an inclined plane, shifted in x
    #

    # Prepare data (x, y, z)
    pos = np.array([[10, 5, 0], [10, 6, 0], [11, 6, 1], [11, 5, 1]])

    # Center of mass
    cm = np.mean(pos, axis=0)

    # Find the parameters of the plane equation
    A, B, C, D = fit_plane_least_squares(pos)
    assert np.isclose(A, -np.sqrt(2) / 2), "Unexpected value for A."
    assert np.isclose(B, 0), "Unexpected value for B."
    assert np.isclose(C, np.sqrt(2) / 2), "Unexpected value for C."
    assert np.isclose(D, 10 * np.sqrt(2) / 2), "Unexpected value for D."

    # Align pos to the extracted plane
    aligned, R, est_centroid, normal, plane_eq_out = align_to_plane(
        pos, plane_eq=(A, B, C, D)
    )

    # Expected transformed coordinates
    expected_aligned = np.array(
        [
            [9.792893218813452, 5.0, 0.5],
            [9.792893218813452, 6.0, 0.5],
            [11.207106781186548, 6.0, 0.5],
            [11.207106781186548, 5.0, 0.5],
        ]
    )

    # Expected rotation matrix
    expected_R = np.array(
        [
            [0.7071067811865476, 0.0, 0.7071067811865476],
            [0.0, 1.0, 0.0],
            [-0.7071067811865476, 0.0, 0.7071067811865476],
        ]
    )

    assert np.allclose(aligned, expected_aligned), "Unexpected transformation."
    assert np.allclose(R, expected_R), "Unexpected transformation matrix."
    assert np.allclose(est_centroid, cm), "Unexpected origin."
    assert np.allclose(plane_eq_out, (A, B, C, D)), "Unexpected plane equation."
    assert np.isclose(
        np.max(aligned[:, 2]) - np.min(aligned[:, 2]), 0.0
    ), "All points should be aligned with the z=0 plane."

    # Length of the original XZ stretch
    length_original_xz = np.sqrt(
        (pos[3, 0] - pos[0, 0]) ** 2 + (pos[3, 2] - pos[0, 2]) ** 2
    )

    # Length of the projected XZ stretch
    length_projected_xz = np.sqrt(
        (aligned[3, 0] - aligned[0, 0]) ** 2 + (aligned[3, 2] - aligned[0, 2]) ** 2
    )

    assert np.isclose(length_original_xz, length_projected_xz), (
        "Range should be " "preserved by " "rotation."
    )

    # Project two new points onto the fitted plane
    new_points = np.array(
        [
            [10.5, 5, 0.5],  # New point in the center (lying on the plane)
            [10.5, 5, 0.6],  # New point in the center, slightly higher
        ]
    )

    # Align new points to the extracted plane
    aligned_points, R_points, est_centroid, normal, plane_eq_out = align_to_plane(
        new_points, plane_eq=(A, B, C, D)
    )

    # Expected transformed coordinates
    expected_aligned_points = np.array(
        [
            [10.464644660940673, 5.0, 0.5146446609406726],
            [10.535355339059327, 5.0, 0.5853553390593274],
        ]
    )

    expected_R_points = np.array(
        [
            [0.7071067811865476, 0.0, 0.7071067811865476],
            [0.0, 1.0, 0.0],
            [-0.7071067811865476, 0.0, 0.7071067811865476],
        ]
    )

    assert np.allclose(
        aligned_points, expected_aligned_points
    ), "Unexpected transformation."
    assert np.allclose(R_points, expected_R_points), "Unexpected transformation matrix."

    # Rest recentering
    new_cm = (10.0, 15.0)
    recentered_pos = recenter_xy(aligned_points, new_cm)
    recentered_cm = np.mean(recentered_pos, axis=0)
    assert np.allclose(new_cm, recentered_cm[:2]), "Unexpected recentered coordinates."
