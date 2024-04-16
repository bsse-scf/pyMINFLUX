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
        #  54      6        1

        tids = [
            51,
            51,
            51,
            54,
            54,
            54,
            54,
            54,
        ]

        x = np.array(
            [
                10.0,  # 51
                11.0,
                12.0,
                10.0,  # 54
                11.0,
                12.0,
                22.0,
                23.0,
            ]
        )
        y = x + 3.0
        z = 0.0 * x
        self._df = pd.DataFrame(columns=["tid", "tim", "x", "y", "z", "fluo"])
        self._df["tid"] = tids
        self._df["tim"] = np.arange(len(x)).tolist()
        self._df["x"] = x
        self._df["y"] = y
        self._df["z"] = z
        self._df["fluo"] = 1

    @property
    def processed_dataframe(self):
        return self._df

    @property
    def num_valid_entries(self):
        """Number of valid entries."""
        return len(self._df.index)

    @property
    def num_invalid_entries(self):
        """Number of invalid entries."""
        return 0

    @property
    def is_tracking(self):
        """This is a localization dataset and not a tracking one."""
        return False


@pytest.fixture(autouse=False)
def extract_raw_npy_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    npy_file_name = Path(__file__).parent / "data" / "2D_All.npy"
    zip_file_name = Path(__file__).parent / "data" / "2D_All.npy.zip"
    if not npy_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

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


def test_filter_raw_dataframes(extract_raw_npy_data_files):

    #
    # 2D_All.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Check counts for totally unfiltered data
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 687394, "Wrong number of invalid entries"
    assert processor.num_values == 12580, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 12580
    ), "Wrong number of filtered entries"

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

    # Reset all filters and confirm counts
    processor.reset()
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 687394, "Wrong number of invalid entries"
    assert processor.num_values == 12580, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 12580
    ), "Wrong number of filtered entries"

    #
    # 2D_All.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Check counts for totally unfiltered data
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 687394, "Wrong number of invalid entries"
    assert processor.num_values == 11903, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 11903
    ), "Wrong number of filtered entries"

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 10385, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 10385
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < processor.min_trace_length) == 0

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 1678, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1678
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < processor.min_trace_length) == 0

    # Reset all filters and confirm counts
    processor.reset()
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 687394, "Wrong number of invalid entries"
    assert processor.num_values == 11903, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 11903
    ), "Wrong number of filtered entries"

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Check counts for totally unfiltered data
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 12580, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 12580
    ), "Wrong number of filtered entries"

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

    # Reset all filters and confirm counts
    processor.reset()
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 12580, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 12580
    ), "Wrong number of filtered entries"

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Check counts for totally unfiltered data
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 11903, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 11903
    ), "Wrong number of filtered entries"

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 10385, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 10385
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < processor.min_trace_length) == 0

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 1678, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1678
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < processor.min_trace_length) == 0

    # Reset all filters and confirm counts
    processor.reset()
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 12580, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 11903, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 11903
    ), "Wrong number of filtered entries"

    #
    # 3D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # 3D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Check counts for totally unfiltered data
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 5812, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 5812, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 5812
    ), "Wrong number of filtered entries"

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 4654, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 4654
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 1589, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1589
    ), "Wrong number of filtered entries"

    # Reset all filters and confirm counts
    processor.reset()
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 5812, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 5812, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 5812
    ), "Wrong number of filtered entries"

    #
    # 3D_ValidOnly.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # 3D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Check counts for totally unfiltered data
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 5812, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 5492, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 5492
    ), "Wrong number of filtered entries"

    # Apply EFO filter and check counts
    processor.filter_by_1d_range("efo", (13823.70184744663, 48355.829889892586))
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 4334, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 4334
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < processor.min_trace_length) == 0

    # Apply CFR filter and check counts
    processor.filter_by_1d_range("cfr", (-0.015163637960486809, 0.2715112942104868))
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 1280, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1280
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < processor.min_trace_length) == 0

    # Reset all filters and confirm counts
    processor.reset()
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert reader.num_valid_entries == 5812, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 5492, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 5492
    ), "Wrong number of filtered entries"


