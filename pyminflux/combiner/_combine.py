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

"""Dataset combining utilities."""

from pathlib import Path
from typing import Optional, Dict, Tuple, List
import numpy as np
import pandas as pd

from pyminflux.reader import MinFluxReaderV2
from pyminflux.correct import align_datasets_using_beads, mbm_dict_to_dataframe
from pyminflux.processor._dataset import MinFluxDataset


def _transform_raw_positions(
    df_raw: pd.DataFrame,
    transform_model: object,
    z_scaling_factor: float,
    unit_scaling_factor: float,
    is_aggregated: bool,
) -> pd.DataFrame:
    """Apply transform_model to raw dataframe positions with correct unit handling.

    Raw positions are stored in meters for non-aggregated datasets and need to be
    scaled to nm (and z-scaled) before applying the transform. After transformation,
    the scaling is reverted to keep raw units consistent.
    """
    df_raw = df_raw.copy()

    # Extract positions in [z, y, x] order
    positions = df_raw[["z", "y", "x"]].to_numpy()

    # Scale to processed-space units
    if not is_aggregated:
        positions = positions * unit_scaling_factor
    positions[:, 0] = positions[:, 0] * z_scaling_factor

    # Apply transformation in processed-space units
    positions_transformed = transform_model(positions)

    # Revert scaling to raw units
    positions_transformed[:, 0] = positions_transformed[:, 0] / z_scaling_factor
    if not is_aggregated:
        positions_transformed = positions_transformed / unit_scaling_factor

    # Update dataframe
    df_raw["z"] = positions_transformed[:, 0]
    df_raw["y"] = positions_transformed[:, 1]
    df_raw["x"] = positions_transformed[:, 2]

    return df_raw


def get_bead_positions_from_mbm(mbm_dict: Dict, n_points: int = 3) -> Dict[str, np.ndarray]:
    """
    Extract average bead positions from MBM dictionary.
    
    Args:
        mbm_dict: MBM dictionary from MinFluxReaderV2
        n_points: Number of earliest points to average
        
    Returns:
        Dictionary mapping bead names to positions [z, y, x] in nm
    """
    df = mbm_dict_to_dataframe(mbm_dict)
    
    if df.empty:
        return {}
    
    # Filter to only include beads marked as "used"
    df = df[df['used'] == True]
    
    if df.empty:
        return {}
    
    bead_positions = {}
    for bead_name in df['bead_name'].unique():
        bead_data = df[df['bead_name'] == bead_name]
        # Get earliest n_points
        earliest = bead_data.nsmallest(n_points, 'tim')
        # Calculate mean position as [z, y, x]
        pos = earliest[['z', 'y', 'x']].mean(axis=0).to_numpy()
        bead_positions[bead_name] = pos
    
    return bead_positions



def load_zarr_for_beads(zarr_path: str) -> Tuple[Optional[MinFluxReaderV2], Optional[Dict]]:
    """
    Load a Zarr file and extract MBM (bead) data.
    
    Args:
        zarr_path: Path to the Zarr file
        
    Returns:
        Tuple of (reader, mbm_dict) or (None, None) if loading fails
    """
    try:
        zarr_path = Path(zarr_path)
        if not zarr_path.exists():
            print(f"Error: Zarr path does not exist: {zarr_path}")
            return None, None
        
        # Load the reader
        reader = MinFluxReaderV2(zarr_path)
        
        # Check if MBM data is available
        if not hasattr(reader, 'mbm_data') or reader.mbm_data is None:
            print(f"Error: No MBM (bead) data found in {zarr_path}")
            return None, None
        
        mbm_dict = reader.mbm_data.get('mbm', {})
        
        if not mbm_dict:
            print(f"Error: MBM dictionary is empty in {zarr_path}")
            return None, None
        
        return reader, mbm_dict
        
    except Exception as e:
        print(f"Error loading Zarr file {zarr_path}: {e}")
        return None, None


def get_next_fluorophore_id(df: pd.DataFrame) -> int:
    """
    Get the next available fluorophore ID.
    
    Args:
        df: DataFrame with 'fluo' column
        
    Returns:
        Next available fluorophore ID
    """
    if 'fluo' not in df.columns:
        return 1
    
    current_ids = df['fluo'].unique()
    if len(current_ids) == 0:
        return 1
    
    return int(np.max(current_ids)) + 1


