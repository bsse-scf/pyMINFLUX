#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.
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
    # Initialize State
    state = State()

    #
    # 2D_All.npy
    #
    # min_num_loc_per_trace = 4
    #

    # Remove short-lived traces
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader)

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


def test_consistence_of_written_csv_files(extract_raw_npy_data_files):
    # Initialize State
    state = State()

    #
    # 2D_All.npy
    #
    # min_num_loc_per_trace = 4
    #

    # Remove short-lived traces
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader)

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
        processor.filtered_dataframe["fluo"].values
        == reloaded_dataframe["fluo"].values
    ), "Mismatch in fluorophore assignments."
    assert np.allclose(
        processor.filtered_dataframe.values, processor.filtered_dataframe.values
    ), "Reloaded .npy file does not match the original."
    assert np.all(
        processor.filtered_dataframe.columns.values
        == reloaded_dataframe.columns.values
    ), "Unexpected columns."