def test_eco_value_extraction(extract_raw_npy_data_files):
    #
    # 2D_ValidOnly.npy
    #
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")

    # Test first 15 eco values
    eco = reader.processed_dataframe["eco"].values
    assert np.all(
        eco[:15]
        == np.array(
            [199, 266, 371, 321, 234, 306, 274, 245, 218, 259, 290, 248, 189, 155, 236]
        )
    )

    # Test last 15 eco values
    assert np.all(
        eco[-15:]
        == np.array(
            [173, 177, 157, 151, 150, 150, 181, 156, 167, 175, 161, 166, 150, 200, 162]
        )
    )

    #
    # 3D_ValidOnly.npy
    #
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")

    # Test first 15 eco values
    eco = reader.processed_dataframe["eco"].values
    assert np.all(
        eco[:15]
        == np.array(
            [93, 108, 101, 87, 113, 58, 159, 110, 84, 90, 70, 152, 187, 215, 70]
        )
    )

    # Test last 15 eco values
    assert np.all(
        eco[-15:]
        == np.array([60, 68, 66, 52, 60, 58, 79, 55, 50, 63, 61, 55, 62, 61, 54])
    )


def test_weighted_localizations(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Turn on weighted localization calculation
    processor.use_weighted_localizations = True

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        eco_rel = frame["eco"] / frame["eco"].sum()
        x_w = (frame["x"] * eco_rel).sum()
        y_w = (frame["y"] * eco_rel).sum()
        z_w = (frame["z"] * eco_rel).sum()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    #
    #

    # Turn off weighted localization calculation
    processor.use_weighted_localizations = False

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        x_w = frame["x"].mean()
        y_w = frame["y"].mean()
        z_w = frame["z"].mean()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Turn on weighted localization calculation
    processor.use_weighted_localizations = True

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        eco_rel = frame["eco"] / frame["eco"].sum()
        x_w = (frame["x"] * eco_rel).sum()
        y_w = (frame["y"] * eco_rel).sum()
        z_w = (frame["z"] * eco_rel).sum()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    #
    #

    # Turn off weighted localization calculation
    processor.use_weighted_localizations = False

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        x_w = frame["x"].mean()
        y_w = frame["y"].mean()
        z_w = frame["z"].mean()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    # 3D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Turn on weighted localization calculation
    processor.use_weighted_localizations = True

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        eco_rel = frame["eco"] / frame["eco"].sum()
        x_w = (frame["x"] * eco_rel).sum()
        y_w = (frame["y"] * eco_rel).sum()
        z_w = (frame["z"] * eco_rel).sum()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    #
    #

    # Turn off weighted localization calculation
    processor.use_weighted_localizations = False

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        x_w = frame["x"].mean()
        y_w = frame["y"].mean()
        z_w = frame["z"].mean()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    # 3D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Turn on weighted localization calculation
    processor.use_weighted_localizations = True

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        eco_rel = frame["eco"] / frame["eco"].sum()
        x_w = (frame["x"] * eco_rel).sum()
        y_w = (frame["y"] * eco_rel).sum()
        z_w = (frame["z"] * eco_rel).sum()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"

    #
    #
    #

    # Turn off weighted localization calculation
    processor.use_weighted_localizations = False

    # Get weighted localizations
    df_loc = processor.weighted_localizations

    # Get filtered dataframe
    df_filt = processor.filtered_dataframe

    # Make sure the TIDs match
    assert np.all(np.unique(df_loc["tid"].values) == np.unique(df_filt["tid"].values))

    # Test extracted localizations
    for tid, frame in df_filt.groupby("tid"):
        x_w = frame["x"].mean()
        y_w = frame["y"].mean()
        z_w = frame["z"].mean()
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values[0])
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values[0])
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values[0])
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"


def test_apply_threshold(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    num_values = processor.num_values
    assert processor.num_values == 12580, "Wrong total number of entries"

    processor.filter_by_single_threshold(prop="dwell", threshold=7, larger_than=True)

    num_values_larger = processor.num_values
    assert processor.num_values == 2428, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["dwell"] < 7).sum() == 0, "Failed filtering."

    processor.reset()
    assert processor.num_values == 12580, "Failed processor reset."

    processor.filter_by_single_threshold(prop="dwell", threshold=7, larger_than=False)

    num_values_smaller = processor.num_values
    assert processor.num_values == 10152, "Wrong total number of filtered entries"
    assert num_values_smaller + num_values_larger == num_values, "Failed partition."
    assert (processor.filtered_dataframe["dwell"] >= 7).sum() == 0, "Failed filtering."

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    num_values = processor.num_values
    assert processor.num_values == 11903, "Wrong total number of entries"

    processor.filter_by_single_threshold(prop="dwell", threshold=7, larger_than=True)

    num_values_larger = processor.num_values
    assert processor.num_values == 1757, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["dwell"] < 7).sum() == 0, "Failed filtering."

    processor.reset()
    assert processor.num_values == 11903, "Failed processor reset."

    processor.filter_by_single_threshold(prop="dwell", threshold=7, larger_than=False)

    num_values_smaller = processor.num_values
    assert processor.num_values == 9355, "Wrong total number of filtered entries"
    # Notice that the global filtering after filter_by_single_threshold() makes the sum
    # num_values_smaller + num_values_larger < num_values!
    assert num_values_smaller + num_values_larger == 11112, "Failed partition."
    assert num_values_smaller + num_values_larger < num_values, "Failed partition."
    assert (processor.filtered_dataframe["dwell"] >= 7).sum() == 0, "Failed filtering."