def combine_datasets_with_alignment(
    reference_dataset: MinFluxDataset,
    moving_dataset: MinFluxDataset,
    transform_model: object,
    next_fluo_id: Optional[int] = None,
) -> MinFluxDataset:
    """
    Combine two datasets by applying transformation to the moving dataset.
    
    Args:
        reference_dataset: Reference dataset (unchanged)
        moving_dataset: Moving dataset (will be transformed and assigned new fluo ID)
        transform_model: Transformation model from align_datasets_using_beads
        next_fluo_id: Fluorophore ID to assign to the moving dataset (auto-assigned if None)
        
    Returns:
        Combined dataset
    """
    # Get the dataframes
    df_reference = reference_dataset.processed_dataframe
    df_moving = moving_dataset.processed_dataframe.copy()

    # Ensure unique iid values to prevent fluorophore mapping collisions
    # Use a single offset for both processed and raw dataframes to keep them aligned.
    iid_offset = 0
    if reference_dataset.full_raw_dataframe is not None and "iid" in reference_dataset.full_raw_dataframe.columns:
        iid_offset = int(reference_dataset.full_raw_dataframe["iid"].max()) if len(reference_dataset.full_raw_dataframe) > 0 else 0
    elif "iid" in df_reference.columns:
        iid_offset = int(df_reference["iid"].max()) if len(df_reference) > 0 else 0

    if iid_offset and "iid" in df_reference.columns and "iid" in df_moving.columns:
        df_moving["iid"] = df_moving["iid"] + iid_offset

    # Ensure unique tid values by offsetting the moving dataset
    tid_offset = 0
    if reference_dataset.full_raw_dataframe is not None and "tid" in reference_dataset.full_raw_dataframe.columns:
        tid_offset = int(reference_dataset.full_raw_dataframe["tid"].max()) + 1 if len(reference_dataset.full_raw_dataframe) > 0 else 0
    elif "tid" in df_reference.columns:
        tid_offset = int(df_reference["tid"].max()) + 1 if len(df_reference) > 0 else 0

    if tid_offset and "tid" in df_moving.columns:
        df_moving["tid"] = df_moving["tid"] + tid_offset
    
    # Determine next fluorophore ID
    if next_fluo_id is None:
        next_fluo_id = get_next_fluorophore_id(df_reference)
    
    # Extract positions and transform them
    positions = df_moving[['z', 'y', 'x']].to_numpy()
    
    # Apply transformation
    positions_transformed = transform_model(positions)
    
    # Update positions in the dataframe
    df_moving['z'] = positions_transformed[:, 0]
    df_moving['y'] = positions_transformed[:, 1]
    df_moving['x'] = positions_transformed[:, 2]
    
    # Assign new fluorophore ID
    df_moving['fluo'] = next_fluo_id
    
    # Concatenate the dataframes
    df_combined = pd.concat([df_reference, df_moving], ignore_index=True)
    
    # Handle full raw dataframe if version 2
    full_raw_combined = None
    if reference_dataset.version == 2 and reference_dataset.full_raw_dataframe is not None:
        if moving_dataset.full_raw_dataframe is not None:
            # Transform the raw dataframe positions with correct unit handling
            df_raw_moving = _transform_raw_positions(
                moving_dataset.full_raw_dataframe,
                transform_model,
                z_scaling_factor=moving_dataset.z_scaling_factor,
                unit_scaling_factor=moving_dataset.unit_scaling_factor,
                is_aggregated=moving_dataset.is_aggregated,
            )
            if iid_offset and "iid" in df_raw_moving.columns:
                df_raw_moving["iid"] = df_raw_moving["iid"] + iid_offset
            if tid_offset and "tid" in df_raw_moving.columns:
                df_raw_moving["tid"] = df_raw_moving["tid"] + tid_offset
            df_raw_moving['fluo'] = next_fluo_id
            
            full_raw_combined = pd.concat(
                [reference_dataset.full_raw_dataframe, df_raw_moving],
                ignore_index=True
            )
        else:
            # Only reference has raw dataframe
            full_raw_combined = reference_dataset.full_raw_dataframe
    
    # Track TID offsets with the first iid they apply to
    combined_tid_offsets: List[Tuple[int, int]] = list(reference_dataset.tid_offsets)
    moving_tid_offsets = moving_dataset.tid_offsets
    base_first_iid = None
    if "iid" in df_moving.columns and len(df_moving) > 0:
        base_first_iid = int(df_moving["iid"].min())
    if moving_tid_offsets:
        adjusted_offsets = []
        for first_iid, offset in moving_tid_offsets:
            adjusted_offsets.append((int(first_iid) + iid_offset, int(offset) + tid_offset))
        combined_tid_offsets.extend(adjusted_offsets)
        if tid_offset and base_first_iid is not None:
            has_base = any(entry_first_iid == base_first_iid for entry_first_iid, _ in adjusted_offsets)
            if not has_base:
                combined_tid_offsets.append((base_first_iid, tid_offset))
    else:
        if tid_offset and base_first_iid is not None:
            combined_tid_offsets.append((base_first_iid, tid_offset))

    # Create the combined dataset
    # Use properties from the reference dataset as the base
    combined_dataset = MinFluxDataset(
        processed_dataframe=df_combined,
        full_raw_dataframe=full_raw_combined,
        filename=None,  # Combined data doesn't have a single source file
        is_3d=reference_dataset.is_3d,
        is_tracking=reference_dataset.is_tracking,
        is_aggregated=reference_dataset.is_aggregated,
        z_scaling_factor=reference_dataset.z_scaling_factor,
        unit_scaling_factor=reference_dataset.unit_scaling_factor,
        dwell_time=reference_dataset.dwell_time,
        pool_dcr=reference_dataset.is_pool_dcr,
        version=reference_dataset.version,
        mbm_data=reference_dataset.mbm_data,  # Keep reference MBM data
        tid_offsets=combined_tid_offsets,
    )
    
    return combined_dataset


