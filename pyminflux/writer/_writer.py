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

import numpy as np

from pyminflux.processor import MinFluxProcessor


class MinFluxWriter:
    __docs__ = "Writer of (filtered) MINFLUX data to either `.npy` or `.csv` formats."

    @staticmethod
    def write_npy(processor: MinFluxProcessor, file_name: Union[Path, str]) -> bool:
        """Write (filtered) data as a NumPy structured array with the same structure as in the Imspector `.npy` file."""

        # Get the raw data
        filtered_array = processor.filtered_numpy_array
        if filtered_array is None:
            return False

        # Save the filtered structured NumPy array to disk
        try:
            np.save(str(file_name), filtered_array)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False

        return True

    @staticmethod
    def write_csv(processor: MinFluxProcessor, file_name: Union[Path, str]) -> bool:
        """Write (filtered) data as a comma-separated-value `.csv` file."""

        # Save the filtered dataframe to disk
        try:
            processor.filtered_dataframe.to_csv(file_name, index=False)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False

        return True
