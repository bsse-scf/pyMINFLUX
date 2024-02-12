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

from pathlib import Path
from pickle import UnpicklingError
from typing import Union

import numpy as np
from scipy.io import loadmat

from pyminflux.reader import MinFluxReader
from pyminflux.reader.metadata import RawArrayMetadata
from pyminflux.reader.util import (
    migrate_npy_array,
    convert_from_mat,
    find_last_valid_iteration,
)


class MinFluxRawArrayParser:
    __docs__ = "Parser of MINFLUX metadata in `.npy` or `.mat` formats."

    __slots__ = [
        "_filename",
        "_is_mat",
        "_is_npy",
    ]

    def __init__(
        self,
        filename: Union[Path, str],
    ):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.npy` or `.mat` file to read
        """

        # Store the filename
        self._filename: Path = Path(filename)
        if not self._filename.is_file():
            raise IOError(f"The file {self._filename} does not seem to exist.")

        # Check the format
        filename_low = str(self._filename).lower()

        self._is_npy: bool = filename_low.endswith(".npy")
        self._is_mat: bool = filename_low.endswith(".mat")

        if not (self._is_npy or self._is_mat):
            raise IOError(f"The format of file {self._filename} is not supported.")

    def scan(self) -> RawArrayMetadata:
        """Scan the file and returns a RawArrayMetadata object.

        Returns
        -------

        metadata: RawArrayMetadata
            Metadata about the raw MINFLUX file.
        """

        # Scan file
        data_array = None
        if self._is_npy:
            # NumPy `.npy` array
            try:
                # Load the arr
                data_array = np.load(str(self._filename))
            except (OSError, UnpicklingError, ValueError, EOFError, FileNotFoundError):
                pass

        elif self._is_mat:
            # MATLAB `.mat` file
            try:
                data_array = migrate_npy_array(convert_from_mat(str(self._filename)))
            except (FileNotFoundError, ValueError):
                pass

        else:
            raise IOError(f"The format of file {self._filename} is not supported.")

        # Check if we have a valid array
        if data_array is None:
            raise IOError(f"The format of file {self._filename} is not supported.")

        # Set properties
        num_entries = data_array["itr"].shape[0]
        num_iterations = data_array["itr"].shape[1]
        is_3d = float(np.nanmean(data_array["itr"][:, -1]["loc"][:, -1])) != 0.0
        last_valid = find_last_valid_iteration(data_array)
        is_valid = True

        # Create metadata object
        metadata = RawArrayMetadata(
            is_3d=is_3d,
            is_valid=is_valid,
            last_valid=last_valid,
            num_entries=num_entries,
            num_iterations=num_iterations,
        )

        # Return the metadata object
        return metadata
