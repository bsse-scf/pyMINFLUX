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

        x = np.array(
            [
                7.4184994,  # 51
                15.54597418,  # 54
                17.0187548,
                10.75712379,
                5.28072338,
                6.08383931,
                13.95264325,
                41.34898337,  # 70
                38.92833729,
                39.98092342,
                37.70430848,
                43.23700451,
                5.62333476,  # 97
                7.92581688,
                17.27103707,
                9.43949113,
                17.75681099,
                2.15371129,
                17.18905948,
                39.50438874,  # 102
                39.24657456,  # 151
                41.2052434,
                44.24509408,
                36.59157864,  # 171
                43.32636097,
                37.86035951,
                39.18906052,
                33.62707418,
                42.12852769,
                39.489917,
                40.78712421,
                40.11585099,
                28.20309915,  # 176
                13.17710337,
                6.60185162,
                7.24951093,
                9.10716601,
                18.22542178,
                6.11708764,
                5.59437818,
            ]
        )
        y = x + 3.0
        z = 0.0 * x
        self.__df = pd.DataFrame(columns=["tid", "x", "y", "z"])
        self.__df["tid"] = tids
        self.__df["x"] = x
        self.__df["y"] = y
        self.__df["z"] = z
        self.__df["fluo"] = 1

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

    @property
    def test_swapped_fluorophore_ids(self):
        """Swapped fluorophore ids to be used for testing."""
        tmp = self.test_fluorophore_ids.copy()
        tmp[tmp == 2] = 0
        tmp += 1
        return tmp


class MockFromRealDataMinFluxReader:
    def __init__(self):
        self.__df = pd.read_csv(
            Path(__file__).parent / "data" / "two_fluorophores_df.csv"
        )
        self.__fluo_ids = np.load(
            str(Path(__file__).parent / "data" / "two_fluorophores_assignment.npy")
        )
        assert len(self.__df.index) == len(self.__fluo_ids), "Inconsistent test data!"

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
        return self.__fluo_ids


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

    # Make sure that the default fluorophore ID is 0
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


def test_process_by_fluorophore_id_with_mock_reader(tmpdir):
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
    assert processor.current_fluorophore_id == 2, "The fluorophore id must be 2."

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


