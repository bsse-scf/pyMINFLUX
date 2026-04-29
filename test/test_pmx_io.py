#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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

import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader, PMXReader
from pyminflux.writer import PMXWriter


@pytest.fixture(autouse=False)
def extract_raw_npy_data_files(tmpdir):
    """Fixture to extract test data files if not already present."""
    
    # Setup
    npy_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy"
    zip_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    # Teardown - nothing for the moment



def test_pmx_write_read_cycle_with_filtering(extract_raw_npy_data_files):
    """Test PMX write-read cycle with trace filtering applied.
    
    This test verifies that filtered data (e.g., removing short traces) is
    correctly preserved through the write-read cycle.
    """
    
    # Load data
    npy_file = Path(__file__).parent / "data" / "2D_ValidOnly.npy"
    reader = MinFluxReader(npy_file, z_scaling_factor=0.7)
    
    # Apply trace length filtering
    MIN_TRACE_LENGTH = 4
    processor = MinFluxProcessor(reader, min_trace_length=MIN_TRACE_LENGTH)
    
    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.processed_dataframe.index))
    processor.set_full_fluorophore_ids(fluo)
    
    # Set custom fluorophore names
    processor.set_fluorophore_names({1: "GFP", 2: "RFP"})
    
    # Store original filtered dataframe AFTER fluorophore assignment
    original_df = processor.filtered_dataframe.copy()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        
        # Write and read back
        writer = PMXWriter(processor)
        pmx_file = Path(tmp_dir) / "test_filtered.pmx"
        assert writer.write(pmx_file) is True, "Failed to write PMX file"
        
        df_read = PMXReader.get_filtered_dataframe(pmx_file)
        
        # Verify the filtered data is preserved
        assert len(df_read) == len(original_df), \
            f"Number of entries mismatch: {len(df_read)} vs {len(original_df)}"
        
        # Verify data equality
        assert original_df.equals(df_read), \
            "Filtered dataframe not preserved through write-read cycle"
        
        # Verify metadata
        metadata = PMXReader.get_metadata(pmx_file)
        assert metadata.min_trace_length == MIN_TRACE_LENGTH, \
            "Filtering parameters not preserved"
        
        # Verify fluorophore names are preserved
        fluorophore_names = PMXReader.get_fluorophore_names(pmx_file)
        assert fluorophore_names == {1: "GFP", 2: "RFP"}, \
            f"Fluorophore names mismatch: {fluorophore_names}"