def test_filter_dataframe_by_2d_range(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    assert processor.num_values == 12580, "Wrong total number of entries"

    # Filter by range
    processor.filter_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-12000, -13000)
    )  # y range will be flipped

    assert processor.num_values == 1165, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    assert processor.num_values == 11903, "Wrong total number of entries"

    # Filter by range
    processor.filter_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-12000, -13000)
    )  # y range will be flipped

    assert processor.num_values == 1098, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."


def test_select_and_filter_dataframe_by_2d_range(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do not filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Select (that is, get a view) by range
    df = processor.select_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-13000, -12000)
    )

    # Please notice that the selection is NOT followed by apply_global_filters().
    # Since apply_global_filters() does not filter away anything, we expect the
    # number of entries in the selected and the filtered dataframes to be the same!
    # localizations per trace and is filtered away!
    assert len(df.index) == 1165, "Wrong total number of filtered entries"
    assert (df["x"] < 2000).sum() == 0, "Failed filtering."
    assert (df["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (df["y"] < -13000).sum() == 0, "Failed filtering."
    assert (df["y"] >= -12000).sum() == 0, "Failed filtering."

    # Now compare with the filter by the same range
    processor.filter_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-13000, -12000)
    )
    assert processor.num_values == 1165, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."

    # Make sure all entries are the same
    assert (
        (df == processor.filtered_dataframe).all().all()
    ), "The selected and filtered set are not identical."

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 4 (filter short traces)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Select (that is, get a view) by range
    df = processor.select_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-13000, -12000)
    )

    # Please notice that the selection is NOT followed by apply_global_filters().
    # The filtering below with the same 2D range leaves a TID with less than 4
    # localizations per trace and is filtered away!
    assert len(df.index) == 1099, "Wrong total number of filtered entries"
    assert (df["x"] < 2000).sum() == 0, "Failed filtering."
    assert (df["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (df["y"] < -13000).sum() == 0, "Failed filtering."
    assert (df["y"] >= -12000).sum() == 0, "Failed filtering."

    # Now compare with the filter by the same range
    processor.filter_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-13000, -12000)
    )
    assert processor.num_values == 1098, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."

    # There should be just one TID difference
    select_tids = np.unique(df["tid"].values)
    filter_tids = np.unique(processor.filtered_dataframe["tid"].values)
    diff = np.setdiff1d(select_tids, filter_tids, assume_unique=True)

    assert len(diff) == 1, "Unexpected number of different TIDs."


