import zipfile
from pathlib import Path

import numpy as np
import pytest

from pyminflux.analysis import (
    find_first_peak_bounds,
    get_robust_threshold,
    prepare_histogram,
)
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.state import State


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


@pytest.fixture(autouse=False)
def extract_bounds_extraction_data_archive(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    npy_file_names = [
        Path(__file__).parent / "data" / "2d_only_cfr.npy",
        Path(__file__).parent / "data" / "2d_only_efo.npy",
        Path(__file__).parent / "data" / "3d_only_cfr.npy",
        Path(__file__).parent / "data" / "3d_only_efo.npy",
        Path(__file__).parent / "data" / "3d_only_overlabeled_efo.npy",
        Path(__file__).parent / "data" / "3d_only_overlabeled_cfr.npy",
    ]

    # Make sure to extract the test data if it is not already there
    need_to_extract = False
    for npy_file_name in npy_file_names:
        if not npy_file_name.is_file():
            need_to_extract = True
            break

    if need_to_extract:
        archive_filename = Path(__file__).parent / "data" / "bounds_extraction.zip"
        with zipfile.ZipFile(archive_filename, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_efo_cfr_bounds_extraction(extract_bounds_extraction_data_archive):
    #
    # 2D_only_efo.npy
    #

    # Load data
    efo = np.load(Path(__file__).parent / "data" / "2d_only_efo.npy")
    assert efo is not None, "Could not load file."
    assert len(efo) == 11903, "Wrong dimensions for 2d_only_efo."

    # Calculate the normalized histogram
    n_efo, _, b_efo, _ = prepare_histogram(efo)
    assert len(n_efo) == 376
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == 13823.70184744663
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 48355.829889892586
    ), "The upper bound is wrong!"

    #
    # 2D_only_cfr.npy
    #

    # Load data
    cfr = np.load(Path(__file__).parent / "data" / "2d_only_cfr.npy")
    assert cfr is not None, "Could not load file."
    assert len(cfr) == 11903, "Wrong dimensions for 2d_only_cfr."

    # Get robust thresholds
    upper_bound, lower_bound, med, mad = get_robust_threshold(cfr, factor=2.0)
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.015163637960486809
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.2715112942104868
    ), "The median value is wrong!"
    assert pytest.approx(med, 1e-4) == 0.128173828125, "The lower bound is wrong!"
    assert (
        pytest.approx(mad, 1e-4) == 0.0716687330427434
    ), "The median absolute difference value is wrong!"

    #
    # 3D_only_efo.npy
    #

    # Load data
    efo = np.load(Path(__file__).parent / "data" / "3d_only_efo.npy")
    assert efo is not None, "Could not load file."
    assert len(efo) == 5492, "Wrong dimensions for 3d_only_efo."

    # Calculate the normalized histogram
    n_efo, _, b_efo, _ = prepare_histogram(efo)
    assert len(n_efo) == 125
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == 12410.76051302978
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 46457.65683676113
    ), "The upper bound is wrong!"

    #
    # 3D_only_cfr.npy
    #

    # Load data
    cfr = np.load(Path(__file__).parent / "data" / "3d_only_cfr.npy")
    assert cfr is not None, "Could not load file."
    assert len(cfr) == 5492, "Wrong dimensions for 3d_only_cfr."

    # Get robust thresholds
    upper_bound, lower_bound, med, mad = get_robust_threshold(cfr, factor=2.0)
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.0006192938657819114
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.7052091376157819
    ), "The median value is wrong!"
    assert pytest.approx(med, 1e-4) == 0.352294921875, "The lower bound is wrong!"
    assert (
        pytest.approx(mad, 1e-4) == 0.17645710787039096
    ), "The median absolute difference value is wrong!"

    #
    # 3D_only_overlabeled_efo.npy
    #

    # Load data
    efo = np.load(Path(__file__).parent / "data" / "3d_only_overlabeled_efo.npy")
    assert efo is not None, "Could not load file."
    assert len(efo) == 81888, "Wrong dimensions for 3d_only_overlabeled_efo."

    # Calculate the normalized histogram
    n_efo, _, b_efo, _ = prepare_histogram(efo)
    assert len(n_efo) == 1280
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == 11600.761913082442
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 44791.84027317494
    ), "The upper bound is wrong!"

    #
    # 3D_only_overlabeled_cfr.npy
    #

    # Load data
    cfr = np.load(Path(__file__).parent / "data" / "3d_only_overlabeled_cfr.npy")
    assert cfr is not None, "Could not load file."
    assert len(cfr) == 81888, "Wrong dimensions for 3d_only_overlabeled_cfr."

    # Get robust thresholds
    upper_bound, lower_bound, med, mad = get_robust_threshold(cfr, factor=2.0)
    assert (
        pytest.approx(lower_bound, 1e-4) == 0.45367502494940626
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.8646843500505937
    ), "The median value is wrong!"
    assert pytest.approx(med, 1e-4) == 0.6591796875, "The lower bound is wrong!"
    assert (
        pytest.approx(mad, 1e-4) == 0.10275233127529688
    ), "The median absolute difference value is wrong!"


def test_filter_raw_dataframes(extract_raw_npy_data_files):
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
    processor.apply_range_filter(
        "efo", min_threshold=13823.70184744663, max_threshold=48355.829889892586
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 11064, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 11064
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.apply_range_filter(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 9760, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 9760
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
    # min_num_loc_per_trace = 4
    #

    # Now set a minimum number of localization per trace (global filter)
    state.min_num_loc_per_trace = 4

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
    processor.apply_range_filter(
        "efo", min_threshold=13823.70184744663, max_threshold=48355.829889892586
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 10468, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 10468
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.apply_range_filter(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 9346, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 9346
    ), "Wrong number of filtered entries"

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
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 3D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
    processor.apply_range_filter(
        "efo", min_threshold=13823.70184744663, max_threshold=48355.829889892586
    )
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 4654, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 4654
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.apply_range_filter(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
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
    # min_num_loc_per_trace = 4
    #

    # Now set a minimum number of localization per trace (global filter)
    state.min_num_loc_per_trace = 4

    # 3D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
    processor.apply_range_filter(
        "efo", min_threshold=13823.70184744663, max_threshold=48355.829889892586
    )
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 4391, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 4391
    ), "Wrong number of filtered entries"

    # Apply CFR filter and check counts
    processor.apply_range_filter(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 1521, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1521
    ), "Wrong number of filtered entries"

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

    #
    # 3D_ValidOnly.npy
    #
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")

    # Test first 15 eco values
    eco = reader.processed_dataframe["eco"].values
    assert np.all(
        eco[:15]
        == np.array(
            [200, 294, 214, 287, 228, 172, 306, 292, 198, 197, 239, 288, 323, 371, 198]
        )
    )
