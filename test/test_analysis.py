import zipfile
from pathlib import Path

import numpy as np
import pytest

import pyminflux
from pyminflux.analysis import find_first_peak_bounds, prepare_histogram


@pytest.fixture(autouse=False)
def extract_peak_analysis_data_archive(tmpdir):
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
        archive_filename = Path(__file__).parent / "data" / "peak_analysis.zip"
        with zipfile.ZipFile(archive_filename, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_find_first_peak_bounds(extract_peak_analysis_data_archive):

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

    # Calculate the normalized histogram
    n_cfr, _, b_cfr, _ = prepare_histogram(cfr)
    assert len(n_cfr) == 119
    assert pytest.approx(n_cfr.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_cfr, b_cfr, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.24971619159990507
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.795376329360338
    ), "The upper bound is wrong!"

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

    # Calculate the normalized histogram
    n_cfr, _, b_cfr, _ = prepare_histogram(cfr)
    assert len(n_cfr) == 32
    assert pytest.approx(n_cfr.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_cfr, b_cfr, min_rel_prominence=0.01, med_filter_support=5, qc=False
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.09818585947658014
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.7850102721958083
    ), "The upper bound is wrong!"

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
        n_efo, b_efo, min_rel_prominence=0.01, med_filter_support=5, qc=True
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

    # Calculate the normalized histogram
    n_cfr, _, b_cfr, _ = prepare_histogram(cfr)
    assert len(n_cfr) == 133
    assert pytest.approx(n_cfr.sum(), 1e-4) == 1.0, "The histogram is not normalized!"

    # Find the first peak bounds
    lower_bound, upper_bound = find_first_peak_bounds(
        n_cfr, b_cfr, min_rel_prominence=0.01, med_filter_support=5, qc=True
    )
    assert (
        pytest.approx(lower_bound, 1e-4) == -0.09818585947658014
    ), "The lower bound is wrong!"
    assert (
        pytest.approx(upper_bound, 1e-4) == 0.7850102721958083
    ), "The upper bound is wrong!"
