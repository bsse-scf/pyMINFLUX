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
#   limitations under the License.
#

import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.state import State
from pyminflux.writer import MinFluxWriter


@pytest.fixture(autouse=False)
def extract_raw_npy_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    npy_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy"
    zip_file_name = Path(__file__).parent / "data" / "2D_ValidOnly.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_update_localizations(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Create random fluorophore IDs (1 or 2)
    rng = np.random.default_rng(seed=42)
    ids = rng.integers(
        low=1, high=3, size=len(processor.filtered_dataframe.index), dtype=int
    )

    num_fluo_1 = np.sum(ids == 1)
    num_fluo_2 = np.sum(ids == 2)
    assert num_fluo_1 == 6349, "Unexpected number of fluorophores with ID 1."
    assert num_fluo_2 == 6231, "Unexpected number of fluorophores with ID 2."
    assert num_fluo_1 + num_fluo_2 == len(processor.filtered_dataframe.index)

    # Assign the fluorophore IDs
    processor.set_fluorophore_ids(ids)

    # Set active fluorophore to 0
    processor.current_fluorophore_id = 0

    # Update all localizations
    processor.update_localizations(
        x=np.zeros(len(processor.filtered_dataframe.index)),
        y=np.zeros(len(processor.filtered_dataframe.index)),
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values

    # Test
    assert np.isclose(mx.sum(), 0.0), "Unexpected mean x localization."
    assert np.isclose(my.sum(), 0.0), "Unexpected mean x localization."

    # Set active fluorophore to 1
    processor.current_fluorophore_id = 1

    # Update localizations for fluorophore 1
    n = np.sum(processor.filtered_dataframe["fluo"] == 1)
    processor.update_localizations(x=-3.0 * np.ones(n), y=-3.0 * np.ones(n))

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values

    # Test
    assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."

    # Make sure that the coordinates for fluorophore 2 were not touched
    processor.current_fluorophore_id = 2

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values

    # Test
    assert np.isclose(mx.mean(), 0.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), 0.0), "Unexpected mean x localization."

    # Update localizations for fluorophore 2
    n = np.sum(processor.filtered_dataframe["fluo"] == 2)
    processor.update_localizations(x=-7.0 * np.ones(n), y=-7.0 * np.ones(n))

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values

    # Test
    assert np.isclose(mx.mean(), -7.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -7.0), "Unexpected mean x localization."

    # Make sure that the coordinates for fluorophore 1 were not touched
    processor.current_fluorophore_id = 1

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values

    # Test
    assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."

    # Try writing and reading the NumPy file
    with tempfile.TemporaryDirectory() as tmp_dir:

        # Make sure to write data for all fluorophores
        processor.current_fluorophore_id = 0

        # Output file name
        filename = Path(tmp_dir) / "out.npy"

        # Write to disk
        assert (
            MinFluxWriter.write_npy(processor, filename) is True
        ), "Could not save .npy file."

        # Now load the stored NumPy file
        reloaded_reader = MinFluxReader(filename)
        reloaded_processor = MinFluxProcessor(reloaded_reader)

        # Check that the fluorophore are set, and that x, y, and z
        # coordinates are the updated ones
        reloaded_processor.current_fluorophore_id = 1
        mx = reloaded_processor.filtered_dataframe_stats["mx"].values
        my = reloaded_processor.filtered_dataframe_stats["my"].values
        assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
        assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."

        reloaded_processor.current_fluorophore_id = 2
        mx = reloaded_processor.filtered_dataframe_stats["mx"].values
        my = reloaded_processor.filtered_dataframe_stats["my"].values

        # Test
        assert np.isclose(mx.mean(), -7.0), "Unexpected mean x localization."
        assert np.isclose(my.mean(), -7.0), "Unexpected mean x localization."
