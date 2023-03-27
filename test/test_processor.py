import zipfile
from pathlib import Path

import numpy as np
import pytest

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
    # Initialize State
    state = State()

    #
    # 2D_All.npy
    #
    # min_num_loc_per_trace = 1
    #

    # Make sure not to filter anything
    state.min_num_loc_per_trace = 1

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader)

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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
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
    # min_num_loc_per_trace = 4
    #

    # Now set a minimum number of localization per trace (global filter)
    state.min_num_loc_per_trace = 4

    # 2D_ValidOnly.npy
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_All.npy")
    processor = MinFluxProcessor(reader)

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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 1678, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1678
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
    assert reader.num_invalid_entries == 687394, "Wrong number of invalid entries"
    assert processor.num_values == 11903, "Wrong number of processed entries"
    assert (
        len(processor.filtered_dataframe.index) == 11903
    ), "Wrong number of filtered entries"

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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
        "cfr", min_threshold=-0.015163637960486809, max_threshold=0.2715112942104868
    )
    assert (
        len(reader.processed_dataframe.index) == 12580
    ), "Wrong total number of entries"
    assert processor.num_values == 1678, "Wrong number of filtered entries"
    assert (
        len(processor.filtered_dataframe.index) == 1678
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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
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
    processor.filter_dataframe_by_1d_range(
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

    # Now set a minimum number of localization per trace (global filter)
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
    # state.min_num_loc_per_trace = 4
    #

    # This time filter short traces
    state.min_num_loc_per_trace = 4

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

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
    processor.filter_dataframe_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-12000, -13000)
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
    processor.filter_dataframe_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-12000, -13000)
    )  # y range will be flipped

    assert processor.num_values == 1099, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."


def test_select_and_filter_dataframe_by_xy_range(extract_raw_npy_data_files):
    # Initialize state
    state = State()

    #
    # 2D_ValidOnly.npy
    # state.min_num_loc_per_trace = 4
    #

    # Now set a minimum number of localization per trace (global filter)
    state.min_num_loc_per_trace = 4

    # Read and process file
    reader = MinFluxReader(Path(__file__).parent / "data" / "2D_ValidOnly.npy")
    processor = MinFluxProcessor(reader)

    # Select (that is, get a view) by range
    df = processor.select_dataframe_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-13000, -12000)
    )

    assert len(df.index) == 1099, "Wrong total number of filtered entries"
    assert (df["x"] < 2000).sum() == 0, "Failed filtering."
    assert (df["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (df["y"] < -13000).sum() == 0, "Failed filtering."
    assert (df["y"] >= -12000).sum() == 0, "Failed filtering."

    # Now compare with the filter by the same range
    processor.filter_dataframe_by_2d_range(
        "x", "y", x_range=(2000, 3000), y_range=(-13000, -12000)
    )
    assert processor.num_values == 1099, "Wrong total number of filtered entries"
    assert (processor.filtered_dataframe["x"] < 2000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["x"] >= 3000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] < -13000).sum() == 0, "Failed filtering."
    assert (processor.filtered_dataframe["y"] >= -12000).sum() == 0, "Failed filtering."

    # Make sure all entries are the same
    assert (
        (df == processor.filtered_dataframe).all().all()
    ), "The selected and filtered set are not identical."
