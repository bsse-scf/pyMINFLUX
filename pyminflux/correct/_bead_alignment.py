#  Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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

"""Bead-based alignment and registration utilities for MINFLUX datasets."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional, Dict


def _kabsch(P: np.ndarray, Q: np.ndarray, allow_reflection: bool = False):
    """
    Rigid (no scale) least-squares alignment using Kabsch algorithm.
    Find R, t such that R @ P + t ≈ Q.
    
    Args:
        P: (n, d) array of points to be aligned
        Q: (n, d) array of reference points
        allow_reflection: If False, enforce det(R) = +1
        
    Returns:
        R: (d, d) rotation matrix
        t: (d,) translation vector
    """
    assert P.shape == Q.shape
    Pc = P - P.mean(axis=0)
    Qc = Q - Q.mean(axis=0)
    H = Pc.T @ Qc
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if not allow_reflection and np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    t = Q.mean(axis=0) - R @ P.mean(axis=0)
    return R, t


class RigidTransform:
    """Simple rigid transformation model compatible with the existing interface."""
    
    def __init__(self, rotation: np.ndarray, translation: np.ndarray):
        """
        Initialize rigid transform.
        
        Args:
            rotation: (d, d) rotation matrix
            translation: (d,) translation vector
        """
        self.rotation = rotation
        self.translation = translation
        self.dimensionality = rotation.shape[0]
        
        # Build homogeneous transformation matrix for compatibility
        d = self.dimensionality
        self.params = np.eye(d + 1)
        self.params[:d, :d] = rotation
        self.params[:d, d] = translation
    
    def __call__(self, coords: np.ndarray) -> np.ndarray:
        """
        Apply transformation to coordinates.
        
        Args:
            coords: (n, d) array of coordinates
            
        Returns:
            Transformed coordinates (n, d)
        """
        return (self.rotation @ coords.T).T + self.translation
    
    def residuals(self, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
        """
        Calculate residuals between transformed source and destination.
        
        Args:
            src: (n, d) source points
            dst: (n, d) destination points
            
        Returns:
            (n,) array of residuals (Euclidean distances)
        """
        transformed = self(src)
        return np.linalg.norm(transformed - dst, axis=1)


class TranslationTransform:
    """Translation-only transformation model for cases with insufficient correspondences."""
    
    def __init__(self, translation: np.ndarray):
        """
        Initialize translation-only transform.
        
        Args:
            translation: (d,) translation vector
        """
        self.translation = translation
        self.dimensionality = translation.shape[0]
        
        # Build homogeneous transformation matrix for compatibility
        d = self.dimensionality
        self.params = np.eye(d + 1)
        self.params[:d, d] = translation
        
        # Store identity rotation for compatibility
        self.rotation = np.eye(d)
    
    def __call__(self, coords: np.ndarray) -> np.ndarray:
        """
        Apply transformation to coordinates.
        
        Args:
            coords: (n, d) array of coordinates
            
        Returns:
            Transformed coordinates (n, d)
        """
        return coords + self.translation
    
    def residuals(self, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
        """
        Calculate residuals between transformed source and destination.
        
        Args:
            src: (n, d) source points
            dst: (n, d) destination points
            
        Returns:
            (n,) array of residuals (Euclidean distances)
        """
        transformed = self(src)
        return np.linalg.norm(transformed - dst, axis=1)


def point_registration(
    pts_fixed: np.ndarray,
    pts_moving: np.ndarray,
    transform_type: str = 'euclidean',
) -> Optional[Union[RigidTransform, TranslationTransform]]:
    """
    Estimate transformation between two sets of corresponding points.
    
    For 3+ correspondences, the Kabsch algorithm is used for rigid alignment.
    When fewer than 3 correspondences are available, a translation-only transform is used.

    Args:
        pts_fixed (np.ndarray): The (N, D) array of points in the fixed coordinate system.
        pts_moving (np.ndarray): The (N, D) array of points in the moving coordinate system.
        transform_type (str): The type of transformation to estimate. 
                            Currently only 'euclidean' (rigid: rotation+translation) is supported.

    Returns:
        Optional[Union[RigidTransform, TranslationTransform]]: The estimated transformation model.
    """
    if transform_type.lower() != 'euclidean':
        raise ValueError("Only 'euclidean' transform type is currently supported.")
    
    n_points, d = pts_moving.shape
    
    if n_points < 1:
        raise ValueError(
            f"Not enough data points ({n_points}) for alignment. "
            f"At least 1 point is required."
        )
    
    if pts_fixed.shape != pts_moving.shape:
        raise ValueError(
            f"Point arrays must have the same shape. "
            f"Got pts_fixed: {pts_fixed.shape}, pts_moving: {pts_moving.shape}"
        )
    
    # Use translation-only transform for 1-2 correspondences
    if n_points < 3:
        # Compute mean translation
        t = pts_fixed.mean(axis=0) - pts_moving.mean(axis=0)
        
        # Create translation-only transformation model
        return TranslationTransform(t)
    
    # Compute optimal rigid transformation using Kabsch algorithm for 3+ correspondences
    R, t = _kabsch(pts_moving, pts_fixed, allow_reflection=False)
    
    # Create transformation model
    return RigidTransform(R, t)


def mbm_dict_to_dataframe(mbm_dict: Dict, additional_metadata: Optional[Dict] = None) -> pd.DataFrame:
    """
    Convert mbm_dict to a single pandas DataFrame.
    
    Args:
        mbm_dict: Dictionary containing bead measurement data
        additional_metadata: Optional dictionary of metadata to add as columns
        
    Returns:
        pd.DataFrame: Combined DataFrame with all bead data
    """
    dfs = []
    for bead_id, bead_data in mbm_dict.items():
        points = bead_data['points']

        # Convert structured array to DataFrame (except xyz first)
        df_points = pd.DataFrame({
            'gri': points['gri'],
            'tim': points['tim'],
            'str': points['str']
        })
        
        # Expand xyz
        xyz_df = pd.DataFrame(points['xyz'], columns=['x', 'y', 'z'])
        xyz_df *= 1e9  # Convert to nm
        df_points = pd.concat([df_points, xyz_df], axis=1)
        
        # Add metadata columns
        df_points['bead_name'] = bead_data['bead_name']
        df_points['bead_gri'] = bead_data['gri']
        df_points['used'] = bead_data['used']

        if additional_metadata:
            for key, value in additional_metadata.items():
                df_points[key] = value
        
        dfs.append(df_points)
    
    if not dfs:
        return pd.DataFrame()
    
    return pd.concat(dfs, ignore_index=True)


def align_datasets_using_beads(
    reference_mbm_dict: Dict,
    moving_mbm_dict: Dict,
    bead_correspondence: Optional[Dict[str, str]] = None,
    transform_type: str = 'euclidean',
    n_points: Optional[int] = 3,
) -> Optional[object]:
    """
    Align two datasets using bead localizations.
    
    Args:
        reference_mbm_dict: MBM dictionary from reference dataset
        moving_mbm_dict: MBM dictionary from dataset to be aligned
        bead_correspondence: Optional dict mapping moving bead names to reference bead names.
                           If None, assumes beads with same names correspond.
        transform_type: Type of transformation ('euclidean' or 'affine')
        n_points: Number of earliest time points to average per bead
        
    Returns:
        model: The transformation model, or None if alignment fails
    """
    # Create dataframes from mbm dicts
    df_ref = mbm_dict_to_dataframe(reference_mbm_dict, additional_metadata={'type': 'reference'})
    df_mov = mbm_dict_to_dataframe(moving_mbm_dict, additional_metadata={'type': 'moving'})
    
    if df_ref.empty or df_mov.empty:
        print("Error: One or both datasets have no bead data.")
        return None
    
    # Filter to only include beads marked as "used"
    df_ref = df_ref[df_ref['used'] == True]
    df_mov = df_mov[df_mov['used'] == True]
    
    if df_ref.empty or df_mov.empty:
        print("Error: No beads marked as 'used' in one or both datasets.")
        return None
    
    # Identify beads to use for alignment
    if bead_correspondence is None:
        # Automatic: use beads with matching names
        common_beads_ref = set(df_ref['bead_name'])
        common_beads_mov = set(df_mov['bead_name'])
        common_beads = common_beads_ref.intersection(common_beads_mov)
        
        if not common_beads:
            print("Error: No common beads found between datasets.")
            return None
        
        # Create identity mapping
        bead_correspondence = {bn: bn for bn in common_beads}
    else:
        # Manual correspondence provided
        # Validate that all beads exist
        missing_ref = set(bead_correspondence.values()) - set(df_ref['bead_name'])
        missing_mov = set(bead_correspondence.keys()) - set(df_mov['bead_name'])
        
        if missing_ref:
            print(f"Warning: Reference beads not found: {missing_ref}")
        if missing_mov:
            print(f"Warning: Moving beads not found: {missing_mov}")
        
        # Filter to only valid correspondences
        bead_correspondence = {
            mov: ref for mov, ref in bead_correspondence.items()
            if mov in set(df_mov['bead_name']) and ref in set(df_ref['bead_name'])
        }
        
        if not bead_correspondence:
            print("Error: No valid bead correspondences.")
            return None
    
    print(f"Using {len(bead_correspondence)} bead pairs for alignment")
    
    # Calculate average positions for each bead (using earliest n_points)
    def get_bead_position(df, bead_name, n_points):
        bead_data = df[df['bead_name'] == bead_name]
        if len(bead_data) == 0:
            return None
        # Get n_points with smallest tim values
        earliest = bead_data.nsmallest(n_points, 'tim')
        # Return mean position as [z, y, x] for consistency with original code
        return earliest[['z', 'y', 'x']].mean(axis=0).to_numpy()
    
    # Build point clouds
    pts_ref = []
    pts_mov = []
    used_beads = []
    
    for bead_mov, bead_ref in bead_correspondence.items():
        pos_ref = get_bead_position(df_ref, bead_ref, n_points)
        pos_mov = get_bead_position(df_mov, bead_mov, n_points)
        
        if pos_ref is not None and pos_mov is not None:
            pts_ref.append(pos_ref)
            pts_mov.append(pos_mov)
            used_beads.append((bead_ref, bead_mov))
    
    if len(pts_ref) < 1:
        print(f"Error: Not enough valid bead pairs ({len(pts_ref)}).")
        return None
    
    pts_ref = np.array(pts_ref)
    pts_mov = np.array(pts_mov)
    
    print(f"Aligning using {len(pts_ref)} bead positions")
    
    # Warn if using translation-only mode
    if len(pts_ref) < 3:
        print(f"Warning: Only {len(pts_ref)} bead pair(s) available. Using translation-only alignment.")
    
    # Execute alignment
    try:
        model = point_registration(
            pts_ref,
            pts_mov,
            transform_type=transform_type,
        )
    except Exception as e:
        print(f"Error during registration: {e}")
        return None
    
    if model is None:
        print("Registration failed.")
        return None
    
    # Calculate residuals
    residuals = model.residuals(pts_mov, pts_ref)
    residual_mean = np.mean(residuals)
    residual_before = np.mean(np.linalg.norm(pts_mov - pts_ref, axis=1))
    
    alignment_mode = "translation-only" if len(pts_ref) < 3 else "rigid (rotation + translation)"
    print(f"Alignment completed using {alignment_mode} mode.")
    print(f"Mean residual: {residual_mean:.2f} nm.")
    print(f"Mean residual before alignment: {residual_before:.2f} nm.")
    
    return model
