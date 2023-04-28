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

import numpy as np

from pyminflux.processor import MinFluxProcessor


class MinFluxWriter:
    @staticmethod
    def write_npy(processor: MinFluxProcessor, file_name: Union[Path, str]) -> bool:
        """Write an Imspector-compatible NumPy structured array."""

        # Get the raw data
        filtered_array = processor.filtered_numpy_array
        if filtered_array is None:
            return False

        # Append the fluorophore ID data
        filtered_array["fluo"] = processor.filtered_dataframe["fluo"].astype(np.uint8)

        # Save the filtered structured NumPy array to disk
        try:
            np.save(str(file_name), filtered_array)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False

        return True

    def write_csv(processor: MinFluxProcessor, file_name: Union[Path, str]) -> bool:
        """Write a comma-separated-value file."""

        # Save the filtered dataframe to disk
        try:
            processor.filtered_dataframe.to_csv(file_name, index=False)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False

        return True
