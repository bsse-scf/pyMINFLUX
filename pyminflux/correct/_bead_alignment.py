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
from skimage.measure import ransac
from skimage.transform import EuclideanTransform, AffineTransform
from typing import Tuple, Union, Optional, Dict
from matplotlib import pyplot as plt


def robust_point_cloud_registration(
    pts_fixed: np.ndarray,
    pts_moving: np.ndarray,
    transform_type: str = 'euclidean',
    residual_threshold: float = 0.1,
    max_trials: int = 1000
) -> Tuple[np.ndarray, np.ndarray, int, Optional[object]]:
    """
    Robustly estimates a geometric transformation between two sets of corresponding points
    using the RANSAC (Random Sample Consensus) algorithm from scikit-image.

    The primary output is the estimated homogeneous transformation matrix.

    Args:
        pts_fixed (np.ndarray): The (N, D) array of points in the fixed coordinate system.
        pts_moving (np.ndarray): The (N, D) array of points in the moving coordinate system.
        transform_type (str): The type of transformation to estimate. 
                            Options: 'euclidean' (rigid: rotation+translation) or 
                            'affine' (rotation+translation+scale+shear). 
                            Defaults to 'euclidean'.
        residual_threshold (float): Maximum distance for a point pair to be considered 
                                    an 'inlier' to the model. Defaults to 0.1.
        max_trials (int): Maximum number of RANSAC iterations. Defaults to 1000.

    Returns:
        Tuple[np.ndarray, np.ndarray, int, Optional[object]]:
            - H (np.ndarray): The (D+1, D+1) homogeneous transformation matrix.
            - inliers_mask (np.ndarray): A boolean mask indicating the inlier correspondences.
            - num_inliers (int): The total count of inliers.
            - model (Optional[object]): The estimated scikit-image transform model object.
    """
    # 1. Select the appropriate scikit-image Transform class and minimum samples
    if transform_type.lower() == 'euclidean':
        model_class = EuclideanTransform
        # EuclideanTransform needs 2 points in 2D or 3 points in 3D
        min_samples = pts_moving.shape[1] 
    elif transform_type.lower() == 'affine':
        model_class = AffineTransform
        # AffineTransform needs 3 points in 2D or 4 points in 3D
        min_samples = pts_moving.shape[1] + 1 
    else:
        raise ValueError("Invalid transform_type. Choose 'euclidean' or 'affine'.")

    # Ensure min_samples is valid given the data size
    if pts_moving.shape[0] < min_samples or pts_fixed.shape[0] < min_samples:
        raise ValueError(
            f"Not enough data points ({pts_moving.shape[0]}) for the selected "
            f"transformation type ({transform_type.upper()}), which requires "
            f"{min_samples} samples."
        )

    # 2. Run RANSAC to robustly estimate the transformation
    model_robust, inliers = ransac(
        (pts_moving, pts_fixed),
        model_class,
        min_samples=min_samples,
        residual_threshold=residual_threshold,
        max_trials=max_trials
    )

    if model_robust is None:
        print("RANSAC failed to find a robust model.")
        return np.eye(pts_moving.shape[1] + 1), np.zeros(pts_moving.shape[0], dtype=bool), 0, None

    # 3. Extract results
    H = model_robust.params 
    num_inliers = np.sum(inliers)
    
    return H, inliers, num_inliers, model_robust


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
    qc_plot_path: Optional[Path] = None
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
        qc_plot_path: Optional path to save QC plots
        
    Returns:
        model: The transformation model, or None if alignment fails
    """
    # Create dataframes from mbm dicts
    df_ref = mbm_dict_to_dataframe(reference_mbm_dict, additional_metadata={'type': 'reference'})
    df_mov = mbm_dict_to_dataframe(moving_mbm_dict, additional_metadata={'type': 'moving'})
    
    if df_ref.empty or df_mov.empty:
        print("Error: One or both datasets have no bead data.")
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
    
    if len(pts_ref) < 2:
        print(f"Error: Not enough valid bead pairs ({len(pts_ref)}).")
        return None
    
    pts_ref = np.array(pts_ref)
    pts_mov = np.array(pts_mov)
    
    print(f"Aligning using {len(pts_ref)} bead positions")
    
    # Execute alignment
    try:
        affine, inliers_mask, num_inliers, model = robust_point_cloud_registration(
            pts_ref,
            pts_mov,
            transform_type=transform_type,
            residual_threshold=np.max(np.std(pts_ref, axis=0)) / 10,
            max_trials=2000
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
    residual_inlier_mean = np.mean(residuals[inliers_mask]) if num_inliers > 0 else 0
    residual_before = np.mean(np.linalg.norm(pts_mov - pts_ref, axis=1))
    
    print(f"Alignment completed. Number of inliers: {num_inliers}/{pts_ref.shape[0]}.")
    print(f"Mean residual (inliers): {residual_inlier_mean:.2f} nm.")
    print(f"Mean residual before alignment: {residual_before:.2f} nm.")
    
    # Create QC plots if requested
    if qc_plot_path is not None:
        try:
            qc_plot_path = Path(qc_plot_path)
            
            # Matplotlib plot
            plt.figure(figsize=(10, 10))
            plt.scatter(pts_ref[:, 1], pts_ref[:, 2], c='red', label='Reference beads', s=50, alpha=0.7)
            plt.scatter(pts_mov[:, 1], pts_mov[:, 2], c='blue', label='Moving beads', s=50, alpha=0.5)
            
            pts_mov_transformed = model(pts_mov)
            plt.scatter(pts_mov_transformed[:, 1], pts_mov_transformed[:, 2], 
                       c='green', label='Aligned beads', s=50, marker='x')
            
            # Draw lines connecting corresponding beads
            for i in range(len(pts_ref)):
                plt.plot([pts_ref[i, 1], pts_mov_transformed[i, 1]], 
                        [pts_ref[i, 2], pts_mov_transformed[i, 2]], 
                        'k-', alpha=0.3, linewidth=0.5)
            
            plt.title(f'Bead Alignment QC\nMean residual (inliers): {residual_inlier_mean:.2f} nm')
            plt.xlabel('Y (nm)')
            plt.ylabel('X (nm)')
            plt.axis('equal')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(qc_plot_path.with_suffix('.pdf'), dpi=300)
            plt.close()
            
            print(f"QC plot saved to {qc_plot_path.with_suffix('.pdf')}")
            
        except Exception as e:
            print(f"Warning: Could not create QC plot: {e}")
    
    return model
