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

from pathlib import Path
from typing import Union

import h5py
import numpy as np

from pyminflux.processor import MinFluxProcessor
from pyminflux.state import State


class PyMinFluxNativeWriter:
    __docs__ = "Writer of (processed) MINFLUX into native `.pmx` format."

    def __init__(self, processor: MinFluxProcessor):
        self._processor = processor
        self._state = State()
        self._message = ""

    def write(self, file_name: Union[Path, str]) -> bool:

        try:

            # Create HDF5 file with the structure
            with h5py.File(file_name, "w") as f:

                # Set file version attribute
                f.attrs["file_version"] = "1.0"

                # Create groups
                raw_data_group = f.create_group("raw")
                _ = f.create_group("paraview")
                parameters_group = f.create_group("parameters")

                # Store the filtered numpy array (with fluorophores)
                raw_data_group.create_dataset(
                    "npy", data=self._processor.filtered_numpy_array, compression="gzip"
                )

                # Store important parameters
                parameters_group.create_dataset(
                    "z_scaling_factor", data=self._processor.z_scaling_factor
                )
                parameters_group.create_dataset(
                    "min_trace_length", data=self._processor.min_num_loc_per_trace
                )
                parameters_group.create_dataset(
                    "efo_thresholds", data=self._state.efo_thresholds
                )
                parameters_group.create_dataset(
                    "cfr_thresholds", data=self._state.cfr_thresholds
                )
                parameters_group.create_dataset(
                    "num_fluorophores", data=self._processor.num_fluorophores
                )

            # Append (mode = "a") the filtered dataframe as a proper Pandas DataFrame
            # to be used by the ParaView plugin
            self._processor.filtered_dataframe.to_hdf(
                file_name, key="/paraview/dataframe", mode="a"
            )

            # No error
            self._message = ""

            # Return success
            return True

        except Exception as e:

            # Set the error message
            self._message = str(e)

            return False

    @property
    def message(self):
        """Return last error message."""
        return self._message
