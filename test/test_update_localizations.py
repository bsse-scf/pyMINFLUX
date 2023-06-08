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
        self._df = pd.DataFrame(columns=["tid", "x", "y", "z"])
        self._df["tid"] = tids
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


def test_update_localizations_with_mock_reader(tmpdir):

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 1 (do not filter anything)
    #

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=1)

    # Check counts for totally unfiltered data
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 40, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 40
    ), "Wrong number of filtered entries"

    # Assign fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set active fluorophore to 0
    processor.current_fluorophore_id = 0

    # Update all localizations
    processor.update_localizations(
        x=np.zeros(len(processor.filtered_dataframe.index)),
        y=np.zeros(len(processor.filtered_dataframe.index)),
        z=np.zeros(len(processor.filtered_dataframe.index)),
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.sum(), 0.0), "Unexpected mean x localization."
    assert np.isclose(my.sum(), 0.0), "Unexpected mean x localization."
    assert np.isclose(mz.sum(), 0.0), "Unexpected mean x localization."

    # Set active fluorophore to 1
    processor.current_fluorophore_id = 1

    # Update localizations for fluorophore 1
    n = np.sum(processor.filtered_dataframe["fluo"] == 1)
    processor.update_localizations(
        x=-3.0 * np.ones(n), y=-3.0 * np.ones(n), z=-3.0 * np.ones(n)
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), -3.0), "Unexpected mean x localization."

    # Make sure that the coordinates for fluorophore 2 were not touched
    processor.current_fluorophore_id = 2

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), 0.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), 0.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), 0.0), "Unexpected mean x localization."

    # Update localizations for fluorophore 2
    n = np.sum(processor.filtered_dataframe["fluo"] == 2)
    processor.update_localizations(
        x=-7.0 * np.ones(n), y=-7.0 * np.ones(n), z=-7.0 * np.ones(n)
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), -7.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -7.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), -7.0), "Unexpected mean x localization."

    # Make sure that the coordinates for fluorophore 1 were not touched
    processor.current_fluorophore_id = 1

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), -3.0), "Unexpected mean x localization."

    #
    # MockMinFluxReader
    #
    # min_num_loc_per_trace = 4 (filter short traces)
    #

    # MockMinFluxReader
    reader = MockMinFluxReader()
    processor = MinFluxProcessor(reader, min_trace_length=4)

    # Check counts for totally unfiltered data
    assert len(reader.processed_dataframe.index) == 40, "Wrong total number of entries"
    assert reader.num_valid_entries == 40, "Wrong number of valid entries"
    assert reader.num_invalid_entries == 0, "Wrong number of invalid entries"
    assert processor.num_values == 35, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 35
    ), "Wrong number of filtered entries"

    # Assign fluorophore IDs
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set active fluorophore to 0
    processor.current_fluorophore_id = 0

    # Update all localizations
    processor.update_localizations(
        x=np.zeros(len(processor.filtered_dataframe.index)),
        y=np.zeros(len(processor.filtered_dataframe.index)),
        z=np.zeros(len(processor.filtered_dataframe.index)),
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.sum(), 0.0), "Unexpected mean x localization."
    assert np.isclose(my.sum(), 0.0), "Unexpected mean x localization."
    assert np.isclose(mz.sum(), 0.0), "Unexpected mean x localization."

    # Set active fluorophore to 1
    processor.current_fluorophore_id = 1

    # Update localizations for fluorophore 1
    n = np.sum(processor.filtered_dataframe["fluo"] == 1)
    processor.update_localizations(
        x=-3.0 * np.ones(n), y=-3.0 * np.ones(n), z=-3.0 * np.ones(n)
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), -3.0), "Unexpected mean x localization."

    # Make sure that the coordinates for fluorophore 2 were not touched
    processor.current_fluorophore_id = 2

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), 0.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), 0.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), 0.0), "Unexpected mean x localization."

    # Update localizations for fluorophore 2
    n = np.sum(processor.filtered_dataframe["fluo"] == 2)
    processor.update_localizations(
        x=-7.0 * np.ones(n), y=-7.0 * np.ones(n), z=-7.0 * np.ones(n)
    )

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), -7.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -7.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), -7.0), "Unexpected mean x localization."

    # Make sure that the coordinates for fluorophore 1 were not touched
    processor.current_fluorophore_id = 1

    # Check the stats
    mx = processor.filtered_dataframe_stats["mx"].values
    my = processor.filtered_dataframe_stats["my"].values
    mz = processor.filtered_dataframe_stats["mz"].values

    # Test
    assert np.isclose(mx.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(my.mean(), -3.0), "Unexpected mean x localization."
    assert np.isclose(mz.mean(), -3.0), "Unexpected mean x localization."
