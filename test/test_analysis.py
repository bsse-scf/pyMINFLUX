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

    # Use 1kHz bins
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=False, bin_size=1000.0)
    assert len(n_efo) == 420
    assert b_efo[1] - b_efo[0] == 1000.0
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Use automatic bin_size determination
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=True)
    assert len(n_efo) == 377
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Check defaults
    n_efo, _, b_efo, _ = prepare_histogram(efo)
    assert len(n_efo) == 377
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == 13821.63722748869
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 48225.758832542466
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

    # Use 1kHz bins
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=True)
    assert len(n_efo) == 126
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Use automatic bin_size determination
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=False, bin_size=1000.0)
    assert len(n_efo) == 284
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert pytest.approx(lower_bound, 1e-4) == 12000.0, "The lower bound is wrong!"
    assert pytest.approx(upper_bound, 1e-4) == 23000.0, "The upper bound is wrong!"

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

    # Use 1kHz bins
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=False, bin_size=1000.0)
    assert len(n_efo) == 2125
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Use automatic bin_size determination
    n_efo, _, b_efo, _ = prepare_histogram(efo, auto_bins=True)
    assert len(n_efo) == 1281
    assert pytest.approx(n_efo.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert pytest.approx(lower_bound, 1e-4) == 11600, "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 44760.60183679485
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
    assert processor.num_values == 10385, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 10385
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < state.min_num_loc_per_trace) == 0

    # Apply CFR filter and check counts
    processor.apply_range_filter(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 9133, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 9133
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < state.min_num_loc_per_trace) == 0

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
    assert processor.num_values == 4334, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 4334
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < state.min_num_loc_per_trace) == 0

    # Apply CFR filter and check counts
    processor.apply_range_filter(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 5812
    ), "Wrong total number of entries"
    assert processor.num_values == 1280, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1280
    ), "Wrong number of filtered entries"

    # Make sure the global filters were applied
    counts = processor.filtered_dataframe["tid"].value_counts(normalize=False)
    assert np.sum(counts.values < state.min_num_loc_per_trace) == 0

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
    # Initialize state
    state = State()

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 1
    #

    # Make sure to not filter anything
    state.min_num_loc_per_trace = 1

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
    # state.min_num_loc_per_trace = 4
    #

    # This time filter short traces
    state.min_num_loc_per_trace = 4

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
    # state.min_num_loc_per_trace = 1
    #

    # Make sure to not filter anything
    state.min_num_loc_per_trace = 1

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
    # state.min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "3D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
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
        exp_x_w = float(df_loc[df_loc["tid"] == tid]["x"].values)
        exp_y_w = float(df_loc[df_loc["tid"] == tid]["y"].values)
        exp_z_w = float(df_loc[df_loc["tid"] == tid]["z"].values)
        assert (
            pytest.approx(x_w, 1e-4) == exp_x_w
        ), "The weighted x localization is wrong!"
        assert (
            pytest.approx(y_w, 1e-4) == exp_y_w
        ), "The weighted y localization is wrong!"
        assert (
            pytest.approx(z_w, 1e-4) == exp_z_w
        ), "The weighted z localization is wrong!"


def test_apply_filter_by_indices(extract_raw_npy_data_files):
    # Initialize state
    state = State()

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 1
    #

    # Make sure to not filter anything
    state.min_num_loc_per_trace = 1

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Get a copy of the filtered dataframe
    df = processor.filtered_dataframe.copy()

    # Check counts for totally unfiltered data
    assert len(df.index) == 12580, "Wrong total number of entries"

    # Select every second entry
    flags = np.zeros(len(df.index), dtype=bool)
    flags[::2] = True
    processor.apply_filter_by_logical_indexing(flags)

    # Check the result
    assert len(processor.filtered_dataframe) == 6290, "Wrong total number of entries"
    for i in range(len(processor.filtered_dataframe)):
        assert np.all(
            processor.filtered_dataframe.iloc[i] == df.iloc[i * 2]
        ), "Unexpected filtering result!"


def test_apply_threshold(extract_raw_npy_data_files):
    # Initialize state
    state = State()

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 1
    #

    # Make sure to not filter anything
    state.min_num_loc_per_trace = 1

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    num_values = processor.num_values
    assert processor.num_values == 12580, "Wrong total number of entries"

    processor.apply_threshold(prop="dwell", threshold=7, larger_than=True)

    num_values_larger = processor.num_values
    assert processor.num_values == 2428, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["dwell"] < 7).sum() == 0, "Failed filtering."

    processor.reset()
    assert processor.num_values == 12580, "Failed processor reset."

    processor.apply_threshold(prop="dwell", threshold=7, larger_than=False)

    num_values_smaller = processor.num_values
    assert processor.num_values == 10152, "Wrong total number of filtered entries"
    assert num_values_smaller + num_values_larger == num_values, "Failed partition."
    assert (processor.filtered_dataframe["dwell"] >= 7).sum() == 0, "Failed filtering."

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 4
    #

    # This time filter short traces
    state.min_num_loc_per_trace = 4

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    num_values = processor.num_values
    assert processor.num_values == 11903, "Wrong total number of entries"

    processor.apply_threshold(prop="dwell", threshold=7, larger_than=True)

    num_values_larger = processor.num_values
    assert processor.num_values == 1757, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["dwell"] < 7).sum() == 0, "Failed filtering."

    processor.reset()
    assert processor.num_values == 11903, "Failed processor reset."

    processor.apply_threshold(prop="dwell", threshold=7, larger_than=False)

    num_values_smaller = processor.num_values
    assert processor.num_values == 9355, "Wrong total number of filtered entries"
    # Notice that the global filtering after apply_threshold() makes the sum
    # num_values_smaller + num_values_larger < num_values!
    assert num_values_smaller + num_values_larger == 11112, "Failed partition."
    assert num_values_smaller + num_values_larger < num_values, "Failed partition."
    assert (processor.filtered_dataframe["dwell"] >= 7).sum() == 0, "Failed filtering."


def test_filter_dataframe_by_xy_range(extract_raw_npy_data_files):
    # Initialize state
    state = State()

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 1
    #

    # Make sure to not filter anything
    state.min_num_loc_per_trace = 1

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    assert processor.num_values == 12580, "Wrong total number of entries"

    # Filter by range
    processor.filter_dataframe_by_xy_range(
        x_range=(2000, 3000), y_range=(-12000, -13000)
    )  # y range will be flipped

    assert processor.num_values == 1165, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 4
    #

    # This time filter short traces
    state.min_num_loc_per_trace = 4

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    assert processor.num_values == 11903, "Wrong total number of entries"

    # Filter by range
    processor.filter_dataframe_by_xy_range(
        x_range=(2000, 3000), y_range=(-12000, -13000)
    )  # y range will be flipped

    assert processor.num_values == 1099, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."
