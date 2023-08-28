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

    # Make sure to extract the test data if it is not already there
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


def test_consistence_of_written_npy_files(extract_raw_npy_data_files):

    #
    # 2D_All.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.filtered_dataframe.index))
    processor.set_fluorophore_ids(fluo)

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 11064, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 11064
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 2432, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 2432
    ), "Wrong number of filtered entries"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Write to disk
        assert (
            MinFluxWriter.write_npy(processor, Path(tmp_dir) / "out.npy") is True
        ), "Could not save .npy file."

        # Now load the stored NumPy file
        reloaded_reader = MinFluxReader(Path(tmp_dir) / "out.npy")

        # And pass it to a new MinFluxProcessor
        reloaded_processor = MinFluxProcessor(reloaded_reader)

    # Now compare the processed file with its reloaded version
    assert (
        len(processor.full_dataframe.index) == 12580
    ), "Original processor's full dataframe must be untouched."
    assert (
        len(reloaded_processor.full_dataframe.index) == 2432
    ), "Unexpected number of entries in reloaded .npy file."
    assert (
        len(reloaded_processor.filtered_dataframe.index) == 2432
    ), "The filtered dataframe does not correspond to the full dataframe after clean reload."
    assert len(processor.filtered_dataframe.index) == len(
        reloaded_processor.filtered_dataframe.index
    ), "Unexpected number of entries in reloaded .npy file."
    assert np.all(
        processor.filtered_dataframe["fluo"].values
        == reloaded_processor.filtered_dataframe["fluo"].values
    ), "Mismatch in fluorophore assignments."
    assert np.allclose(
        processor.filtered_dataframe.values, processor.filtered_dataframe.values
    ), "Reloaded .npy file does not match the original."
    assert np.all(
        processor.filtered_dataframe.columns.values
        == reloaded_processor.filtered_dataframe.columns.values
    ), "Unexpected columns."


