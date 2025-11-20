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

"""Dataset merging utilities."""

from pathlib import Path
from typing import Optional, Dict, Tuple
import numpy as np
import pandas as pd

from pyminflux.reader import MinFluxReaderV2
from pyminflux.correct import align_datasets_using_beads, mbm_dict_to_dataframe


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
    
    bead_positions = {}
    for bead_name in df['bead_name'].unique():
        bead_data = df[df['bead_name'] == bead_name]
        # Get earliest n_points
        earliest = bead_data.nsmallest(n_points, 'tim')
        # Calculate mean position as [z, y, x]
        pos = earliest[['z', 'y', 'x']].mean(axis=0).to_numpy()
        bead_positions[bead_name] = pos
    
    return bead_positions


def merge_dataframes_with_alignment(
    df_reference: pd.DataFrame,
    df_moving: pd.DataFrame,
    transform_model: object,
    next_fluo_id: int = 2
) -> pd.DataFrame:
    """
    Merge two dataframes by applying transformation to the moving dataset.
    
    Args:
        df_reference: Reference dataset dataframe (unchanged)
        df_moving: Moving dataset dataframe (will be transformed and assigned new fluo ID)
        transform_model: Transformation model from align_datasets_using_beads
        next_fluo_id: Fluorophore ID to assign to the moving dataset
        
    Returns:
        Merged dataframe
    """
    # Make a copy of the moving dataframe to avoid modifying the original
    df_moving_copy = df_moving.copy()
    
    # Extract positions and transform them
    positions = df_moving_copy[['z', 'y', 'x']].to_numpy()
    
    # Apply transformation
    # The transform model expects [z, y, x] order based on our alignment code
    positions_transformed = transform_model(positions)
    
    # Update positions in the dataframe
    df_moving_copy['z'] = positions_transformed[:, 0]
    df_moving_copy['y'] = positions_transformed[:, 1]
    df_moving_copy['x'] = positions_transformed[:, 2]
    
    # Also transform localization uncertainties if they exist
    if 'lncz' in df_moving_copy.columns:
        lnc_positions = df_moving_copy[['lncz', 'lncy', 'lncx']].to_numpy()
        # For uncertainties, we only apply rotation/scaling, not translation
        # This is a simplification - proper uncertainty transformation is more complex
        # For now, we'll just keep them as-is
        pass
    
    # Assign new fluorophore ID
    df_moving_copy['fluo'] = next_fluo_id
    
    # Concatenate the dataframes
    df_merged = pd.concat([df_reference, df_moving_copy], ignore_index=True)
    
    return df_merged


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
