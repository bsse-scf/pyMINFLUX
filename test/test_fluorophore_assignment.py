import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.state import State


class MockMinFluxReader:
    def __init__(self):

        # TID   # loc   Fluo ID
        #  51      1        1
        #  54      6        1
        #  70      5        2
        #  97      7        1
        # 102      1        2
        # 151      3        2
        # 171      9        2
        # 176      8        1

        tids = [
            51,
            54,
            54,
            54,
            54,
            54,
            54,
            70,
            70,
            70,
            70,
            70,
            97,
            97,
            97,
            97,
            97,
            97,
            97,
            102,
            151,
            151,
            151,
            171,
            171,
            171,
            171,
            171,
            171,
            171,
            171,
            171,
            176,
            176,
            176,
            176,
            176,
            176,
            176,
            176,
        ]
        self.__df = pd.DataFrame(columns=["tid"])
        self.__df["tid"] = tids

    @property
    def processed_dataframe(self):
        return self.__df

    @property
    def num_valid_entries(self):
        """Number of valid entries."""
        return len(self.__df.index)

    @property
    def num_invalid_entries(self):
        """Number of invalid entries."""
        return 0

    @property
    def test_fluorophore_ids(self):
        """Fluorophore ids to be used for testing."""
        return np.array(
            [
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
                2,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
            ]
        )


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

    npy_file_name = Path(__file__).parent / "data" / "3D_ValidOnly.npy"
    zip_file_name = Path(__file__).parent / "data" / "3D_ValidOnly.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_assign_fluorophore_id(extract_raw_npy_data_files):

    # Initialize State
    state = State()

    #
    # 2D_ValidOnly.npy
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Create random fluorophore IDs (1 or 2)
    rng = np.random.default_rng(seed=42)
    ids = rng.integers(
        low=1, high=3, size=len(processor.filtered_dataframe.index), dtype=int
    )

    num_fluo_0 = np.sum(ids == 0)
    num_fluo_1 = np.sum(ids == 1)
    num_fluo_2 = np.sum(ids == 2)
    num_fluo_3 = np.sum(ids == 3)
    assert num_fluo_0 == 0, "Unexpected number of fluorophores with ID 0."
    assert num_fluo_1 == 6349, "Unexpected number of fluorophores with ID 1."
    assert num_fluo_2 == 6231, "Unexpected number of fluorophores with ID 2."
    assert num_fluo_3 == 0, "Unexpected number of fluorophores with ID 3."
    assert num_fluo_1 + num_fluo_2 == len(processor.filtered_dataframe.index)

    # Assign the fluorophore IDs
    processor.set_fluorophore_ids(ids)

    # Make sure that the default fluorophore ID is 0 (that is, no selection)
    assert processor.current_fluorophore_id == 0, "Default fluorophore ID must be 0."

    # Set current_fluorophore ID to 1
    processor.current_fluorophore_id = 1

    # Get the subset of data for fluorophore 1
    df_fluo_1 = processor.filtered_dataframe
    assert len(df_fluo_1.index) == num_fluo_1

    # Set current_fluorophore ID to 2
    processor.current_fluorophore_id = 2

    # Get the subset of data for fluorophore 2
    df_fluo_2 = processor.filtered_dataframe
    assert len(df_fluo_2.index) == num_fluo_2

    # Set current_fluorophore ID to 3
    with pytest.raises(ValueError):
        processor.current_fluorophore_id = 3


def test_process_by_fluorophore_id_with_mock_reader(extract_raw_npy_data_files):

    # Initialize State
    state = State()

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Check counts for totally unfiltered data
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 40, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Wrong number of filtered entries"

    # Check that no traces are shorter than state.min_num_loc_per_trace
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert len(counts[counts < state.min_num_loc_per_trace].values) == 0

    # Assign the test fluorophore ids
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set the fluorophore id to 1
    processor.current_fluorophore_id = 1
    assert processor.current_fluorophore_id == 1, "The fluorophore id must be 1."

    # Check counts
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 22, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 22
    ), "Wrong number of filtered entries"

    # Check that the extracted ID are the expected ones
    extracted_tids = np.unique(processor.filtered_dataframe["tid"])
    expected_tids = np.array([51, 54, 97, 176])
    assert np.all(extracted_tids == expected_tids), "Unexpected set of filtered TIDs."

    # Check that no traces are shorter than state.min_num_loc_per_trace
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert len(counts[counts < state.min_num_loc_per_trace].values) == 0

    # Set the fluorophore id to 2
    processor.current_fluorophore_id = 2
    assert processor.current_fluorophore_id == 2, "The fluorophore id must be 1."

    # Check counts
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 18, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 18
    ), "Wrong number of filtered entries"

    # Check that the extracted ID are the expected ones
    extracted_tids = np.unique(processor.filtered_dataframe["tid"])
    expected_tids = np.array([70, 102, 151, 171])
    assert np.all(extracted_tids == expected_tids), "Unexpected set of filtered TIDs."

    # Check that no traces are shorter than state.min_num_loc_per_trace
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert len(counts[counts < state.min_num_loc_per_trace].values) == 0

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Filter short traces
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Check counts for totally unfiltered data
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 35, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 35
    ), "Wrong number of filtered entries"

    # Check that no traces are shorter than state.min_num_loc_per_trace
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert len(counts[counts < state.min_num_loc_per_trace].values) == 0

    # Expected TIDs
    extracted_tids = np.unique(processor.filtered_dataframe["tid"])
    expected_tids = np.array([54, 70, 97, 171, 176])
    assert np.all(extracted_tids == expected_tids), "Unexpected set of filtered TIDs."

    # Assign the test fluorophore ids
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set the fluorophore id to 1
    processor.current_fluorophore_id = 1
    assert processor.current_fluorophore_id == 1, "The fluorophore id must be 1."

    # Check counts
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 21, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 21
    ), "Wrong number of filtered entries"

    # Check that the extracted ID are the expected ones
    extracted_tids = np.unique(processor.filtered_dataframe["tid"])
    expected_tids = np.array([54, 97, 176])
    assert np.all(extracted_tids == expected_tids), "Unexpected set of filtered TIDs."

    # Check that no traces are shorter than state.min_num_loc_per_trace
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert len(counts[counts < state.min_num_loc_per_trace].values) == 0

    # Set the fluorophore id to 2
    processor.current_fluorophore_id = 2
    assert processor.current_fluorophore_id == 2, "The fluorophore id must be 1."

    # Check counts
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 14, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 14
    ), "Wrong number of filtered entries"

    # Check that the extracted ID are the expected ones
    extracted_tids = np.unique(processor.filtered_dataframe["tid"])
    expected_tids = np.array([70, 171])
    assert np.all(extracted_tids == expected_tids), "Unexpected set of filtered TIDs."

    # Check that no traces are shorter than state.min_num_loc_per_trace
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert len(counts[counts < state.min_num_loc_per_trace].values) == 0
