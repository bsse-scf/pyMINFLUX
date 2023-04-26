import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pyminflux.reader import MinFluxReader


@pytest.fixture(autouse=False)
def extract_multi_format_data_files(tmpdir):
    """Fixture to execute asserts before and after a test is run"""

    #
    # Setup
    #

    # Make sure to extract the test data if it is not already there
    npy_file_name = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    mat_file_name = Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    zip_file_name = Path(__file__).parent / "data" / "input_multi_format.zip"
    if not npy_file_name.is_file() or not mat_file_name.is_file():
        with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
            zip_ref.extractall(Path(__file__).parent / "data")

    yield  # This is where the testing happens

    #
    # Teardown
    #

    # Do whatever is needed to clean up:
    # - Nothing for the moment


def test_compare_readers(extract_multi_format_data_files):
    # Read both formats
    reader_npy = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.npy"
    )
    reader_mat = MinFluxReader(
        Path(__file__).parent / "data" / "230321-111601_minflux2D_3.mat"
    )

    # Compare the dimensions of the read dataframes
    assert (
        reader_npy.processed_dataframe.shape == reader_mat.processed_dataframe.shape
    ), "Dimensions mismatch."
    # Compare the read dataframes
    assert np.allclose(
        reader_npy.processed_dataframe.values,
        reader_mat.processed_dataframe.values,
        equal_nan=True,
    ), "Mismatch in read values."