def test_select_by_1d_range_and_get_stats(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1 (do nto filter anything)
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Select (that is, get a view) by range
    df = processor.select_by_1d_range("tim", x_range=(0.0, 60.0))

    assert len(df.index) == 814, "Wrong total number of filtered entries"
    assert (df["tim"] < 0.0).sum() == 0, "Failed filtering."
    assert (df["tim"] >= 60.0).sum() == 0, "Failed filtering."

    # Get the stats for this dataframe view
    df_stats = processor.calculate_statistics_on(df)

    # Not get the internal statistics after filtering on the same range
    processor.filter_by_1d_range("tim", (0.0, 60.0))

    # Make sure all entries are the same
    assert df_stats.equals(
        processor.filtered_dataframe_stats
    ), "The selected and filtered set are not identical."


def test_proper_application_of_global_filters():

    # FILTER 1D RANGE

    # We expect 8 entries
    processor = MinFluxProcessor(MockMinFluxReader(), min_trace_length=1)
    assert len(processor.filtered_dataframe.index) == 8

    # We filter out 2, and we should be left with 3 for 51 and 3 for 54 = 6
    processor.filter_by_1d_range("x", (0.0, 15.0))
    assert len(processor.filtered_dataframe.index) == 6

    processor.min_trace_length = 4

    processor.reset()

    # We expect 5 entries (51 is filtered out to begin with)
    assert len(processor.filtered_dataframe.index) == 5

    # We filter out 2, and the remaining 3 should be suppressed by the global
    # filters since now processor.min_trace_length is 4.
    processor.filter_by_1d_range("x", (0.0, 15.0))
    assert len(processor.filtered_dataframe.index) == 0

    # FILTER 2D RANGE

    processor.min_trace_length = 1

    processor.reset()

    # We filter out 2, and we should be left with 3 for 51 and 3 for 54 = 6
    processor.filter_by_2d_range("x", "y", (0.0, 15.0), (3.0, 18.0))
    assert len(processor.filtered_dataframe.index) == 6

    processor.min_trace_length = 4

    processor.reset()

    # We expect 5 entries (51 is filtered out to begin with)
    assert len(processor.filtered_dataframe.index) == 5

    # We filter out 2, and the remaining 3 should be suppressed by the global
    # filters since now processor.min_trace_length is 4.
    processor.filter_by_2d_range("x", "y", (0.0, 15.0), (3.0, 18.0))
    assert len(processor.filtered_dataframe.index) == 0

    # FILTER 1D SINGLE THRESHOLD

    processor.min_trace_length = 1

    processor.reset()

    # We expect 8 entries
    assert len(processor.filtered_dataframe.index) == 8

    # We filter out 2, and we should be left with 3 for 51 and 3 for 54 = 6
    processor.filter_by_single_threshold("x", 15.0, larger_than=False)
    assert len(processor.filtered_dataframe.index) == 6

    processor.min_trace_length = 4

    processor.reset()

    # We expect 5 entries (51 is filtered out to begin with)
    assert len(processor.filtered_dataframe.index) == 5

    # We filter out 2, and the remaining 3 should be suppressed by the global
    # filters since now processor.min_trace_length is 4.
    processor.filter_by_single_threshold("x", 15.0, larger_than=False)
    assert len(processor.filtered_dataframe.index) == 0


def test_filter_1d_complement(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Select (that is, get a view) by range
    processor.filter_by_1d_range_complement("tim", x_range=(2000, 3000))

    assert (
        len(processor.filtered_dataframe.index) == 10600
    ), "Wrong total number of filtered entries"
    selected = (
        (processor.filtered_dataframe["tim"] >= 2000)
        & (processor.filtered_dataframe["tim"] < 3000)
    ).values.sum()
    assert selected == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 1102, "Failed filtering."
    assert (
        processor.filtered_dataframe["x"] >= 3000
    ).sum() == 6237, "Failed filtering."

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 4
    #

    # Do not filter anything
    processor.min_trace_length = 4

    # Read and process file
    processor.reset()

    # Select (that is, get a view) by range
    processor.filter_by_1d_range_complement("tim", x_range=(2000, 3000))

    assert (
        len(processor.filtered_dataframe.index) == 10053
    ), "Wrong total number of filtered entries"
    selected = (
        (processor.filtered_dataframe["tim"] >= 2000)
        & (processor.filtered_dataframe["tim"] < 3000)
    ).values.sum()
    assert selected == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] < 1046).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 5882).sum() == 0, "Failed filtering."


def test_filter_by_1d_stats_mock_reader():

    # MockMinFluxReader
    #
    # min_trace_length = 1
    #

    #
    # Filter that rejects everything
    #

    # Process mock reader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Explicitly extract all tids that have trace lengths inside x_range
    x_range = (0.0, 2.0)
    subset = processor.filtered_dataframe_stats[
        (
            (processor.filtered_dataframe_stats["n"] >= x_range[0])
            & (processor.filtered_dataframe_stats["n"] <= x_range[1])
        )
    ][["tid", "n"]]

    # All should be gone
    assert len(subset.index) == 0, "Unexpected number of filtered entries."

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 0
    ), "No TIDs expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 0
    ), "No TIDs expected."

    #
    # Filter that rejects nothing
    #

    # Process mock reader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Explicitly extract all tids that have trace lengths inside x_range
    x_range = (0.0, 8.0)
    subset = processor.filtered_dataframe_stats[
        (
            (processor.filtered_dataframe_stats["n"] >= x_range[0])
            & (processor.filtered_dataframe_stats["n"] <= x_range[1])
        )
    ][["tid", "n"]]

    # Both TIDs should be there
    assert len(subset.index) == 2, "Unexpected number of filtered entries."

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 2
    ), "Two TIDs expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([51, 54])
    ), "TIDs 51 and 54 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 2
    ), "Two TIDs expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values)
        == np.array([51, 54])
    ), "TIDs 51 and 54 expected."

    #
    # Filter that rejects one TID
    #

    # Explicitly extract all tids that have trace lengths inside x_range
    x_range = (0.0, 4.0)
    subset = processor.filtered_dataframe_stats[
        (
            (processor.filtered_dataframe_stats["n"] >= x_range[0])
            & (processor.filtered_dataframe_stats["n"] <= x_range[1])
        )
    ][["tid", "n"]]

    # One TID should be there
    assert len(subset.index) == 1, "Unexpected number of filtered entries."

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([51])
    ), "TID 51 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 1
    ), "Two TIDs expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values) == np.array([51])
    ), "TID 51 expected."


