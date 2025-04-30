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

from pyminflux.processor import MinFluxProcessor


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
    def test_fluorophore_ids(self):
        """Fluorophore ids to be used for testing."""
        return np.array(
            [
                1,  # 51
                1,  # 54
                1,
                1,
                1,
                1,
                1,
                2,  # 70
                2,
                2,
                2,
                2,
                1,  # 97
                1,
                1,
                1,
                1,
                1,
                1,
                2,  # 102
                2,  # 151
                2,
                2,
                2,  # 171
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                2,
                1,  # 176
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
    def is_tracking(self):
        """This is a localization dataset and not a tracking one."""
        return False

    @property
    def test_swapped_fluorophore_ids(self):
        """Swapped fluorophore ids to be used for testing."""
        tmp = self.test_fluorophore_ids.copy()
        tmp[tmp == 2] = 0
        tmp += 1
        return tmp


def test_drop_first_n_locs():

    #
    # No filtering on trace length and localizations to drop
    #

    # Create mock reader
    reader = MockMinFluxReader()

    # No filtering on traces
    processor = MinFluxProcessor(reader, num_locs_to_drop=0, min_trace_length=1)

    # Assign fluorophores
    processor.set_fluorophore_ids(reader.test_fluorophore_ids)

    # Set current fluorophore id to 0
    processor.current_fluorophore_id = 0
    assert processor.current_fluorophore_id == 0, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 40, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 1, "Unexpected number of entries."
    assert len(tid_54) == 6, "Unexpected number of entries."
    assert len(tid_70) == 5, "Unexpected number of entries."
    assert len(tid_97) == 7, "Unexpected number of entries."
    assert len(tid_102) == 1, "Unexpected number of entries."
    assert len(tid_151) == 3, "Unexpected number of entries."
    assert len(tid_171) == 9, "Unexpected number of entries."
    assert len(tid_176) == 8, "Unexpected number of entries."

    # Set current fluorophore id to 1
    processor.current_fluorophore_id = 1
    assert processor.current_fluorophore_id == 1, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 22, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 1, "Unexpected number of entries."
    assert len(tid_54) == 6, "Unexpected number of entries."
    assert len(tid_70) == 0, "Unexpected number of entries."
    assert len(tid_97) == 7, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 0, "Unexpected number of entries."
    assert len(tid_176) == 8, "Unexpected number of entries."

    # Set current fluorophore id to 2
    processor.current_fluorophore_id = 2
    assert processor.current_fluorophore_id == 2, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 18, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 0, "Unexpected number of entries."
    assert len(tid_70) == 5, "Unexpected number of entries."
    assert len(tid_97) == 0, "Unexpected number of entries."
    assert len(tid_102) == 1, "Unexpected number of entries."
    assert len(tid_151) == 3, "Unexpected number of entries."
    assert len(tid_171) == 9, "Unexpected number of entries."
    assert len(tid_176) == 0, "Unexpected number of entries."

    #
    # Set number of initial localizations to drop to 3
    #

    # Create mock reader
    reader = MockMinFluxReader()

    # No filtering on traces
    processor = MinFluxProcessor(reader, num_locs_to_drop=3, min_trace_length=1)

    # Assign fluorophores
    processor.set_fluorophore_ids(
        np.array([1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1])
    )

    # Set current fluorophore id to 0
    processor.current_fluorophore_id = 0
    assert processor.current_fluorophore_id == 0, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 20, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 3, "Unexpected number of entries."
    assert len(tid_70) == 2, "Unexpected number of entries."
    assert len(tid_97) == 4, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 6, "Unexpected number of entries."
    assert len(tid_176) == 5, "Unexpected number of entries."

    # Set current fluorophore id to 1
    processor.current_fluorophore_id = 1
    assert processor.current_fluorophore_id == 1, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 12, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 3, "Unexpected number of entries."
    assert len(tid_70) == 0, "Unexpected number of entries."
    assert len(tid_97) == 4, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 0, "Unexpected number of entries."
    assert len(tid_176) == 5, "Unexpected number of entries."

    # Set current fluorophore id to 2
    processor.current_fluorophore_id = 2
    assert processor.current_fluorophore_id == 2, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 8, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 0, "Unexpected number of entries."
    assert len(tid_70) == 2, "Unexpected number of entries."
    assert len(tid_97) == 0, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 6, "Unexpected number of entries."
    assert len(tid_176) == 0, "Unexpected number of entries."

    #
    # Set number of initial localizations to drop to 3 and min trace length to 4
    #

    # Create mock reader
    reader = MockMinFluxReader()

    # No filtering on traces
    processor = MinFluxProcessor(reader, num_locs_to_drop=3, min_trace_length=4)

    # Assign fluorophores
    processor.set_fluorophore_ids(
        np.array([1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1])
    )

    # Set current fluorophore id to 0
    processor.current_fluorophore_id = 0
    assert processor.current_fluorophore_id == 0, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 15, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 0, "Unexpected number of entries."
    assert len(tid_70) == 0, "Unexpected number of entries."
    assert len(tid_97) == 4, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 6, "Unexpected number of entries."
    assert len(tid_176) == 5, "Unexpected number of entries."

    # Set current fluorophore id to 1
    processor.current_fluorophore_id = 1
    assert processor.current_fluorophore_id == 1, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 9, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 0, "Unexpected number of entries."
    assert len(tid_70) == 0, "Unexpected number of entries."
    assert len(tid_97) == 4, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 0, "Unexpected number of entries."
    assert len(tid_176) == 5, "Unexpected number of entries."

    # Set current fluorophore id to 2
    processor.current_fluorophore_id = 2
    assert processor.current_fluorophore_id == 2, "Unexpected fluorophore id."

    assert len(processor.filtered_dataframe) == 6, "Unexpected number of entries."
    tid_51 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 51]
    tid_54 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 54]
    tid_70 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 70]
    tid_97 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 97]
    tid_102 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 102]
    tid_151 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 151]
    tid_171 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 171]
    tid_176 = processor.filtered_dataframe[processor.filtered_dataframe["tid"] == 176]
    assert len(tid_51) == 0, "Unexpected number of entries."
    assert len(tid_54) == 0, "Unexpected number of entries."
    assert len(tid_70) == 0, "Unexpected number of entries."
    assert len(tid_97) == 0, "Unexpected number of entries."
    assert len(tid_102) == 0, "Unexpected number of entries."
    assert len(tid_151) == 0, "Unexpected number of entries."
    assert len(tid_171) == 6, "Unexpected number of entries."
    assert len(tid_176) == 0, "Unexpected number of entries."
