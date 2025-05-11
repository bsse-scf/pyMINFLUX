#  Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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

import h5py
import numpy as np

from pyminflux.processor import MinFluxProcessor
from pyminflux.ui.state import State


class PMXWriter:
    """Writer of (processed) MINFLUX into native `.pmx` format."""

    def __init__(self, processor: MinFluxProcessor):
        self.processor = processor
        self.state = State()
        self._message = ""

        # HDF5 has no native support for boolean datatypes; therefore
        # we convert back and forth between bool and np.int8
        self.boolean_columns = ["vld", "fnl", "bot", "eot"]

    def write(self, file_name: Union[Path, str]) -> bool:

        try:

            # Create HDF5 file with the structure
            with h5py.File(file_name, "w") as f:

                # Set file version attribute
                f.attrs["file_version"] = "3.0"

                # Set MinFluxReader version
                f.attrs["reader_version"] = self.processor.reader.version

                # Create groups
                raw_data_group = f.create_group("raw")
                parameters_group = f.create_group("parameters")
                paraview_group = f.create_group("paraview")

                # If the reader is version 1, we store filtered_raw_data_array
                # as "raw/npy" for backwards compatibility
                if self.processor.reader.version == 1:
                    raw_data_group.create_dataset(
                        "npy",
                        data=self.processor.filtered_raw_data_array,
                        compression="gzip",
                    )
                elif self.processor.reader.version == 2:
                    self._store_dataframe(
                        raw_data_group,
                        self.processor.filtered_raw_dataframe,
                        "df",
                    )
                else:
                    raise ValueError("Unexpected reader version!")

                # Store the filtered dataframe for compatibility with ParaView
                self._store_dataframe(
                    paraview_group,
                    self.processor.filtered_dataframe,
                    "dataframe",
                )

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

    def _store_dataframe(self, group, dataframe, datataset_name):
        """Write a Pandas DataFrame in a way that it can be reloaded without external dependencies.

        To support external tools like ParaView (via our reader plug-in) that may not have required
        Pandas dependencies (like "tables"), we save the dataframe as a NumPy array and save the
        column names and types as attributes.
        """

        if dataframe is None:
            return

        # Convert the column names to a list of strings
        column_names = dataframe.columns.tolist()

        # Convert column data types to a list of strings
        column_types = [str(dataframe[col].dtype) for col in dataframe.columns]

        # Convert boolean types to np.int8 to be hdf5-compatible
        for col in self.boolean_columns:
            if col in dataframe.columns:
                dataframe[col] = np.int8(dataframe[col])

        dataset = group.create_dataset(
            datataset_name,
            data=dataframe.to_numpy(),
            compression="gzip",
        )

        # Store the column names as an attribute of the dataset
        dataset.attrs["column_names"] = column_names

        # Store (original) column data types as attribute of the dataset
        dataset.attrs["column_types"] = column_types

        # We preserve the index as well (as a Dataset, since it can be large)
        index_data = np.array(dataframe.index)
        group.create_dataset(
            f"{datataset_name}_index", data=index_data, compression="gzip"
        )

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
        group.create_dataset("pool_dcr", data=np.int8(self.state.pool_dcr))
