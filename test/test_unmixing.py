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

import numpy as np
import pandas as pd
import pytest

from pyminflux.analysis import assign_data_to_clusters
from pyminflux.processor import MinFluxProcessor


class SimpleMockReader:
    """A simple mock reader with controlled fluorophore data for unmixing tests."""
    
    def __init__(self, num_locs=100, initial_fluo_id=1):
        """Create a simple dataset with one fluorophore and varying dcr values.
        
        Parameters
        ----------
        num_locs : int
            Number of localizations
        initial_fluo_id : int
            Initial fluorophore ID (default 1)
        """
        # Create simple x, y, z coordinates
        self.x = np.random.rand(num_locs) * 100
        self.y = np.random.rand(num_locs) * 100
        self.z = np.random.rand(num_locs) * 10
        
        # Create two clusters with different dcr values for unmixing
        # First half: low dcr (0.1-0.3), second half: high dcr (0.6-0.8)
        self.dcr = np.concatenate([
            np.random.rand(num_locs // 2) * 0.2 + 0.1,  # Low dcr cluster
            np.random.rand(num_locs // 2) * 0.2 + 0.6   # High dcr cluster
        ])
        
        # All belong to same trace for simplicity
        self.tid = np.ones(num_locs, dtype=int)
        
        # All start with the same fluorophore ID
        self.fluo = np.ones(num_locs, dtype=int) * initial_fluo_id
        
        # Create the dataframe
        self._df = pd.DataFrame({
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'dcr': self.dcr,
            'tid': self.tid,
            'fluo': self.fluo,
            'tim': np.arange(num_locs),
            'eco': np.ones(num_locs),
            'efo': np.ones(num_locs) * 0.5,
            'eoy': np.zeros(num_locs),
            'cfr': np.ones(num_locs) * 1000,
            'sky': np.ones(num_locs) * 100,
        })
    
    @property
    def processed_dataframe(self):
        return self._df
    
    @property
    def num_valid_entries(self):
        return len(self._df)
    
    @property
    def num_invalid_entries(self):
        return 0
    
    @property
    def is_tracking(self):
        return False


def test_unmixing_single_fluorophore_into_two():
    """Test unmixing a single fluorophore into two new fluorophores."""
    
    # Create a simple dataset with fluo_id = 1
    reader = SimpleMockReader(num_locs=100, initial_fluo_id=1)
    processor = MinFluxProcessor(reader, min_trace_length=1)
    
    # Verify initial state
    assert processor.num_fluorophores == 1
    unique_fluo_ids = np.unique(processor.processed_dataframe["fluo"].to_numpy())
    assert list(unique_fluo_ids) == [1]
    
    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1
    
    # Get the dcr data for clustering
    dcr = processor.filtered_dataframe["dcr"].to_numpy()
    assert len(dcr) == 100
    
    # Perform clustering into 2 groups
    cluster_ids = assign_data_to_clusters(dcr, 2, seed=42)
    unique_clusters = sorted(np.unique(cluster_ids).tolist())
    assert len(unique_clusters) == 2  # Should have 2 clusters
    
    # Simulate the remapping logic from color_unmixer.py
    current_fluo_id = processor.current_fluorophore_id
    assert current_fluo_id == 1
    
    # Get all existing fluorophore IDs
    all_existing_fluo_ids = set(np.unique(processor.processed_dataframe["fluo"].to_numpy()).astype(int))
    assert all_existing_fluo_ids == {1}
    
    # Create the mapping: first cluster keeps ID 1, second gets next available ID (2)
    new_fluo_id_mapping = {unique_clusters[0]: current_fluo_id}  # Keep existing ID
    
    # Find unused ID for second cluster
    next_id = 1
    for i in range(1, len(unique_clusters)):
        while next_id in all_existing_fluo_ids or next_id in new_fluo_id_mapping.values():
            next_id += 1
        new_fluo_id_mapping[unique_clusters[i]] = next_id
        next_id += 1
    
    # The mapping should be: cluster 1 -> fluo_id 1, cluster 2 -> fluo_id 2
    assert 1 in new_fluo_id_mapping.values()
    assert 2 in new_fluo_id_mapping.values()
    
    # Remap the cluster IDs to fluorophore IDs
    remapped_fluo_ids = np.array([new_fluo_id_mapping[cid] for cid in cluster_ids], dtype=np.uint8)
    
    # Verify the remapped IDs
    unique_remapped = sorted(np.unique(remapped_fluo_ids).tolist())
    assert unique_remapped == [1, 2]
    assert len(remapped_fluo_ids) == 100
    
    # Apply the new fluorophore IDs
    processor.set_fluorophore_ids(remapped_fluo_ids)
    
    # Verify the result
    assert processor.num_fluorophores == 2
    final_fluo_ids = sorted(np.unique(processor.processed_dataframe["fluo"].to_numpy()).tolist())
    assert final_fluo_ids == [1, 2]


def test_unmixing_middle_fluorophore_into_two():
    """Test unmixing when fluorophore ID 2 exists among IDs 1, 2, 3 and we unmix ID 2."""
    
    # Create a dataset with 3 fluorophores
    reader = SimpleMockReader(num_locs=100, initial_fluo_id=1)
    processor = MinFluxProcessor(reader, min_trace_length=1)
    
    # Manually create a dataset with 3 fluorophores
    fluo_ids = np.array([1] * 30 + [2] * 40 + [3] * 30, dtype=np.uint8)
    processor.set_fluorophore_ids(fluo_ids)
    
    # Verify initial state
    assert processor.num_fluorophores == 3
    unique_fluo_ids = sorted(np.unique(processor.processed_dataframe["fluo"].to_numpy()).tolist())
    assert unique_fluo_ids == [1, 2, 3]
    
    # Set current fluorophore to 2 (the middle one)
    processor.current_fluorophore_id = 2
    
    # Get the dcr data for clustering (should only get fluo_id 2 data)
    dcr = processor.filtered_dataframe["dcr"].to_numpy()
    assert len(dcr) == 40  # Only fluorophore 2 data
    
    # Perform clustering into 2 groups
    cluster_ids = assign_data_to_clusters(dcr, 2, seed=42)
    unique_clusters = sorted(np.unique(cluster_ids).tolist())
    assert len(unique_clusters) == 2
    
    # Simulate the remapping logic
    current_fluo_id = processor.current_fluorophore_id
    assert current_fluo_id == 2
    
    # Get all existing fluorophore IDs
    all_existing_fluo_ids = set(np.unique(processor.processed_dataframe["fluo"].to_numpy()).astype(int))
    assert all_existing_fluo_ids == {1, 2, 3}
    
    # Create the mapping: first cluster keeps ID 2, second gets next available ID (4)
    new_fluo_id_mapping = {unique_clusters[0]: current_fluo_id}
    
    # Find unused ID for second cluster (should skip 1, 2, 3 and use 4)
    next_id = 1
    for i in range(1, len(unique_clusters)):
        while next_id in all_existing_fluo_ids or next_id in new_fluo_id_mapping.values():
            next_id += 1
        new_fluo_id_mapping[unique_clusters[i]] = next_id
        next_id += 1
    
    # The mapping should be: cluster 1 -> fluo_id 2, cluster 2 -> fluo_id 4
    assert 2 in new_fluo_id_mapping.values()
    assert 4 in new_fluo_id_mapping.values()
    assert new_fluo_id_mapping[unique_clusters[0]] == 2
    assert new_fluo_id_mapping[unique_clusters[1]] == 4
    
    # Remap the cluster IDs to fluorophore IDs
    remapped_fluo_ids = np.array([new_fluo_id_mapping[cid] for cid in cluster_ids], dtype=np.uint8)
    
    # Verify the remapped IDs contain only 2 and 4
    unique_remapped = sorted(np.unique(remapped_fluo_ids).tolist())
    assert unique_remapped == [2, 4]
    assert len(remapped_fluo_ids) == 40
    
    # Apply the new fluorophore IDs (only affects fluo_id 2 localizations)
    processor.set_fluorophore_ids(remapped_fluo_ids)
    
    # Verify the final result: should have fluo_ids 1, 2, 3, and 4
    # IDs 1 and 3 should be PRESERVED (not set to 0!)
    final_fluo_ids = sorted(np.unique(processor.processed_dataframe["fluo"].to_numpy()).tolist())
    assert 1 in final_fluo_ids, "Fluorophore 1 should be preserved"
    assert 2 in final_fluo_ids, "Fluorophore 2 should still exist"
    assert 3 in final_fluo_ids, "Fluorophore 3 should be preserved"
    assert 4 in final_fluo_ids, "Fluorophore 4 should be the new unmixed cluster"
    assert 0 not in final_fluo_ids, "No fluorophores should be set to 0"


def test_unmixing_with_single_fluorophore_and_all_selected():
    """Test the bug fix: unmixing when only one fluorophore exists and 'All' is selected.
    
    This test covers the case where:
    - Only one fluorophore exists (ID 1)
    - The GUI shows only "All" (current_fluorophore_id = 0)
    - Unmixing should NOT create fluorophore ID 0
    """
    
    # Create a dataset with only one fluorophore
    reader = SimpleMockReader(num_locs=100, initial_fluo_id=1)
    processor = MinFluxProcessor(reader, min_trace_length=1)
    
    # Verify initial state
    assert processor.num_fluorophores == 1
    unique_fluo_ids = np.unique(processor.processed_dataframe["fluo"].to_numpy())
    assert list(unique_fluo_ids) == [1]
    
    # Set current fluorophore to 0 (simulating "All" selection when only one fluorophore exists)
    processor.current_fluorophore_id = 0
    
    # Get the dcr data for clustering
    dcr = processor.filtered_dataframe["dcr"].to_numpy()
    assert len(dcr) == 100
    
    # Perform clustering into 2 groups
    cluster_ids = assign_data_to_clusters(dcr, 2, seed=42)
    unique_clusters = sorted(np.unique(cluster_ids).tolist())
    assert len(unique_clusters) == 2
    
    # Simulate the fixed remapping logic from color_unmixer.py
    current_fluo_id = processor.current_fluorophore_id
    assert current_fluo_id == 0  # This is the problematic case!
    
    # THE FIX: When current_fluo_id is 0, extract the actual fluorophore ID from the data
    if current_fluo_id == 0:
        filtered_df = processor.filtered_dataframe
        if filtered_df is not None and len(filtered_df) > 0:
            current_fluo_id = int(filtered_df['fluo'].iloc[0])
        else:
            current_fluo_id = 1
    
    # Now current_fluo_id should be 1, not 0
    assert current_fluo_id == 1, "Should have extracted the actual fluorophore ID from data"
    
    # Get all existing fluorophore IDs
    all_existing_fluo_ids = set(np.unique(processor.processed_dataframe["fluo"].to_numpy()).astype(int))
    all_existing_fluo_ids.discard(0)  # Remove 0 if present
    assert all_existing_fluo_ids == {1}
    
    # Create the mapping with the corrected current_fluo_id
    new_fluo_id_mapping = {unique_clusters[0]: current_fluo_id}
    
    # Find unused ID for second cluster
    next_id = 1
    for i in range(1, len(unique_clusters)):
        while next_id in all_existing_fluo_ids or next_id in new_fluo_id_mapping.values():
            next_id += 1
        new_fluo_id_mapping[unique_clusters[i]] = next_id
        next_id += 1
    
    # The mapping should be: cluster 1 -> fluo_id 1, cluster 2 -> fluo_id 2
    # NOT: cluster 1 -> fluo_id 0, cluster 2 -> fluo_id 2 (the bug!)
    assert new_fluo_id_mapping == {1: 1, 2: 2} or new_fluo_id_mapping == {2: 1, 1: 2}
    assert 0 not in new_fluo_id_mapping.values(), "Should NOT create fluorophore ID 0"
    
    # Remap the cluster IDs to fluorophore IDs
    remapped_fluo_ids = np.array([new_fluo_id_mapping[cid] for cid in cluster_ids], dtype=np.uint8)
    
    # Verify the remapped IDs - should be [1, 2], NOT [0, 2]
    unique_remapped = sorted(np.unique(remapped_fluo_ids).tolist())
    assert unique_remapped == [1, 2], f"Expected [1, 2], got {unique_remapped}"
    assert 0 not in unique_remapped, "Fluorophore ID 0 should NEVER be created"
    
    # Apply the new fluorophore IDs
    processor.set_fluorophore_ids(remapped_fluo_ids)
    
    # Verify the final result
    assert processor.num_fluorophores == 2
    final_fluo_ids = sorted(np.unique(processor.processed_dataframe["fluo"].to_numpy()).tolist())
    assert final_fluo_ids == [1, 2], f"Expected [1, 2], got {final_fluo_ids}"
    assert 0 not in final_fluo_ids, "No fluorophore ID 0 should exist in the final data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
