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
