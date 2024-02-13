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

import pytest

import numpy as np

from pyminflux.reader.util import find_last_valid_iteration


@pytest.fixture(autouse=False)
def extract_parsing_archives(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    #
    # 2D/3D localization datasets
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

    #
    # Tracking datasets
    #
    npy_file_names = [
        Path(__file__).parent / "data" / "2d_tracking.npy",
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk3D.npy",
        Path(__file__).parent / "data" / "precision_immobilized_seqTrkFast.npy",
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk.npy",
        Path(__file__).parent / "data" / "tracking_free_seqTrck3D.npy",
        Path(__file__).parent / "data" / "tracking_free_seqTrckFast.npy",
        Path(__file__).parent / "data" / "tracking_free_seqTrck.npy",
    ]

    # Make sure to extract the test data if it is not already there
    need_to_extract = False
    for npy_file_name in npy_file_names:
        if not npy_file_name.is_file():
            need_to_extract = True
            break

    if need_to_extract:
        archive_filename = Path(__file__).parent / "data" / "tracking.zip"
        with zipfile.ZipFile(archive_filename, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_last_valid_iteration(extract_parsing_archives):

    # 2D_ValidOnly.npy
    data_array = np.load(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is False, "Dataset is expected to be 2D."
    assert num_iterations == 5, "Dataset is expected to have 5 iterations."
    assert num_entries == 12580, "Dataset is expected to have 12580 entries."
    assert last_valid["cfr_index"] == 4, "Last valid CFR index should be 4."
    assert last_valid["dcr_index"] == 4, "Last valid DCR index should be 4."
    assert last_valid["eco_index"] == 4, "Last valid ECO index should be 4."
    assert last_valid["efo_index"] == 4, "Last valid EFO index should be 4."
    assert last_valid["loc_index"] == 4, "Last valid LOC index should be 4."

    # 3D_ValidOnly.npy
    data_array = np.load(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is True, "Dataset is expected to be 3D."
    assert num_iterations == 10, "Dataset is expected to have 10 iterations."
    assert num_entries == 5812, "Dataset is expected to have 5812 entries."
    assert last_valid["cfr_index"] == 6, "Last valid CFR index should be 6."
    assert last_valid["dcr_index"] == 9, "Last valid DCR index should be 9."
    assert last_valid["eco_index"] == 9, "Last valid ECO index should be 9."
    assert last_valid["efo_index"] == 9, "Last valid EFO index should be 9."
    assert last_valid["loc_index"] == 9, "Last valid LOC index should be 9."

    # 2d_tracking.npy
    data_array = np.load(Path(__file__).parent / "data" / "2d_tracking.npy")
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is False, "Dataset is expected to be 2D."
    assert num_iterations == 4, "Dataset is expected to have 4 iterations."
    assert num_entries == 38105, "Dataset is expected to have 38105 entries."
    assert last_valid["cfr_index"] == 1, "Last valid CFR index should be 1."
    assert last_valid["dcr_index"] == 3, "Last valid DCR index should be 3."
    assert last_valid["eco_index"] == 3, "Last valid ECO index should be 3."
    assert last_valid["efo_index"] == 3, "Last valid EFO index should be 3."
    assert last_valid["loc_index"] == 3, "Last valid LOC index should be 3."

    # precision_immobilized_seqTrk3D.npy
    data_array = np.load(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk3D.npy"
    )
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is True, "Dataset is expected to be 3D."
    assert num_iterations == 5, "Dataset is expected to have 5 iterations."
    assert num_entries == 3826, "Dataset is expected to have 3826 entries."
    assert last_valid["cfr_index"] == 2, "Last valid CFR index should be 2."
    assert last_valid["dcr_index"] == 4, "Last valid DCR index should be 4."
    assert last_valid["eco_index"] == 4, "Last valid ECO index should be 4."
    assert last_valid["efo_index"] == 4, "Last valid EFO index should be 4."
    assert last_valid["loc_index"] == 4, "Last valid LOC index should be 4."

    # precision_immobilized_seqTrkFast.npy
    data_array = np.load(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrkFast.npy"
    )
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is False, "Dataset is expected to be 2D."
    assert num_iterations == 4, "Dataset is expected to have 4 iterations."
    assert num_entries == 13100, "Dataset is expected to have 13100 entries."
    assert last_valid["cfr_index"] == 1, "Last valid CFR index should be 1."
    assert last_valid["dcr_index"] == 3, "Last valid DCR index should be 3."
    assert last_valid["eco_index"] == 3, "Last valid ECO index should be 3."
    assert last_valid["efo_index"] == 3, "Last valid EFO index should be 3."
    assert last_valid["loc_index"] == 3, "Last valid LOC index should be 3."

    # precision_immobilized_seqTrk.npy
    data_array = np.load(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk.npy"
    )
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is False, "Dataset is expected to be 2D."
    assert num_iterations == 4, "Dataset is expected to have 4 iterations."
    assert num_entries == 15189, "Dataset is expected to have 15189 entries."
    assert last_valid["cfr_index"] == 3, "Last valid CFR index should be 3."
    assert last_valid["dcr_index"] == 3, "Last valid DCR index should be 3."
    assert last_valid["eco_index"] == 3, "Last valid ECO index should be 3."
    assert last_valid["efo_index"] == 3, "Last valid EFO index should be 3."
    assert last_valid["loc_index"] == 3, "Last valid LOC index should be 3."
    print("\n* * * Why is cfr_index == 3 for precision_immobilized_seqTrk.npy? * * *")

    # tracking_free_seqTrck3D.npy
    data_array = np.load(Path(__file__).parent / "data" / "tracking_free_seqTrck3D.npy")
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is True, "Dataset is expected to be 3D."
    assert num_iterations == 5, "Dataset is expected to have 4 iterations."
    assert num_entries == 27735, "Dataset is expected to have 27735 entries."
    assert last_valid["cfr_index"] == 2, "Last valid CFR index should be 2."
    assert last_valid["dcr_index"] == 4, "Last valid DCR index should be 4."
    assert last_valid["eco_index"] == 4, "Last valid ECO index should be 4."
    assert last_valid["efo_index"] == 4, "Last valid EFO index should be 4."
    assert last_valid["loc_index"] == 4, "Last valid LOC index should be 4."

    # tracking_free_seqTrckFast.npy
    data_array = np.load(
        Path(__file__).parent / "data" / "tracking_free_seqTrckFast.npy"
    )
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is False, "Dataset is expected to be 2D."
    assert num_iterations == 4, "Dataset is expected to have 4 iterations."
    assert num_entries == 160079, "Dataset is expected to have 160079 entries."
    assert last_valid["cfr_index"] == 1, "Last valid CFR index should be 1."
    assert last_valid["dcr_index"] == 3, "Last valid DCR index should be 3."
    assert last_valid["eco_index"] == 3, "Last valid ECO index should be 3."
    assert last_valid["efo_index"] == 3, "Last valid EFO index should be 3."
    assert last_valid["loc_index"] == 3, "Last valid LOC index should be 3."

    # tracking_free_seqTrck.npy
    data_array = np.load(Path(__file__).parent / "data" / "tracking_free_seqTrck.npy")
    data_array = data_array[data_array["vld"]]
    num_iterations = data_array["itr"]["itr"].shape[1]
    num_entries = data_array["itr"]["itr"].shape[0]
    last_valid = find_last_valid_iteration(data_array)
    is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0

    assert is_3d is False, "Dataset is expected to be 2D."
    assert num_iterations == 4, "Dataset is expected to have 4 iterations."
    assert num_entries == 184421, "Dataset is expected to have 184421 entries."
    assert last_valid["cfr_index"] == 3, "Last valid CFR index should be 3."
    assert last_valid["dcr_index"] == 3, "Last valid DCR index should be 3."
    assert last_valid["eco_index"] == 3, "Last valid ECO index should be 3."
    assert last_valid["efo_index"] == 3, "Last valid EFO index should be 3."
    assert last_valid["loc_index"] == 3, "Last valid LOC index should be 3."
    print("\n* * * Why is cfr_index == 3 for tracking_free_seqTrck.npy? * * *")
