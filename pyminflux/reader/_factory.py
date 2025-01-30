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
#  limitations under the License.
from pathlib import Path
from typing import Union

# Avoid circular imports
from pyminflux.reader._reader import MinFluxReader
from pyminflux.reader._reader_v2 import MinFluxReaderV2
from pyminflux.reader.util import (
    get_reader_version_for_mat_file,
    get_reader_version_for_npy_file,
    get_reader_version_for_pmx_file,
)


class MinFluxReaderFactory:
    __docs__ = "Factory for MinFluxReader version 1 or 2."

    @staticmethod
    def get_reader(filename: Union[Path, str]) -> (MinFluxReader, str):
        """Returns the appropriate reader class for the passed filename.

        Usage
        -----

        reader_class = MinFluxReaderFactory.get_reader(filename)  # One of MinFluxReader or MinFluxReaderV2
        reader = reader_class(filename, valid, z_scaling_factor, is_tracking, pool_dcr, dwell_time)

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx`, `.npy`, `.mat`, or '.json' file to read.

        Returns
        -------

        reader: MinFluxReader class
            Either version 1 or version 2 MinFluxReader. Version 2 MinFluxReader supports Imspector >=24.10.
        """

        # Check if the file exists
        filename = Path(filename)

        if not filename.is_file():
            return None, f"{filename} does not exist."

        # Determine file type
        file_ext = filename.suffix.lower()

        # Check the file
        if file_ext == ".npy":
            reader_version = get_reader_version_for_npy_file(filename)
        elif file_ext == ".mat":
            reader_version = get_reader_version_for_mat_file(filename)
        elif file_ext == ".json":
            reader_version = 2
        elif file_ext == ".pmx":
            reader_version = get_reader_version_for_pmx_file(filename)
        else:
            return None, f"{filename} is not supported."

        # Return the requested reader
        if reader_version == 1:
            return MinFluxReader, ""
        elif reader_version == 2:
            return MinFluxReaderV2, ""
        elif reader_version == -1:
            # In case parsing the files failed, the returned reader_version would be 1.
            return None, f"Error processing file {filename}."
        else:
            # Unexpected version number
            return None, f"MinFluxReader version {reader_version} is not supported."