def test_statistics_by_fluorophore_id_with_mock_reader(tmpdir):
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

    # Check that fluorophore 0 (All) is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([51, 54, 70, 97, 102, 151, 171, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([1, 6, 5, 7, 1, 3, 9, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        if rows.shape[0] > 1:
            sx = rows["x"].values.std(ddof=1)
            sy = rows["y"].values.std(ddof=1)
            sz = rows["z"].values.std(ddof=1)
        else:
            sx = np.nan
            sy = np.nan
            sz = np.nan
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Reset the processor
    processor.reset()

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([51, 54, 70, 97, 102, 151, 171, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([1, 6, 5, 7, 1, 3, 9, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        if rows.shape[0] > 1:
            sx = rows["x"].values.std(ddof=1)
            sy = rows["y"].values.std(ddof=1)
            sz = rows["z"].values.std(ddof=1)
        else:
            sx = np.nan
            sy = np.nan
            sz = np.nan
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Reset the processor
    processor.reset()

    # Check that fluorophore 0 is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Make sure that rows for both fluorophores are returned
    # Make sure that rows for both fluorophores are returned
    df = processor.filtered_dataframe

    assert np.all(np.unique(df["fluo"]) == [1, 2]), "Both fluorophore 1 and 2 expected."
    assert len(df.index) == 40, "Unexpected total number of entries in the dataframe."

    # Get statistics for fluorophore ID 0 (All)
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([51, 54, 70, 97, 102, 151, 171, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([1, 6, 5, 7, 1, 3, 9, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        if rows.shape[0] > 1:
            sx = rows["x"].values.std(ddof=1)
            sy = rows["y"].values.std(ddof=1)
            sz = rows["z"].values.std(ddof=1)
        else:
            sx = np.nan
            sy = np.nan
            sz = np.nan
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([51, 54, 97, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([1, 6, 7, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        if rows.shape[0] > 1:
            sx = rows["x"].values.std(ddof=1)
            sy = rows["y"].values.std(ddof=1)
            sz = rows["z"].values.std(ddof=1)
        else:
            sx = np.nan
            sy = np.nan
            sz = np.nan
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Reset the processor
    processor.reset()

    # Check that fluorophore 0 is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([70, 102, 151, 171])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([5, 1, 3, 9])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        if rows.shape[0] > 1:
            sx = rows["x"].values.std(ddof=1)
            sy = rows["y"].values.std(ddof=1)
            sz = rows["z"].values.std(ddof=1)
        else:
            sx = np.nan
            sy = np.nan
            sz = np.nan
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    #
    # Check filtering by x and y range
    #

    # Reset the processor
    processor.reset()

    # Check that fluorophore 0 is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return 4 rows (for the four TIDs from fluorophore 2)
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # Now collect the stats
    stats = processor.filtered_dataframe_stats

    # The dataframe should be empty
    assert (
        len(stats.index) == 4
    ), "The stats dataframe should contain 4 rows (the ones for fluorophore 2)!"

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # Now collect the stats
    stats = processor.filtered_dataframe_stats

    # The dataframe should be empty
    assert len(stats.index) == 0, "The stats dataframe should be empty!"

    # Reset the processor
    processor.reset()

    # Check that fluorophore 0 is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe
    x_range = (5.0, 15.0)
    y_range = (8.0, 18.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # Now collect the stats
    stats = processor.filtered_dataframe_stats

    # The dataframe should be empty
    assert len(stats.index) == 0, "The stats dataframe should be empty!"

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Check that fluorophore 0 (All) is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([54, 70, 97, 171, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([6, 5, 7, 9, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        sx = rows["x"].values.std(ddof=1)
        sy = rows["y"].values.std(ddof=1)
        sz = rows["z"].values.std(ddof=1)
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Reset the processor
    processor.reset()

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([54, 70, 97, 171, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([6, 5, 7, 9, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        sx = rows["x"].values.std(ddof=1)
        sy = rows["y"].values.std(ddof=1)
        sz = rows["z"].values.std(ddof=1)
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Reset the processor
    processor.reset()

    # Check that fluorophore 0 is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Make sure that rows for fluorophores are returned
    df = processor.filtered_dataframe

    assert np.all(np.unique(df["fluo"]) == [1]), "Both fluorophore 1 and 2 expected."
    assert len(df.index) == 35, "Unexpected total number of entries in the dataframe."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Make sure that rows for fluorophores are returned
    df = processor.filtered_dataframe

    assert np.all(np.unique(df["fluo"]) == [1, 2]), "Both fluorophore 1 and 2 expected."
    assert len(df.index) == 35, "Unexpected total number of entries in the dataframe."

    # Get statistics for fluorophore ID 0 (All)
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([54, 70, 97, 171, 176])
    ), "Unexpected TID grouping."
    assert np.all(
        stats["n"].values == np.array([6, 5, 7, 9, 8])
    ), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        sx = rows["x"].values.std(ddof=1)
        sy = rows["y"].values.std(ddof=1)
        sz = rows["z"].values.std(ddof=1)
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([54, 97, 176])
    ), "Unexpected TID grouping."
    assert np.all(stats["n"].values == np.array([6, 7, 8])), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        sx = rows["x"].values.std(ddof=1)
        sy = rows["y"].values.std(ddof=1)
        sz = rows["z"].values.std(ddof=1)
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)

    # Reset the processor
    processor.reset()

    # Check that fluorophore 0 is selected
    assert processor.current_fluorophore_id == 0, "Default fluorophore must be 0."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Get statistics
    stats = processor.filtered_dataframe_stats

    assert np.all(
        stats["tid"].values == np.array([70, 171])
    ), "Unexpected TID grouping."
    assert np.all(stats["n"].values == np.array([5, 9])), "Unexpected TID grouping."
    assert np.sum(stats["n"].values) == len(
        processor.filtered_dataframe.index
    ), "Unexpected total number of entries in the stats dataframe."

    for tid in stats["tid"].values:
        rows = processor.filtered_dataframe.loc[
            processor.filtered_dataframe["tid"] == tid
        ]
        mx = rows["x"].values.mean()
        my = rows["y"].values.mean()
        mz = rows["z"].values.mean()
        sx = rows["x"].values.std(ddof=1)
        sy = rows["y"].values.std(ddof=1)
        sz = rows["z"].values.std(ddof=1)
        if np.isnan(sx):
            sx = 0.0
        if np.isnan(sy):
            sy = 0.0
        if np.isnan(sz):
            sz = 0.0
        assert np.allclose(mx, stats.loc[stats["tid"] == tid, "mx"].values, atol=1e-6)
        assert np.allclose(my, stats.loc[stats["tid"] == tid, "my"].values, atol=1e-6)
        assert np.allclose(mz, stats.loc[stats["tid"] == tid, "mz"].values, atol=1e-6)
        assert np.allclose(sx, stats.loc[stats["tid"] == tid, "sx"].values, atol=1e-6)
        assert np.allclose(sy, stats.loc[stats["tid"] == tid, "sy"].values, atol=1e-6)
        assert np.allclose(sz, stats.loc[stats["tid"] == tid, "sz"].values, atol=1e-6)


def test_select_by_fluorophore_id_with_mock_reader(extract_raw_npy_data_files):
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

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    select_df = processor.select_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The dataframe should be empty
    assert len(select_df.index) == 0, "The selection should be empty!"

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We select a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe
    x_range = (5.0, 15.0)
    y_range = (8.0, 18.0)
    select_df = processor.select_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The dataframe should be empty
    assert len(select_df.index) == 0, "The selection should be empty!"

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We select a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    select_df = processor.select_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The dataframe should be empty
    assert len(select_df.index) == 0, "The selection should be empty!"

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe
    x_range = (5.0, 15.0)
    y_range = (8.0, 18.0)
    select_df = processor.select_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The dataframe should be empty
    assert len(select_df.index) == 0, "The selection should be empty!"


def test_1d_and_2d_filtering_by_fluorophore_id_with_mock_reader(
    tmpdir,
):
    # Initialize State
    state = State()

    #
    # 2D filtering
    #

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

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe and NOT affect the selection
    # of the localizations assigned to fluorophore 2.
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 0
    ), "The selection should be empty!"

    # If we now switch to fluorophore 2 and apply the same filter,
    # we should get the localizations of all fluorophores (since they
    # all fit in the range).

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2.
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 17
    ), "The selection should not be empty!"

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe and NOT affect the selection
    # of the localizations assigned to fluorophore 2.
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 0
    ), "The selection should be empty!"

    # If we now switch to fluorophore 2 and apply the same filter,
    # we should get the localizations of all fluorophores (since they
    # all fit in the range).

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2.
    x_range = (35.0, 45.0)
    y_range = (38.0, 48.0)
    processor.filter_by_2d_range("x", "y", x_range=x_range, y_range=y_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 13
    ), "The selection should not be empty!"

    #
    # 1D filtering
    #

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

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe and NOT affect the selection
    # of the localizations assigned to fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_1d_range("x", x_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 0
    ), "The selection should be empty!"

    # If we now switch to fluorophore 2 and apply the same filter,
    # we should get the localizations of all fluorophores (since they
    # all fit in the range).

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_1d_range("x", x_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 17
    ), "The selection should not be empty!"

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe and NOT affect the selection
    # of the localizations assigned to fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_1d_range("x", x_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 0
    ), "The selection should be empty!"

    # If we now switch to fluorophore 2 and apply the same filter,
    # we should get the localizations of all fluorophores (since they
    # all fit in the range).

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_1d_range("x", x_range)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 13
    ), "The selection should not be empty!"

    #
    # 1D thresholding
    #

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

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe and NOT affect the selection
    # of the localizations assigned to fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_single_threshold("x", x_range[0], larger_than=True)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 0
    ), "The selection should be empty!"

    # If we now switch to fluorophore 2 and apply the same filter,
    # we should get the localizations of all fluorophores (since they
    # all fit in the range).

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_single_threshold("x", x_range[0], larger_than=True)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 17
    ), "The selection should not be empty!"

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore to 1
    processor.current_fluorophore_id = 1

    # We filter with a range that only contains traces of fluorophore 2:
    # this should return an empty stats dataframe and NOT affect the selection
    # of the localizations assigned to fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_single_threshold("x", x_range[0], larger_than=True)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 0
    ), "The selection should be empty!"

    # If we now switch to fluorophore 2 and apply the same filter,
    # we should get the localizations of all fluorophores (since they
    # all fit in the range).

    # Set current fluorophore to 2
    processor.current_fluorophore_id = 2

    # We filter with a range that only contains traces of fluorophore 2.
    x_range = (35.0, 45.0)
    processor.filter_by_single_threshold("x", x_range[0], larger_than=True)

    # The current selection should be empty
    assert (
        len(processor.filtered_dataframe.index) == 13
    ), "The selection should not be empty!"


def test_extract_filtered_fluorophore_ids():
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

    # Check that the global filters have been applied (and nothing has been dropped)
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Unexpected number of entries."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Check that we have the default fluorophore (0)
    assert processor.current_fluorophore_id == 0, "Default fluorophore ID must be 0."

    # Now, the data for all fluorophores will be returned
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Unexpected number of entries."

    # Change to fluorophore 1
    processor.current_fluorophore_id = 1

    # Now, the data for fluorophore 1 will be returned
    assert (
        len(processor.filtered_dataframe.index) == 22
    ), "Unexpected number of entries."

    # We filter with a single threshold that should return just one ID 1 fluorophore.
    x_thresh = 20.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 1, "Expected 1 entry."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 1, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 0, "Unexpected number of ID 2 fluorophores."

    # Now change to fluorophore ID 2. This reset current filters.
    processor.current_fluorophore_id = 2

    # Check that there are 18 entries
    assert (
        len(processor.filtered_dataframe.index) == 18
    ), "Unexpected number of entries."

    # Same filter
    x_thresh = 20.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 18, "Expected 18 entries."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 18, "Unexpected number of ID 2 fluorophores."

    #
    # Now the same with some global filtering applied.
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Check that there are 35 entries
    assert (
        len(processor.filtered_dataframe.index) == 35
    ), "Unexpected number of entries."

    # Change to fluorophore 1
    processor.current_fluorophore_id = 1

    # Check that there are 21 entries
    assert (
        len(processor.filtered_dataframe.index) == 21
    ), "Unexpected number of entries."

    # Same filter
    x_thresh = 20.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 0, "Expected 0 entries."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 0, "Unexpected number of ID 2 fluorophores."

    # Finally, change to fluorophore ID 2. This reset current filters.
    processor.current_fluorophore_id = 2

    # Check that there are 14 entries
    assert (
        len(processor.filtered_dataframe.index) == 14
    ), "Unexpected number of entries."

    # Same filter
    x_thresh = 20.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 14, "Unexpected number of ID 2 fluorophores."


def test_assignment_by_increasing_dcr(tmpdir):
    """The fluorophore ID is sorted by increasing DCR."""

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

    # Set the swapped fluorophore IDs
    processor.set_fluorophore_ids(reader.test_swapped_fluorophore_ids)

    # Check that the global filters have been applied (and nothing has been dropped)
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Unexpected number of entries."

    # Check that we have the default fluorophore (0)
    assert processor.current_fluorophore_id == 0, "Default fluorophore ID must be 0."

    # Now, the data for all fluorophores will be returned
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Unexpected number of entries."

    # Change to fluorophore 1
    processor.current_fluorophore_id = 1

    # Now, the data for fluorophore 1 will be returned
    assert (
        len(processor.filtered_dataframe.index) == 18  # 22 if now swapped
    ), "Unexpected number of entries."

    # Now change to fluorophore ID 2. This reset current filters.
    processor.current_fluorophore_id = 2

    # Check that there are 18 entries
    assert (
        len(processor.filtered_dataframe.index) == 22  # 18 if not swapped
    ), "Unexpected number of entries."


def test_extract_filtered_fluorophore_ids_from_real_data(tmpdir):
    # Initialize State
    state = State()

    #
    # MockFromRealDataMinFluxReader
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # MockMinFluxReader
    reader = MockFromRealDataMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Consistency check
    assert len(reader.processed_dataframe.index) == len(reader.test_fluorophore_ids)

    # Check that the global filters have been applied (and nothing has been dropped)
    assert (
        len(processor.filtered_dataframe.index) == 17955
    ), "Unexpected number of entries."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    #
    # Switch through fluorophore IDs to check that the number of returned items is correct.
    #

    # Fluorophore ID = 1
    processor.current_fluorophore_id = 1
    ids = processor.filtered_dataframe["fluo"]
    assert (
        len(processor.filtered_dataframe.index) == 12884
    ), "Unexpected number of entries."
    assert len(ids) == 12884, "Unexpected number of entries."
    assert (ids == 1).sum() == (
        reader.test_fluorophore_ids == 1
    ).sum(), "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 0, "Unexpected number of ID 2 fluorophores."

    # Fluorophore ID = 2
    processor.current_fluorophore_id = 2
    ids = processor.filtered_dataframe["fluo"]
    assert (
        len(processor.filtered_dataframe.index) == 5071
    ), "Unexpected number of entries."
    assert len(ids) == 5071, "Unexpected number of entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == (
        reader.test_fluorophore_ids == 2
    ).sum(), "Unexpected number of ID 2 fluorophores."

    #
    # MockFromRealDataMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockFromRealDataMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Consistency check
    assert len(reader.processed_dataframe.index) == len(reader.test_fluorophore_ids)

    # Check that the global filters have been applied (and nothing has been dropped)
    assert (
        len(processor.filtered_dataframe.index) == 16281
    ), "Unexpected number of entries."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    #
    # Switch through fluorophore IDs to check that the number of returned items is correct.
    #

    # Fluorophore ID = 1
    processor.current_fluorophore_id = 1
    ids = processor.filtered_dataframe["fluo"]
    assert (
        len(processor.filtered_dataframe.index) == 11544
    ), "Unexpected number of entries."
    assert len(ids) == 11544, "Unexpected number of entries."
    assert (ids == 1).sum() == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 0, "Unexpected number of ID 2 fluorophores."

    # Fluorophore ID = 2
    processor.current_fluorophore_id = 2
    ids = processor.filtered_dataframe["fluo"]
    assert (
        len(processor.filtered_dataframe.index) == 4737
    ), "Unexpected number of entries."
    assert len(ids) == 4737, "Unexpected number of entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of ID 2 fluorophores."


def test_retrieving_dataframe_with_no_fluorophore_filtering(tmpdir):
    """Test retrieving the join of the fluorophore 1 and 2 filtered datasets."""

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

    # Check that the global filters have been applied (and nothing has been dropped)
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Unexpected number of entries."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Check that we have the default fluorophore (0)
    assert processor.current_fluorophore_id == 0, "Default fluorophore ID must be 0."

    # Change to fluorophore 1
    processor.current_fluorophore_id = 1

    # Now, the data for fluorophore 1 will be returned
    assert (
        len(processor.filtered_dataframe.index) == 22
    ), "Unexpected number of entries."

    # We filter with a single threshold that should return 10 ID 1 fluorophore.
    x_thresh = 10.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Keep a copy of the filtered_dataframe for later testing
    df_1 = processor.filtered_dataframe.copy()

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 10, "Expected 10 entry."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 10, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 0, "Unexpected number of ID 2 fluorophores."

    # Now change to fluorophore ID 2. This reset current filters.
    processor.current_fluorophore_id = 2

    # Check that there are 18 entries
    assert (
        len(processor.filtered_dataframe.index) == 18
    ), "Unexpected number of entries."

    # We filter with a single threshold that should return 8 ID 2 fluorophore.
    x_thresh = 40.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 8, "Expected 8 entries."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 8, "Unexpected number of ID 2 fluorophores."

    # Keep a copy of the filtered_dataframe for later testing
    df_2 = processor.filtered_dataframe.copy()

    # Now compare the join of df_1 and df_2 with the result of processor.filtered_dataframe_all
    processor.current_fluorophore_id = 0
    df_all = processor.filtered_dataframe
    df_join = pd.concat([df_1, df_2]).sort_index()
    # Make sure all entries are the same
    assert (
        (df_all == df_join).all().all()
    ), "The selected and filtered set are not identical."

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4
    #

    # Now we filter all short-lived traces
    state.min_num_loc_per_trace = 4

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader)

    # Check that the global filters have been applied (and nothing has been dropped)
    assert (
        len(processor.filtered_dataframe.index) == 35
    ), "Unexpected number of entries."

    # Reassign the fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Check that we have the default fluorophore (0)
    assert processor.current_fluorophore_id == 0, "Default fluorophore ID must be 0."

    # Now, the data for all fluorophores will be returned
    assert (
        len(processor.filtered_dataframe.index) == 35
    ), "Unexpected number of entries."

    # Change to fluorophore 1
    processor.current_fluorophore_id = 1

    # Now, the data for fluorophore 1 will be returned
    assert (
        len(processor.filtered_dataframe.index) == 21
    ), "Unexpected number of entries."

    # We filter with a single threshold that should return 10 ID 1 fluorophore.
    x_thresh = 10.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Keep a copy of the filtered_dataframe for later testing
    df_1 = processor.filtered_dataframe.copy()

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 4, "Expected 10 entry."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 4, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 0, "Unexpected number of ID 2 fluorophores."

    # Now change to fluorophore ID 2. This reset current filters.
    processor.current_fluorophore_id = 2

    # Check that there are 14 entries
    assert (
        len(processor.filtered_dataframe.index) == 14
    ), "Unexpected number of entries."

    # We filter with a single threshold that should return 8 ID 2 fluorophore.
    x_thresh = 40.0
    processor.filter_by_single_threshold("x", threshold=x_thresh, larger_than=True)

    # Get the fluorophore IDs
    ids = processor.filtered_dataframe["fluo"]

    # Check
    assert len(processor.filtered_dataframe.index) == 4, "Expected 8 entries."
    assert len(processor.filtered_dataframe.index) == len(
        ids
    ), "The number of fluorophore IDs must match the number of df entries."
    assert (ids == 1).sum() == 0, "Unexpected number of ID 1 fluorophores."
    assert (ids == 2).sum() == 4, "Unexpected number of ID 2 fluorophores."

    # Keep a copy of the filtered_dataframe for later testing
    df_2 = processor.filtered_dataframe.copy()

    # Now compare the join of df_1 and df_2 with the result of processor.filtered_dataframe_all
    processor.current_fluorophore_id = 0
    df_all = processor.filtered_dataframe
    df_join = pd.concat([df_1, df_2]).sort_index()

    # Make sure all entries are the same
    assert (
        (df_all == df_join).all().all()
    ), "The selected and filtered set are not identical."