def test_filter_by_1d_stats_with_fluo_id_mock_reader():
    #
    # Filter that rejects everything but as a function
    # of the assigned fluorophore ID.
    #

    #
    # Current fluorophore ID = 0: keep all TIDs
    #

    x_range = (0.0, 8.0)

    # Process mock reader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophore IDs
    processor.set_fluorophore_ids(np.array([2, 2, 2, 1, 1, 1, 1, 1]))

    # Now filter
    processor.current_fluorophore_id = 0

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 2
    ), "Two TIDs expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([51, 54])
    ), "TIDs 51 and 54 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 2
    ), "Two TIDs expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values)
        == np.array([51, 54])
    ), "TIDs 51 and 54 expected."

    #
    # Current fluorophore ID = 1
    #
    # The range rejects TID 54 if ID == 1
    #

    x_range = (0.0, 4.0)

    # Process mock reader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophore IDs
    processor.set_fluorophore_ids(np.array([2, 2, 2, 1, 1, 1, 1, 1]))

    # Set current fluorophore ID to 1
    processor.current_fluorophore_id = 1

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 0
    ), "No TIDs expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 0
    ), "No TIDs expected."

    # IF we change to fluorophore ID == 2, the TID 51 should still be there
    processor.current_fluorophore_id = 2

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([51])
    ), "TID 51 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values) == np.array([51])
    ), "TID 51 expected."

    #
    # Current fluorophore ID = 2
    #
    # The range does not reject TID 51 if ID == 2
    #

    x_range = (0.0, 4.0)

    # Process mock reader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophore IDs
    processor.set_fluorophore_ids(np.array([2, 2, 2, 1, 1, 1, 1, 1]))

    # Now filter
    processor.current_fluorophore_id = 2

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([51])
    ), "TID 51 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values) == np.array([51])
    ), "TID 51 expected."

    # If we change to fluorophore ID == 1, the TID 54 should still be there
    processor.current_fluorophore_id = 1

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([54])
    ), "TID 51 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values) == np.array([54])
    ), "TID 51 expected."

    #
    # Current fluorophore ID = 2
    #
    # The range rejects TID 51 if ID == 2
    #

    x_range = (3.5, 4.5)

    # Process mock reader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Assign fluorophore IDs
    processor.set_fluorophore_ids(np.array([2, 2, 2, 1, 1, 1, 1, 1]))

    # Now filter
    processor.current_fluorophore_id = 2

    # Now call the filter_by_1d_stats() function
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 0
    ), "No TIDs expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 0
    ), "No TIDs expected."

    # If we change to fluorophore ID == 1, the TID 54 should still be there
    processor.current_fluorophore_id = 1

    # Test
    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == np.array([54])
    ), "TID 51 expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 1
    ), "One TID expected."
    assert np.all(
        np.unique(processor.filtered_dataframe_stats["tid"].values) == np.array([54])
    ), "TID 51 expected."

    # If we now apply the filter again, also 54 should go.
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    assert (
        len(np.unique(processor.filtered_dataframe["tid"].values)) == 0
    ), "No TIDs expected."
    assert (
        len(np.unique(processor.filtered_dataframe_stats["tid"].values)) == 0
    ), "No TIDs expected."


