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
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import h5py


@dataclass
class Metadata:
    z_scaling_factor: float
    min_trace_length: int
    efo_thresholds: tuple[int, int]
    cfr_thresholds: tuple[float, float]
    num_fluorophores: int


class MetadataReader:
    """Reads metadata information from `.pmx` files."""

    @staticmethod
    def scan(filename: Union[Path, str]):
        """Constructor.

        Parameters
        ----------

        filename: Union[Path, str]
            Full path to the `.pmx` file to scan.
        """

        # Open the file
        with h5py.File(filename, "r") as f:

            # Read the file_version attribute
            file_version = f.attrs["file_version"]

            if file_version != "1.0":
                return None

            # Read the parameters
            try:
                z_scaling_factor = f["parameters/z_scaling_factor"][()]
                min_trace_length = f["parameters/min_trace_length"][()]
                efo_thresholds = tuple(f["parameters/efo_thresholds"][:])
                cfr_thresholds = tuple(f["parameters/cfr_thresholds"][:])
                num_fluorophores = f["parameters/num_fluorophores"][()]
            except:
                return None

        # Store and return
        metadata = Metadata(
            z_scaling_factor=z_scaling_factor,
            min_trace_length=min_trace_length,
            efo_thresholds=efo_thresholds,
            cfr_thresholds=cfr_thresholds,
            num_fluorophores=num_fluorophores,
        )

        return metadata