def test_consistence_of_fluorophore_selection(extract_raw_npy_data_files):

    #
    # 2D_All.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.filtered_dataframe.index))
    processor.set_fluorophore_ids(fluo)

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 11064, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 11064
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 2432, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 2432
    ), "Wrong number of filtered entries"

    # Now get the filtered dataframes for fluorophore ID = "All", "1", and "2"
    processor.current_fluorophore_id = 0
    filtered_dataframe_all = processor.filtered_dataframe
    processor.current_fluorophore_id = 1
    filtered_dataframe_1 = processor.filtered_dataframe
    processor.current_fluorophore_id = 2
    filtered_dataframe_2 = processor.filtered_dataframe

    # Now get the filtered Numpy array for fluorophore ID = "All", "1", and "2"
    processor.current_fluorophore_id = 0
    filtered_numpy_array_all = processor.filtered_numpy_array
    processor.current_fluorophore_id = 1
    filtered_numpy_array_1 = processor.filtered_numpy_array
    processor.current_fluorophore_id = 2
    filtered_numpy_array_2 = processor.filtered_numpy_array

    # And finally, compare the extracted data
    assert len(filtered_dataframe_all.index) == len(filtered_numpy_array_all)
    assert np.all(
        (filtered_dataframe_all["fluo"] == 1).values
        == (filtered_numpy_array_all["fluo"] == 1)
    ), "Fluorophore ID mismatch"
    assert np.all(
        (filtered_dataframe_all["fluo"] == 2).values
        == (filtered_numpy_array_all["fluo"] == 2)
    ), "Fluorophore ID mismatch"
    assert len(filtered_dataframe_1.index) == len(filtered_numpy_array_1)
    assert np.all(
        (filtered_dataframe_1["fluo"] == 1).values
        == (filtered_numpy_array_1["fluo"] == 1)
    ), "Fluorophore ID mismatch"
    assert np.all(
        (filtered_dataframe_1["fluo"] == 2).values
        == (filtered_numpy_array_1["fluo"] == 2)
    ), "Fluorophore ID mismatch"
    assert (
        filtered_numpy_array_1["fluo"] == 2
    ).sum() == 0, "There should be no localizations for fluorophore 2."
    assert len(filtered_dataframe_2.index) == len(filtered_numpy_array_2)
    assert np.all(
        (filtered_dataframe_2["fluo"] == 1).values
        == (filtered_numpy_array_2["fluo"] == 1)
    ), "Fluorophore ID mismatch"
    assert np.all(
        (filtered_dataframe_2["fluo"] == 2).values
        == (filtered_numpy_array_2["fluo"] == 2)
    ), "Fluorophore ID mismatch"
    assert (
        filtered_numpy_array_2["fluo"] == 1
    ).sum() == 0, "There should be no localizations for fluorophore 1."

    # Constants
    factor = 1e9
    efo_index = 4
    cfr_index = 4
    loc_index = 4

    # Test the actual content

    # All fluorophores
    assert np.all(
        filtered_dataframe_all["tid"].values == filtered_numpy_array_all["tid"]
    ), "Content mismatch."
    assert np.allclose(
        filtered_dataframe_all["tim"].values, filtered_numpy_array_all["tim"]
    ), "Content mismatch."
    efo = filtered_numpy_array_all["itr"][:, efo_index]["efo"]
    assert np.allclose(filtered_dataframe_all["efo"].values, efo), "Content mismatch."
    cfr = filtered_numpy_array_all["itr"][:, cfr_index]["cfr"]
    assert np.allclose(filtered_dataframe_all["cfr"].values, cfr), "Content mismatch."
    loc = filtered_numpy_array_all["itr"][:, loc_index]["loc"] * factor
    assert np.allclose(
        filtered_dataframe_all["x"].values, loc[:, 0]
    ), "Content mismatch."
    assert np.allclose(
        filtered_dataframe_all["y"].values, loc[:, 1]
    ), "Content mismatch."
    assert np.allclose(
        filtered_dataframe_all["z"].values, loc[:, 2]
    ), "Content mismatch."

    # Fluorphore 1
    assert np.all(
        filtered_dataframe_1["tid"].values == filtered_numpy_array_1["tid"]
    ), "Content mismatch."
    assert np.allclose(
        filtered_dataframe_1["tim"].values, filtered_numpy_array_1["tim"]
    ), "Content mismatch."
    efo = filtered_numpy_array_1["itr"][:, efo_index]["efo"]
    assert np.allclose(filtered_dataframe_1["efo"].values, efo), "Content mismatch."
    cfr = filtered_numpy_array_1["itr"][:, cfr_index]["cfr"]
    assert np.allclose(filtered_dataframe_1["cfr"].values, cfr), "Content mismatch."
    loc = filtered_numpy_array_1["itr"][:, loc_index]["loc"] * factor
    assert np.allclose(filtered_dataframe_1["x"].values, loc[:, 0]), "Content mismatch."
    assert np.allclose(filtered_dataframe_1["y"].values, loc[:, 1]), "Content mismatch."
    assert np.allclose(filtered_dataframe_1["z"].values, loc[:, 2]), "Content mismatch."

    # Fluorphore 2
    assert np.all(
        filtered_dataframe_2["tid"].values == filtered_numpy_array_2["tid"]
    ), "Content mismatch."
    assert np.allclose(
        filtered_dataframe_2["tim"].values, filtered_numpy_array_2["tim"]
    ), "Content mismatch."
    efo = filtered_numpy_array_2["itr"][:, efo_index]["efo"]
    assert np.allclose(filtered_dataframe_2["efo"].values, efo), "Content mismatch."
    cfr = filtered_numpy_array_2["itr"][:, cfr_index]["cfr"]
    assert np.allclose(filtered_dataframe_2["cfr"].values, cfr), "Content mismatch."
    loc = filtered_numpy_array_2["itr"][:, loc_index]["loc"] * factor
    assert np.allclose(filtered_dataframe_2["x"].values, loc[:, 0]), "Content mismatch."
    assert np.allclose(filtered_dataframe_2["y"].values, loc[:, 1]), "Content mismatch."
    assert np.allclose(filtered_dataframe_2["z"].values, loc[:, 2]), "Content mismatch."


def test_consistence_of_written_csv_files(extract_raw_npy_data_files):

    #
    # 2D_All.npy
    #
    # min_trace_length = 1
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophores
    np.random.seed(42)
    fluo = np.random.randint(1, 3, len(processor.filtered_dataframe.index))
    processor.set_fluorophore_ids(fluo)

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 11064, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 11064
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 2432, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 2432
    ), "Wrong number of filtered entries"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Write to disk
        assert (
            MinFluxWriter.write_csv(processor, Path(tmp_dir) / "out.csv") is True
        ), "Could not save .csv file."

        # Now load the stored csv file
        reloaded_dataframe = pd.read_csv(Path(tmp_dir) / "out.csv")

    # Now compare the processed file with its reloaded version
    assert (
        len(processor.full_dataframe.index) == 12580
    ), "Original processor's full dataframe must be untouched."
    assert (
        len(reloaded_dataframe.index) == 2432
    ), "Unexpected number of entries in reloaded .npy file."
    assert len(processor.filtered_dataframe.index) == len(
        reloaded_dataframe.index
    ), "Unexpected number of entries in reloaded .npy file."
    assert np.all(
        processor.filtered_dataframe["fluo"].values == reloaded_dataframe["fluo"].values
    ), "Mismatch in fluorophore assignments."
    assert np.allclose(
        processor.filtered_dataframe.values, processor.filtered_dataframe.values
    ), "Reloaded .npy file does not match the original."
    assert np.all(
        processor.filtered_dataframe.columns.values == reloaded_dataframe.columns.values
    ), "Unexpected columns."