def test_filter_by_1d_stats(extract_raw_npy_data_files):

    #
    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1
    #

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Extract all tids that have trace lengths outside x_range
    x_range = (0.0, 100.0)
    subset = processor.filtered_dataframe_stats[
        (
            (processor.filtered_dataframe_stats["n"] >= x_range[0])
            & (processor.filtered_dataframe_stats["n"] <= x_range[1])
        )
    ][["tid", "n"]]

    # Make sure that the extracted TIDs are correct
    assert len(subset.index) == 1245, "Wrong number of extracted TIDs."
    assert (
        np.sum((subset["n"] < x_range[0]).values)
        + np.sum((subset["n"] > x_range[1]).values)
        == 0
    ), "No TIDs should be in the rejected range."
    valid_tids = subset["tid"].values

    # Filter all traces that have less than 100 localizations
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Now check the filtered dataframe
    assert np.all(
        np.unique(processor.filtered_dataframe["tid"].values) == valid_tids
    ), "Unexpected subset of selected TIDs."

    # Make sure the filtered stats dataframe has been updated as well.
    assert (
        np.sum((processor.filtered_dataframe_stats["n"] < x_range[0]).values)
        + np.sum((processor.filtered_dataframe_stats["n"] > x_range[1]).values)
        == 0
    ), "The filtered stats dataframe has not been update or has been updated incorrectly"

    # 2D_ValidOnly.npy
    #
    # min_trace_length = 1
    #
    # Now assign fluorophore IDs and filter again

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Keep track of all TIDs that are outside the range
    x_range = (0.0, 100.0)
    tids_outside = processor.filtered_dataframe_stats[
        (
            (processor.filtered_dataframe_stats["n"] < x_range[0])
            | (processor.filtered_dataframe_stats["n"] > x_range[1])
        )
    ]["tid"].values

    # Assign the first half (of the TIDs) to fluorophore ID 2 and the second half to fluorophore ID 1
    thresh = np.median(processor.filtered_dataframe_stats["tid"].values)
    fluo_ids = np.ones(len(processor.filtered_dataframe.index))
    fluo_ids[processor.filtered_dataframe["tid"].values < thresh] = 2
    processor.set_fluorophore_ids(fluorophore_ids=fluo_ids.astype(int))

    # Rejected TIDs per fluorophore
    rejected_tid_fluo_2 = tids_outside[tids_outside < thresh]
    rejected_tid_fluo_1 = tids_outside[tids_outside >= thresh]

    # Check the number of assigned fluorophores
    assert (
        int(np.sum(processor.filtered_dataframe["fluo"].values == 0)) == 0
    ), "All rows should be assigned to fluo 1 or 2."
    n_fluo_1 = int(np.sum(processor.filtered_dataframe["fluo"].values == 1))
    n_fluo_2 = int(np.sum(processor.filtered_dataframe["fluo"].values == 2))
    assert n_fluo_1 + n_fluo_2 == len(
        processor.filtered_dataframe.index
    ), "All rows should be assigned to fluo 1 or 2."
    assert n_fluo_1 == 6011, "Wrong number of rows assigned to fluorophore 1."
    assert n_fluo_2 == 6569, "Wrong number of rows assigned to fluorophore 2."

    # Now set the active fluorophore to 1
    processor.current_fluorophore_id = 1

    # Filter all traces that have less than 100 localizations
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Now check that only the TIDs that where associated to fluorophore 1 were filtered by x_range
    subset_fluo_1 = processor.filtered_dataframe_stats[["tid", "n"]]
    assert np.all(
        subset_fluo_1["tid"].values >= thresh
    ), "Unexpected TIDs for fluorophore 1."
    tids_outside_fluo_1 = tids_outside[tids_outside >= thresh]
    assert np.all(
        rejected_tid_fluo_1 == tids_outside_fluo_1
    ), "Unexpected set of rejected TIDs."

    # Now set the active fluorophore to 2
    processor.current_fluorophore_id = 2

    # Filter all traces that have less than 100 localizations
    processor.filter_by_1d_stats(x_prop_stats="n", x_range=x_range)

    # Now check that only the TIDs that where associated to fluorophore 1 were filtered by x_range
    subset_fluo_2 = processor.filtered_dataframe_stats[["tid", "n"]]
    assert np.all(
        subset_fluo_2["tid"].values < thresh
    ), "Unexpected TIDs for fluorophore 2."
    tids_outside_fluo_2 = tids_outside[tids_outside < thresh]
    assert np.all(
        rejected_tid_fluo_2 == tids_outside_fluo_2
    ), "Unexpected set of rejected TIDs."