def combine_datasets_with_bead_alignment(
    reference_dataset: MinFluxDataset,
    moving_dataset: MinFluxDataset,
    bead_correspondence: Dict[str, str] = None,
    transform_type: str = 'euclidean',
    n_points: int = 3,
    next_fluo_id: Optional[int] = None,
) -> Optional[MinFluxDataset]:
    """
    Perform bead-based alignment and combine two datasets.
    
    The MBM (bead) data is extracted from the datasets themselves.
    
    Args:
        reference_dataset: Reference dataset (must contain mbm_data)
        moving_dataset: Moving dataset (must contain mbm_data)
        bead_correspondence: Mapping of reference bead names to moving bead names
        transform_type: Type of transformation ('euclidean', 'affine', etc.)
        n_points: Number of earliest points to use for bead position averaging
        next_fluo_id: Fluorophore ID to assign (auto-assigned if None)
        
    Returns:
        Combined dataset, or None if alignment fails
    """
    # Extract MBM data from datasets
    if reference_dataset.mbm_data is None:
        print("Error: Reference dataset does not contain MBM (bead) data")
        return None
    
    if moving_dataset.mbm_data is None:
        print("Error: Moving dataset does not contain MBM (bead) data")
        return None
    
    ref_mbm_dict = reference_dataset.mbm_data.get('mbm', {})
    mov_mbm_dict = moving_dataset.mbm_data.get('mbm', {})
    
    if not ref_mbm_dict:
        print("Error: Reference dataset MBM dictionary is empty")
        return None
    
    if not mov_mbm_dict:
        print("Error: Moving dataset MBM dictionary is empty")
        return None
    
    # Perform alignment
    transform_model = align_datasets_using_beads(
        ref_mbm_dict,
        mov_mbm_dict,
        bead_correspondence=bead_correspondence,
        transform_type=transform_type,
        n_points=n_points,
    )
    
    if transform_model is None:
        return None
    
    # Combine the datasets
    return combine_datasets_with_alignment(
        reference_dataset,
        moving_dataset,
        transform_model,
        next_fluo_id=next_fluo_id,
    )
