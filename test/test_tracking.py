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
import pytest

from pyminflux.analysis import (
    calculate_time_steps,
    calculate_total_distance_traveled,
    get_robust_threshold,
)
from pyminflux.analysis._analysis import calculate_displacements
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader


@pytest.fixture(autouse=False)
def extract_tracking_archives(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
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


def test_tracking_from_npy(extract_tracking_archives):
    #
    # 2D_Tracking.npy
    #
    # Using NumPy

    # Load data
    tracking_2d = np.load(Path(__file__).parent / "data" / "2d_tracking.npy")
    assert tracking_2d is not None, "Could not load file."

    # Check structure
    assert len(tracking_2d.dtype.names) == 9, "Unexpected number of features."
    assert np.all(
        tracking_2d.dtype.names
        == ("itr", "sqi", "gri", "tim", "tid", "vld", "act", "dos", "sky")
    ), "Unexpected feature names."
    assert np.all(
        tracking_2d["itr"].dtype.names
        == (
            "itr",
            "tic",
            "loc",
            "eco",
            "ecc",
            "efo",
            "efc",
            "sta",
            "cfr",
            "dcr",
            "ext",
            "gvy",
            "gvx",
            "eoy",
            "eox",
            "dmz",
            "lcy",
            "lcx",
            "lcz",
            "fbg",
            "lnc",
        )
    ), "Unexpected 'itr' feature names."
    assert tracking_2d["itr"].shape[1] == 4, "Unexpected number of 'itr' localizations."

    # Check data
    efo = tracking_2d["itr"]["efo"][:, 3]
    assert len(efo) == 38105, "Unexpected number of 'efo' measurements."
    assert (
        pytest.approx(efo.min(), 1e-4) == 60060.06006006006
    ), "Unexpected min value of 'efo'."
    assert (
        pytest.approx(efo.max(), 1e-4) == 880880.8808808809
    ), "Unexpected max value of 'efo'."

    cfr = tracking_2d["itr"]["cfr"][:, 3]
    assert len(cfr) == 38105, "Unexpected number of 'cfr' measurements."
    assert (
        pytest.approx(cfr.min(), 1e-4) == -3.0517578125e-05
    ), "Unexpected min value of 'cfr'."
    assert (
        pytest.approx(cfr.max(), 1e-4) == -3.0517578125e-05
    ), "Unexpected max value of 'cfr'."

    #
    # 2D_Tracking.npy
    #
    # Using MinFluxReader

    # Load data
    tracking_2d = MinFluxReader(Path(__file__).parent / "data" / "2d_tracking.npy")
    assert tracking_2d.num_valid_entries != 0, "Could not load file."
    assert tracking_2d.num_valid_entries == 38105, "Unexpected number of valid entries."

    # Check data
    efo = tracking_2d.processed_dataframe["efo"]
    assert (
        pytest.approx(efo.min(), 1e-6) == 60060.06006006006
    ), "Unexpected min value of 'efo'."
    assert (
        pytest.approx(efo.max(), 1e-6) == 880880.8808808809
    ), "Unexpected max value of 'efo'."

    # Please notice: the 2d_tracking.npy dataset has strange data in the last iteration
    # that makes the reader pick it instead of the previous iteration.
    # @TODO: Re-evaluate this!
    cfr = tracking_2d.processed_dataframe["cfr"]
    assert (
        pytest.approx(cfr.min(), 1e-6) == -3.0517578125e-05
    ), "Unexpected min value of 'cfr'."
    assert (
        pytest.approx(cfr.max(), 1e-6) == 0.499725341796875
    ), "Unexpected max value of 'cfr'."


def test_tracking_from_reader_and_processor(extract_tracking_archives):
    # Min trace length to  consider
    min_trace_length = 4

    #
    # 2d_tracking
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "2d_tracking.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 49.91002512390616
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 31.293718267776885
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 53.98030433608855
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 37.93743368907597
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 0.00
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 0.00
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 501.0, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 510.014974276861
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 0.1522000000022672
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.09951963706067685
    ), "Unexpected mad time resolution."

    #
    # precision_immobilized_seqTrk3D
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 16.154817907708743
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 5.363280315345168
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 17.398082992653343
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 6.652914705379723
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 0.00
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 0.00
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 47.00, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 45.96065175169387
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 0.9409749999989003
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.6827751338065132
    ), "Unexpected mad time resolution."

    #
    # precision_immobilized_seqTrk3D
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk3D.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is True

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 16.77324059525086
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 5.720898721269537
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 16.774971827154758
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 7.0786049157967605
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 16.316215290475306
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 4.726000463901208
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 16.00, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 11.860813355275837
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 1.3634999999680986
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.9923423624467126
    ), "Unexpected mad time resolution."

    #
    # precision_immobilized_seqTrkFast
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrkFast.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 20.20228255238626
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 3.960777398143508
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 20.355041176275183
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 3.7856673316913647
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 0.00
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 0.00
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 109.00, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 121.57333689157733
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 0.4193000000043412
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.2961126184041845
    ), "Unexpected mad time resolution."

    #
    # tracking_free_seqTrck3D
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "tracking_free_seqTrck3D.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is True

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 26.28193988854605
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 14.9939347057202
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 26.553785225647452
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 16.833543619800928
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 23.940939013549023
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 11.949423271157572
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 52.00, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 60.78666844578866
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 0.6944250000060492
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.49719046983689835
    ), "Unexpected mad time resolution."

    #
    # tracking_free_seqTrckFast
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "tracking_free_seqTrckFast.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 26.131099635005015
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 8.968755507981896
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 28.643418383045272
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 9.461503635001277
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 0.00
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 0.00
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 406.50, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 436.6261916410918
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 0.7527249999839114
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.6917078088400457
    ), "Unexpected mad time resolution."

    #
    # tracking_free_seqTrck
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "tracking_free_seqTrck.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    _, _, median_sx, mad_sx = get_robust_threshold(
        processor.filtered_dataframe_stats["sx"].to_numpy()
    )
    _, _, median_sy, mad_sy = get_robust_threshold(
        processor.filtered_dataframe_stats["sy"].to_numpy()
    )
    _, _, median_sz, mad_sz = get_robust_threshold(
        processor.filtered_dataframe_stats["sz"].to_numpy()
    )
    _, _, median_n, mad_n = get_robust_threshold(
        processor.filtered_dataframe_stats["n"].to_numpy()
    )
    tim, median_tim, mad_tim = calculate_time_steps(processor.filtered_dataframe)

    assert len(tim.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of time differences."
    assert (
        pytest.approx(median_sx, 1e-6) == 19.95096561847626
    ), "Unexpected x median localization precision."
    assert (
        pytest.approx(mad_sx, 1e-6) == 6.576534424774915
    ), "Unexpected x mad localization precision."
    assert (
        pytest.approx(median_sy, 1e-6) == 18.735888739342528
    ), "Unexpected y median localization precision."
    assert (
        pytest.approx(mad_sy, 1e-6) == 7.003130342120453
    ), "Unexpected y mad localization precision."
    assert (
        pytest.approx(median_sz, 1e-6) == 0.00
    ), "Unexpected z median localization precision."
    assert (
        pytest.approx(mad_sz, 1e-6) == 0.00
    ), "Unexpected z mad localization precision."
    assert pytest.approx(median_n, 1e-6) == 134.00, "Unexpected median trace length."
    assert (
        pytest.approx(mad_n, 1e-6) == 158.63837862681433
    ), "Unexpected mad trace length."
    assert (
        pytest.approx(median_tim, 1e-6) == 1.2482000000204607
    ), "Unexpected median time resolution."
    assert (
        pytest.approx(mad_tim, 1e-6) == 0.9100209049310964
    ), "Unexpected mad time resolution."


def test_calculate_total_distance_traveled(extract_tracking_archives):
    # Parameters
    min_trace_length = 4

    #
    # precision_immobilized_seqTrk3D
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    # Calculate displacements
    displacements, med_d, mad_d = calculate_displacements(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    # Calculate the total distance traveled per tid
    (
        total_distance,
        med,
        mad,
    ) = calculate_total_distance_traveled(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    assert len(total_distance.index) == len(
        processor.filtered_dataframe_stats.index
    ), "Unexpected number of distances."
    assert len(displacements.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of displacements."
    assert (
        pytest.approx(med, 1e-6) == 945.8445877951381
    ), "Unexpected median for the total traveled distance per tid."
    assert (
        pytest.approx(mad, 1e-6) == 908.8712103386998
    ), "Unexpected median absolute deviation for the total traveled distance per tid."
    assert (
        pytest.approx(med_d, 1e-6) == 19.07780436918798
    ), "Unexpected median for all displacements."
    assert (
        pytest.approx(mad_d, 1e-6) == 12.28678312068945
    ), "Unexpected median absolute deviation for all displacements."

    #
    # precision_immobilized_seqTrk3D
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrk3D.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is True

    # Calculate displacements
    displacements, med_d, mad_d = calculate_displacements(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    # Calculate the total distance traveled per tid
    (
        total_distance,
        med,
        mad,
    ) = calculate_total_distance_traveled(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    assert len(total_distance.index) == len(
        processor.filtered_dataframe_stats.index
    ), "Unexpected number of distances."
    assert len(displacements.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of displacements."
    assert (
        pytest.approx(med, 1e-6) == 410.7251004389293
    ), "Unexpected median for the total traveled distance per tid."
    assert (
        pytest.approx(mad, 1e-6) == 351.8878925096984
    ), "Unexpected median absolute deviation for the total traveled distance per tid."
    assert (
        pytest.approx(med_d, 1e-6) == 28.877920840662167
    ), "Unexpected median for all displacements."
    assert (
        pytest.approx(mad_d, 1e-6) == 13.719981778393253
    ), "Unexpected median absolute deviation for all displacements."

    #
    # precision_immobilized_seqTrkFast
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "precision_immobilized_seqTrkFast.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    # Calculate displacements
    displacements, med_d, mad_d = calculate_displacements(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    # Calculate the total distance traveled per tid
    (
        total_distance,
        med,
        mad,
    ) = calculate_total_distance_traveled(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    assert len(total_distance.index) == len(
        processor.filtered_dataframe_stats.index
    ), "Unexpected number of distances."
    assert len(displacements.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of displacements."
    assert (
        pytest.approx(med, 1e-6) == 3110.0166114044587
    ), "Unexpected median for the total traveled distance per tid."
    assert (
        pytest.approx(mad, 1e-6) == 3479.5802586609575
    ), "Unexpected median absolute deviation for the total traveled distance per tid."
    assert (
        pytest.approx(med_d, 1e-6) == 27.995822523087682
    ), "Unexpected median for all displacements."
    assert (
        pytest.approx(mad_d, 1e-6) == 16.00018406679733
    ), "Unexpected median absolute deviation for all displacements."

    #
    # tracking_free_seqTrck3D
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "tracking_free_seqTrck3D.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is True

    # Calculate displacements
    displacements, med_d, mad_d = calculate_displacements(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    # Calculate the total distance traveled per tid
    (
        total_distance,
        med,
        mad,
    ) = calculate_total_distance_traveled(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    assert len(total_distance.index) == len(
        processor.filtered_dataframe_stats.index
    ), "Unexpected number of distances."
    assert len(displacements.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of displacements."
    assert (
        pytest.approx(med, 1e-6) == 1206.2126699478988
    ), "Unexpected median for the total traveled distance per tid."
    assert (
        pytest.approx(mad, 1e-6) == 1392.7747332444576
    ), "Unexpected median absolute deviation for the total traveled distance per tid."
    assert (
        pytest.approx(med_d, 1e-6) == 22.559207065867305
    ), "Unexpected median for all displacements."
    assert (
        pytest.approx(mad_d, 1e-6) == 11.825964413327107
    ), "Unexpected median absolute deviation for all displacements."

    #
    # tracking_free_seqTrckFast
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "tracking_free_seqTrckFast.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    # Calculate displacements
    displacements, med_d, mad_d = calculate_displacements(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    # Calculate the total distance traveled per tid
    (
        total_distance,
        med,
        mad,
    ) = calculate_total_distance_traveled(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    assert len(total_distance.index) == len(
        processor.filtered_dataframe_stats.index
    ), "Unexpected number of distances."
    assert len(displacements.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of displacements."
    assert (
        pytest.approx(med, 1e-6) == 11834.591038905457
    ), "Unexpected median for the total traveled distance per tid."
    assert (
        pytest.approx(mad, 1e-6) == 12779.898733261447
    ), "Unexpected median absolute deviation for the total traveled distance per tid."
    assert (
        pytest.approx(med_d, 1e-6) == 27.81657636134422
    ), "Unexpected median for all displacements."
    assert (
        pytest.approx(mad_d, 1e-6) == 15.918213620957275
    ), "Unexpected median absolute deviation for all displacements."

    #
    # tracking_free_seqTrck
    #
    reader = MinFluxReader(
        Path(__file__).parent / "data" / "tracking_free_seqTrck.npy",
        z_scaling_factor=0.7,
        is_tracking=True,
    )
    processor = MinFluxProcessor(reader, min_trace_length=min_trace_length)
    assert processor.is_3d is False

    # Calculate displacements
    displacements, med_d, mad_d = calculate_displacements(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    # Calculate the total distance traveled per tid
    (
        total_distance,
        med,
        mad,
    ) = calculate_total_distance_traveled(
        processor.filtered_dataframe, is_3d=processor.is_3d
    )

    assert len(total_distance.index) == len(
        processor.filtered_dataframe_stats.index
    ), "Unexpected number of distances."
    assert len(displacements.index) == len(
        processor.filtered_dataframe.index
    ), "Unexpected number of displacements."
    assert (
        pytest.approx(med, 1e-6) == 2736.843343938342
    ), "Unexpected median for the total traveled distance per tid."
    assert (
        pytest.approx(mad, 1e-6) == 3146.8302964660757
    ), "Unexpected median absolute deviation for the total traveled distance per tid."
    assert (
        pytest.approx(med_d, 1e-6) == 18.502447434529394
    ), "Unexpected median for all displacements."
    assert (
        pytest.approx(mad_d, 1e-6) == 12.038166058676897
    ), "Unexpected median absolute deviation for all displacements."
