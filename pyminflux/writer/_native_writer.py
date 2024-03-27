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
        self.processor = processor
        self.state = State()
        self._message = ""

    def write(self, file_name: Union[Path, str]) -> bool:

        try:

            # Create HDF5 file with the structure
            with h5py.File(file_name, "w") as f:

                # Set file version attribute
                f.attrs["file_version"] = "2.0"

                # Create groups
                raw_data_group = f.create_group("raw")
                paraview_group = f.create_group("paraview")
                parameters_group = f.create_group("parameters")

                # Store the filtered numpy array (with fluorophores)
                raw_data_group.create_dataset(
                    "npy", data=self.processor.filtered_numpy_array, compression="gzip"
                )

                # Store the pandas dataframe: to make sure not to depend on additional
                # dependencies (like "tables") that are not bundled with ParaView, we
                # save the dataframe as a NumPy array and save the column names and types
                # as attributes.
                self._store_dataframe(paraview_group)

                # Store important parameters
                self._store_parameters(parameters_group)

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

    def _store_dataframe(self, group):
        """Write the Pandas DataFrame in a way that it can be reloaded without external dependencies."""

        dataset = group.create_dataset(
            "dataframe",
            data=self.processor.filtered_dataframe.to_numpy(),
            compression="gzip",
        )

        # Convert the column names to a list of strings
        column_names = self.processor.filtered_dataframe.columns.tolist()

        # Convert column data types to a list of strings
        column_types = [
            str(self.processor.filtered_dataframe[col].dtype)
            for col in self.processor.filtered_dataframe.columns
        ]

        # Store the column names as an attribute of the dataset
        dataset.attrs["column_names"] = column_names

        # Store column data types as attribute of the dataset
        dataset.attrs["column_types"] = column_types

        # We preserve the index as well (as a Dataset, since it can be large)
        index_data = np.array(self.processor.filtered_dataframe.index)
        group.create_dataset("dataframe_index", data=index_data, compression="gzip")

    def _store_parameters(self, group):
        """Write important parameters."""

        group.create_dataset("z_scaling_factor", data=self.processor.z_scaling_factor)
        group.create_dataset("min_trace_length", data=self.processor.min_trace_length)
        if self.state.applied_efo_thresholds is not None:
            group.create_dataset(
                "applied_efo_thresholds",
                data=self.state.applied_efo_thresholds,
            )
        if self.state.applied_cfr_thresholds is not None:
            group.create_dataset(
                "applied_cfr_thresholds",
                data=self.state.applied_cfr_thresholds,
            )
        if self.state.applied_tr_len_thresholds is not None:
            group.create_dataset(
                "applied_tr_len_thresholds",
                data=self.state.applied_tr_len_thresholds,
            )
        if self.state.applied_time_thresholds is not None:
            group.create_dataset(
                "applied_time_thresholds",
                data=self.state.applied_time_thresholds,
            )
        group.create_dataset("num_fluorophores", data=self.processor.num_fluorophores)
        group.create_dataset("dwell_time", data=self.state.dwell_time)
        group.create_dataset("scale_bar_size", data=self.state.scale_bar_size)

        # HDF5 does not have a native boolean type, so we save as int8 and convert it
        # back to boolean on read.
        group.create_dataset("is_tracking", data=np.int8(self.state.is_tracking))
