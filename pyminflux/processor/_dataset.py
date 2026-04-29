#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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

"""Dataset container for MINFLUX data."""

from pathlib import Path
from typing import Optional, Union, List, Tuple

import pandas as pd
import numpy as np


class MinFluxDataset:
    """Container for MINFLUX data that can be processed by MinFluxProcessor.
    
    This class serves as a data container that holds the processed dataframe
    and associated metadata. It can be created from a MinFluxReader or by
    combining multiple datasets.
    """
    
    __slots__ = [
        "_processed_dataframe",
        "_full_raw_dataframe",
        "_valid_raw_data_array",
        "_filename",
        "_is_3d",
        "_is_tracking",
        "_is_aggregated",
        "_z_scaling_factor",
        "_unit_scaling_factor",
        "_dwell_time",
        "_pool_dcr",
        "_version",
        "_mbm_data",
        "_tid_offsets",
    ]
    
    def __init__(
        self,
        processed_dataframe: pd.DataFrame,
        full_raw_dataframe: Optional[pd.DataFrame] = None,
        valid_raw_data_array: Optional[np.ndarray] = None,
        filename: Optional[Union[Path, str]] = None,
        is_3d: bool = False,
        is_tracking: bool = False,
        is_aggregated: bool = False,
        z_scaling_factor: float = 1.0,
        unit_scaling_factor: float = 1e9,
        dwell_time: float = 1.0,
        pool_dcr: bool = False,
        version: int = 2,
        mbm_data: Optional[dict] = None,
        tid_offsets: Optional[List[Tuple[int, int]]] = None,
    ):
        """Constructor.
        
        Parameters
        ----------
        processed_dataframe: pd.DataFrame
            The processed dataframe with MINFLUX data.
        full_raw_dataframe: Optional[pd.DataFrame]
            The full raw dataframe (for version 2 readers), or None.
        valid_raw_data_array: Optional[np.ndarray]
            The valid raw data array (for version 1 readers), or None.
        filename: Optional[Union[Path, str]]
            Original filename, if applicable.
        is_3d: bool
            Whether the acquisition is 3D.
        is_tracking: bool
            Whether the dataset is from a tracking experiment.
        is_aggregated: bool
            Whether the dataset contains aggregated measurements.
        z_scaling_factor: float
            Refractive index mismatch correction factor for z coordinates.
        unit_scaling_factor: float
            Unit scaling factor to convert raw coordinates to nm.
        dwell_time: float
            Dwell time in milliseconds.
        pool_dcr: bool
            Whether to pool DCR values.
        version: int
            Reader version (1 or 2).
        mbm_data: Optional[dict]
            Beamline monitoring (bead) data, if available.
        tid_offsets: Optional[List[Tuple[int, int]]]
            List of (first_iid, tid_offset) pairs applied when combining datasets.
        """
        self._processed_dataframe = processed_dataframe
        self._full_raw_dataframe = full_raw_dataframe
        self._valid_raw_data_array = valid_raw_data_array
        self._filename = Path(filename) if filename else None
        self._is_3d = is_3d
        self._is_tracking = is_tracking
        self._is_aggregated = is_aggregated
        self._z_scaling_factor = z_scaling_factor
        self._unit_scaling_factor = unit_scaling_factor
        self._dwell_time = dwell_time
        self._pool_dcr = pool_dcr
        self._version = version
        self._mbm_data = mbm_data
        self._tid_offsets = list(tid_offsets) if tid_offsets else []
    
    @classmethod
    def from_reader(cls, reader):
        """Create a MinFluxDataset from a MinFluxReader or MinFluxReaderV2.
        
        Parameters
        ----------
        reader: Union[MinFluxReader, MinFluxReaderV2]
            The reader instance to extract data from.
            
        Returns
        -------
        dataset: MinFluxDataset
            A new dataset instance.
        """
        # Get the full raw dataframe if it exists (version 2)
        full_raw_dataframe = getattr(reader, "_full_raw_dataframe", None)
        mbm_data = getattr(reader, "_mbm_data", None)
        valid_raw_data_array = None
        if hasattr(reader, "valid_raw_data_array"):
            try:
                valid_raw_data_array = reader.valid_raw_data_array
            except Exception:
                valid_raw_data_array = None
        
        return cls(
            processed_dataframe=reader.processed_dataframe.copy(),
            full_raw_dataframe=full_raw_dataframe.copy() if full_raw_dataframe is not None else None,
            valid_raw_data_array=valid_raw_data_array.copy() if valid_raw_data_array is not None else None,
            filename=getattr(reader, "filename", None),
            is_3d=getattr(reader, "is_3d", False),
            is_tracking=getattr(reader, "is_tracking", False),
            is_aggregated=getattr(reader, "is_aggregated", False),
            z_scaling_factor=getattr(reader, "z_scaling_factor", 1.0),
            unit_scaling_factor=getattr(reader, "_unit_scaling_factor", 1e9),
            dwell_time=getattr(reader, "dwell_time", 1.0),
            pool_dcr=getattr(reader, "is_pool_dcr", False),
            version=getattr(reader, "version", 2),
            mbm_data=mbm_data,
            tid_offsets=getattr(reader, "tid_offsets", None),
        )
    
    @property
    def processed_dataframe(self) -> pd.DataFrame:
        """Return the processed dataframe."""
        return self._processed_dataframe
    
    @processed_dataframe.setter
    def processed_dataframe(self, value: pd.DataFrame):
        """Set the processed dataframe."""
        self._processed_dataframe = value
    
    @property
    def full_raw_dataframe(self) -> Optional[pd.DataFrame]:
        """Return the full raw dataframe (version 2 only)."""
        return self._full_raw_dataframe
    
    @full_raw_dataframe.setter
    def full_raw_dataframe(self, value: Optional[pd.DataFrame]):
        """Set the full raw dataframe."""
        self._full_raw_dataframe = value
    
    @property
    def filename(self) -> Optional[Path]:
        """Return the filename."""
        return self._filename
    
    @property
    def is_3d(self) -> bool:
        """Return True if the acquisition is 3D."""
        return self._is_3d
    
    @property
    def is_tracking(self) -> bool:
        """Return True if the dataset is from a tracking experiment."""
        return self._is_tracking
    
    @property
    def is_aggregated(self) -> bool:
        """Return True if the dataset contains aggregated measurements."""
        return self._is_aggregated
    
    @property
    def z_scaling_factor(self) -> float:
        """Return the z scaling factor."""
        return self._z_scaling_factor

    @property
    def unit_scaling_factor(self) -> float:
        """Return the unit scaling factor for raw coordinates."""
        return self._unit_scaling_factor
    
    @property
    def dwell_time(self) -> float:
        """Return the dwell time."""
        return self._dwell_time
    
    @property
    def is_pool_dcr(self) -> bool:
        """Return True if DCR values are pooled."""
        return self._pool_dcr
    
    @property
    def version(self) -> int:
        """Return the reader version."""
        return self._version
    
    @property
    def mbm_data(self) -> Optional[dict]:
        """Return the beamline monitoring data."""
        return self._mbm_data

    @property
    def tid_offsets(self) -> List[Tuple[int, int]]:
        """Return list of (first_iid, tid_offset) pairs applied when combining datasets."""
        return list(self._tid_offsets)
    
    @property
    def valid_full_raw_dataframe(self) -> Optional[pd.DataFrame]:
        """Return the valid raw dataframe (for compatibility with version 2 readers)."""
        if self._full_raw_dataframe is None:
            return None
        # Assume all entries in the dataset are valid
        return self._full_raw_dataframe.copy()
    
    @property
    def valid_raw_data_array(self):
        """Return the valid raw data array (for compatibility with version 1 readers).
        
        Note: Version 1 functionality is not fully supported in datasets.
        This property exists for backwards compatibility but will return None
        for datasets created from version 2 readers.
        """
        if self._valid_raw_data_array is None:
            return None
        return self._valid_raw_data_array.copy()
    
    def copy(self):
        """Create a deep copy of the dataset."""
        return MinFluxDataset(
            processed_dataframe=self._processed_dataframe.copy(),
            full_raw_dataframe=self._full_raw_dataframe.copy() if self._full_raw_dataframe is not None else None,
            valid_raw_data_array=self._valid_raw_data_array.copy() if self._valid_raw_data_array is not None else None,
            filename=self._filename,
            is_3d=self._is_3d,
            is_tracking=self._is_tracking,
            is_aggregated=self._is_aggregated,
            z_scaling_factor=self._z_scaling_factor,
            unit_scaling_factor=self._unit_scaling_factor,
            dwell_time=self._dwell_time,
            pool_dcr=self._pool_dcr,
            version=self._version,
            mbm_data=self._mbm_data,
            tid_offsets=self._tid_offsets.copy(),
        )
