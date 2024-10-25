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
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy.stats import mode

from pyminflux.analysis import calculate_total_distance_traveled, calculate_trace_time
from pyminflux.reader import MinFluxReader


class MinFluxProcessor:
    """Processor of MINFLUX data."""

    __doc__ = """Allows for filtering and selecting data read by the underlying `MinFluxReader`. Please notice that
     `MinFluxProcessor` makes use of `State.min_trace_length` to make sure that at load and after every
      filtering step, short traces are dropped."""

    __slots__ = [
        "state",
        "reader",
        "_current_fluorophore_id",
        "_filtered_stats_dataframe",
        "_min_trace_length",
        "_selected_rows_dict",
        "_stats_to_be_recomputed",
        "_weighted_localizations",
        "_weighted_localizations_to_be_recomputed",
        "_use_weighted_localizations",
    ]

    def __init__(self, reader: MinFluxReader, min_trace_length: int = 1):
        """Constructor.

        Parameters
        ----------

        reader: MinFluxReader
            MinFluxReader object.

        min_trace_length: int (Default = 1)
            Minimum number of localizations for a trace to be kept. Shorter traces are dropped.
        """

        # Store a reference to the MinFluxReader
        self.reader: MinFluxReader = reader

        # Global options
        self._min_trace_length: int = min_trace_length

        # Cache the filtered stats dataframe
        self._filtered_stats_dataframe = None

        # Keep separate arrays of booleans to cache selection state for all fluorophores IDs.
        self._selected_rows_dict = None
        self._init_selected_rows_dict()

        # Keep track of the selected fluorophore
        # 0 - All (default)
        # 1 - Fluorophore 1
        # 2 - Fluorophore 2
        self._current_fluorophore_id = 0

        # Cache the weighted, averaged TID positions
        self._weighted_localizations = None

        # Keep track whether the statistics and the weighted localizations need to be recomputed
        self._stats_to_be_recomputed = False
        self._weighted_localizations_to_be_recomputed = False

        # Whether to use weighted average for localizations
        self._use_weighted_localizations = False

        # Apply the global filters
        self._apply_global_filters()

    def _init_selected_rows_dict(self):
        """Initialize the selected rows array."""
        if self.full_dataframe is None:
            return

        # How many fluorophores do we have?
        self._selected_rows_dict = {
            1: pd.Series(
                data=np.ones(len(self.full_dataframe.index), dtype=bool),
                index=self.full_dataframe.index,
            ),
            2: pd.Series(
                data=np.ones(len(self.full_dataframe.index), dtype=bool),
                index=self.full_dataframe.index,
            ),
        }

    @property
    def is_tracking(self):
        """Minimum number of localizations for the trace to be kept."""
        return self.reader.is_tracking

    @property
    def min_trace_length(self):
        """Minimum number of localizations for the trace to be kept."""
        return self._min_trace_length

    @property
    def z_scaling_factor(self):
        """Returns the scaling factor for the z coordinates from the underlying MinFluxReader."""
        return self.reader.z_scaling_factor

    @min_trace_length.setter
    def min_trace_length(self, value):
        if value < 1 or int(value) != value:
            raise ValueError(
                "MinFluxProcessor.min_trace_length must be a positive integer!"
            )
        self._min_trace_length = value

        # Run the global filters
        self._apply_global_filters()

    @property
    def is_3d(self) -> bool:
        """Return True if the acquisition is 3D.

        Returns
        -------

        is_3d: bool
            True if the acquisition is 3D, False otherwise.
        """
        return self.reader.is_3d

    @property
    def num_values(self) -> int:
        """Return the number of values in the (filtered) dataframe.

        Returns
        -------

        n: int
            Number of values in the dataframe after all filters have been applied.
        """
        if self.filtered_dataframe is not None:
            return len(self.filtered_dataframe.index)

        return 0

    @property
    def current_fluorophore_id(self) -> int:
        """Return current fluorophore ID (0 for all)."""
        return self._current_fluorophore_id

    @current_fluorophore_id.setter
    def current_fluorophore_id(self, fluorophore_id: int) -> None:
        """Set current fluorophore ID (0 for all)."""

        if fluorophore_id not in [0, 1, 2]:
            raise ValueError("Only 1 or 2 are valid fluorophore IDs.")

        # Set the new fluorophore_id
        self._current_fluorophore_id = fluorophore_id

        # Apply the global filters
        self._apply_global_filters()

        # Flag stats to be recomputed
        self._stats_to_be_recomputed = True

    @property
    def num_fluorophores(self) -> int:
        """Return the number of fluorophores."""
        if self.full_dataframe is None:
            return 0
        return len(np.unique(self.full_dataframe["fluo"].to_numpy()))

    @property
    def filtered_numpy_array_all(self):
        """Return the raw NumPy array with applied filters (for all fluorophores)."""

        # Copy the raw NumPy array
        raw_array = self.reader.valid_raw_data
        if raw_array is None:
            return None

        if self.full_dataframe is None or self._selected_rows_dict is None:
            return None

        # Append the fluorophore ID data
        raw_array["fluo"] = self.full_dataframe["fluo"].astype(np.uint8)

        # Extract combination of fluorophore 1 and 2 filtered dataframes
        mask_1 = (self.full_dataframe["fluo"] == 1) & self._selected_rows_dict[1]
        mask_2 = (self.full_dataframe["fluo"] == 2) & self._selected_rows_dict[2]
        return raw_array[mask_1 | mask_2]

    @property
    def filtered_numpy_array(self):
        """Return the raw NumPy array with applied filters for the selected fluorophores."""

        # Copy the raw NumPy array
        full_array = self.filtered_numpy_array_all
        if full_array is None:
            return None

        if self.current_fluorophore_id == 0:
            return full_array
        elif self.current_fluorophore_id == 1:
            return full_array[full_array["fluo"] == 1]
        elif self.current_fluorophore_id == 2:
            return full_array[full_array["fluo"] == 2]
        else:
            raise ValueError(
                f"Unexpected fluorophore ID {self.current_fluorophore_id}."
            )

    @property
    def full_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the full dataframe (with valid entries only), with no selections or filters.

        Returns
        -------

        full_dataframe: Union[None, pd.DataFrame]
            A Pandas dataframe or None if no file was loaded.
        """
        return self.reader.processed_dataframe

    @property
    def filename(self) -> Union[Path, None]:
        """Return the filename if set."""
        if self.reader is None:
            return None
        return self.reader.filename

    def _filtered_dataframe_all(self) -> Union[None, pd.DataFrame]:
        """Return joint dataframe for all fluorophores and with all filters applied.

        Returns
        -------

        filtered_dataframe_all: Union[None, pd.DataFrame]
            A Pandas dataframe or None if no file was loaded.
        """
        if self.full_dataframe is None or self._selected_rows_dict is None:
            return None

        # Extract combination of fluorophore 1 and 2 filtered dataframes
        mask_1 = (self.full_dataframe["fluo"] == 1) & self._selected_rows_dict[1]
        mask_2 = (self.full_dataframe["fluo"] == 2) & self._selected_rows_dict[2]
        return self.full_dataframe.loc[mask_1 | mask_2]

    @property
    def filtered_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return dataframe with all filters applied.

        Returns
        -------

        filtered_dataframe: Union[None, pd.DataFrame]
            A Pandas dataframe or None if no file was loaded.
        """
        if self.full_dataframe is None:
            return None
        if self.current_fluorophore_id == 0:
            return self._filtered_dataframe_all()
        else:
            # Use .loc to filter the dataframe in a single step
            filtered_df = self.full_dataframe.loc[
                self.full_dataframe["fluo"] == self.current_fluorophore_id
            ]
            if self._selected_rows_dict is None:
                return None
            selected_indices = self._selected_rows_dict.get(
                self.current_fluorophore_id, []
            )
            return filtered_df.loc[selected_indices]

    @property
    def filtered_dataframe_stats(self) -> Union[None, pd.DataFrame]:
        """Return dataframe stats with all filters applied.

        Returns
        -------

        filtered_dataframe_stats: Union[None, pd.DataFrame]
            A Pandas dataframe with all data statistics or None if no file was loaded.
        """
        if self._stats_to_be_recomputed:
            self._calculate_statistics()
        return self._filtered_stats_dataframe

    @property
    def weighted_localizations(self) -> Union[None, pd.DataFrame]:
        """Return the average (x, y, z) position per TID weighted by the relative photon count."""
        if self._weighted_localizations_to_be_recomputed:
            self._calculate_weighted_positions()
        return self._weighted_localizations

    @property
    def use_weighted_localizations(self) -> bool:
        """Whether to use weighted average to calculate the mean localization per TID."""
        return self._use_weighted_localizations

    @use_weighted_localizations.setter
    def use_weighted_localizations(self, value: bool):
        """Whether to use weighted average to calculate the mean localization per TID."""
        self._use_weighted_localizations = value
        self._weighted_localizations_to_be_recomputed = True

    @classmethod
    def processed_properties(cls):
        """Return the processed dataframe columns."""
        return MinFluxReader.processed_properties()

    @classmethod
    def trace_stats_properties(cls):
        """Return the columns of the filtered_dataframe_stats."""
        return [
            "tid",
            "n",
            "fluo",
            "mx",
            "my",
            "mz",
            "sx",
            "sy",
            "sxy",
            "exy",
            "rms_xy",
            "sz",
            "ez",
            "mtim",
            "tim_tot",
        ]

    @classmethod
    def trace_stats_with_tracking_properties(cls):
        """Return the columns of the filtered_dataframe_stats with tracking columns."""
        return MinFluxProcessor.trace_stats_properties() + [
            "avg_speed",
            "total_dist",
        ]

    def reset(self):
        """Drops all dynamic filters and resets the data to the processed data frame with global filters."""

        # Clear the selection per fluorophore; they will be reinitialized as
        # all selected at the first access.
        self._init_selected_rows_dict()

        # Reset the mapping to the corresponding fluorophore
        self.full_dataframe["fluo"] = 1

        # Default fluorophore is 0 (no selection)
        self.current_fluorophore_id = 0

        # Apply global filters
        self._apply_global_filters()

    def update_localizations(
        self, x: np.ndarray, y: np.ndarray, z: Optional[np.ndarray] = None
    ):
        """Updates the localization coordinates of current filtered dataframe.

        This can be used for instance after a drift correction.

        Parameters
        ----------

        x: np.ndarray
            Array of x coordinates.

        y: np.ndarray
            Array of y coordinates.

        z: np.ndarray (Optional)
            Optional array of z coordinates. Omit it to skip.
            If the acquisition is 2D, it will be ignored in any case.
        """

        if (
            self.full_dataframe is None
            or self._selected_rows_dict is None
            or self.reader._data_df is None
            or self.reader._valid_entries is None
        ):
            return

        # Make sure to work with NumPy arrays
        x = np.array(x)
        y = np.array(y)
        if z is not None and self.is_3d:
            z = np.array(z)

        # Select the correct rows to update
        if self.current_fluorophore_id == 0:
            mask_1 = (self.full_dataframe["fluo"] == 1) & self._selected_rows_dict[1]
            mask_2 = (self.full_dataframe["fluo"] == 2) & self._selected_rows_dict[2]
            mask = mask_1 | mask_2
        elif self.current_fluorophore_id == 1:
            mask = (self.full_dataframe["fluo"] == 1) & self._selected_rows_dict[1]
        else:
            mask = (self.full_dataframe["fluo"] == 2) & self._selected_rows_dict[2]

        # Make sure that the lengths match
        assert np.sum(mask.to_numpy()) == len(x), "Unexpected number of elements in x."
        assert np.sum(mask.to_numpy()) == len(y), "Unexpected number of elements in y."
        if z is not None and self.is_3d:
            assert np.sum(mask.to_numpy()) == len(
                z
            ), "Unexpected number of elements in z."

        # Re-assign the data at the reader level
        self.reader._data_df.loc[mask, "x"] = x
        self.reader._data_df.loc[mask, "y"] = y
        if z is not None and self.is_3d:
            self.reader._data_df.loc[mask, "z"] = z

        # Also update the raw structured NumPy array. Since NumPy
        # will return a copy if we try to access the "loc" array
        # directly using logical arrays, we need to iterate over
        # all rows one by one!
        #
        # Furthermore, we need to scale the values by the factor
        # self.reader._unit_scaling_factor
        x_scaled = x / self.reader._unit_scaling_factor
        y_scaled = y / self.reader._unit_scaling_factor
        if z is not None and self.is_3d:
            z_scaled = z / self.reader._unit_scaling_factor
        idx = self.reader._loc_index
        vld_indices = np.where(self.reader._valid_entries)[0]
        mask_indices = np.where(mask)[0]
        for i, I in enumerate(mask_indices):
            if I in vld_indices:
                self.reader._data_array[I]["itr"][idx]["loc"][0] = x_scaled[i]
                self.reader._data_array[I]["itr"][idx]["loc"][1] = y_scaled[i]
                if z is not None and self.is_3d:
                    self.reader._data_array[I]["itr"][idx]["loc"][2] = z_scaled[i]

        # Mark derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def set_fluorophore_ids(self, fluorophore_ids: np.ndarray[np.uint8]):
        """Assign the fluorophore IDs to current filtered dataset."""
        if self.filtered_dataframe is None:
            return
        if len(fluorophore_ids) != len(self.filtered_dataframe.index):
            raise ValueError(
                "The number of fluorophore IDs does not match the number of entries in the dataframe."
            )

        # Extract combination of fluorophore 1 and 2 filtered dataframes
        mask_1 = (self.full_dataframe["fluo"] == 1) & self._selected_rows_dict[1]
        mask_2 = (self.full_dataframe["fluo"] == 2) & self._selected_rows_dict[2]
        mask = mask_1 | mask_2
        self.full_dataframe.loc[mask, "fluo"] = fluorophore_ids.astype(np.uint8)
        self.full_dataframe.loc[~mask, "fluo"] = np.uint8(0)

        # Apply global filters
        self._init_selected_rows_dict()
        self._apply_global_filters()

    def set_full_fluorophore_ids(self, fluorophore_ids: np.ndarray[int]):
        """Assign the fluorophore IDs to the original, full dataframe ignoring current filters."""
        if self.full_dataframe is None:
            return
        if len(fluorophore_ids) != len(self.full_dataframe.index):
            raise ValueError(
                "The number of fluorophore IDs does not match the number of entries in the dataframe."
            )
        self.full_dataframe["fluo"] = fluorophore_ids.astype(np.uint8)

        # Apply global filters
        self._init_selected_rows_dict()
        self._apply_global_filters()

    def select_by_rows(
        self, indices: np.ndarray, from_weighted_locs: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Return view on a subset of the filtered dataset or the weighted localisations defined by the passed
        DataFrame row indices.

        The underlying dataframe is not modified.

        Parameters
        ----------

        indices: np.ndarray
            Logical array for selecting the elements to be returned.

        from_weighted_locs: bool
            If True, select from the weighted_localizations dataframe; otherwise, from the filtered_dataframe.

        Returns
        -------

        subset: Union[None, pd.DataFrame]
            A view on a subset of the dataframe defined by the passed indices, or None if no file was loaded.
        """
        if from_weighted_locs:
            if self._weighted_localizations is None:
                return None
            return self._weighted_localizations.iloc[indices]
        else:
            if self.filtered_dataframe is None:
                return None
            return self.filtered_dataframe.iloc[indices]

    def select_by_series_iloc(
        self, iloc: np.ndarray, from_weighted_locs: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Return view on a subset of the filtered dataset or the weighted localisations defined by the passed
        DataFrame index locations.

        The underlying dataframe is not modified.

        Parameters
        ----------

        iloc: np.ndarray
            Array of Series index locations for selecting rows.

        from_weighted_locs: bool
            If True, select from the weighted_localizations dataframe; otherwise, from the filtered_dataframe.

        Returns
        -------

        subset: Union[None, pd.DataFrame]
            A view on a subset of the dataframe defined by the passed indices, or None if no file was loaded.
        """
        if from_weighted_locs:
            if self._weighted_localizations is None:
                return None
            return self._weighted_localizations.loc[iloc]
        else:
            if self.filtered_dataframe is None:
                return None
            return self.filtered_dataframe.loc[iloc]

    def select_by_1d_range(
        self, x_prop, x_range, from_weighted_locs: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Return a view on a subset of the filtered dataset or the weighted localisations defined by the passed
        parameter and corresponding range.

        The underlying dataframe is not modified.

        Parameters
        ----------

        x_prop: str
            Property to be filtered by corresponding x_range.

        x_range: tuple
            Tuple containing the minimum and maximum values for the selected property.

        from_weighted_locs: bool
            If True, select from the weighted_localizations dataframe; otherwise, from the filtered_dataframe.

        Returns
        -------

        subset: Union[None, pd.DataFrame]
            A view on a subset of the dataframe defined by the passed property and range, or None if no file was loaded.
        """

        # Make sure that the range is increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        if from_weighted_locs:
            if self._weighted_localizations is None:
                return None
            return self._weighted_localizations.loc[
                (self._weighted_localizations[x_prop] >= x_min)
                & (self._weighted_localizations[x_prop] < x_max)
            ]
        else:
            # Work with currently selected rows
            if self.filtered_dataframe is None:
                return None
            df = self.filtered_dataframe
            return df.loc[(df[x_prop] >= x_min) & (df[x_prop] < x_max)]

    def select_by_2d_range(
        self, x_prop, y_prop, x_range, y_range, from_weighted_locs: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Return a view on a subset of the filtered dataset or the weighted localisations defined by the passed
        parameters and corresponding ranges.

        The underlying dataframe is not modified.

        Parameters
        ----------

        x_prop: str
            First property to be filtered by corresponding x_range.

        y_prop: str
            Second property to be filtered by corresponding y_range.

        x_range: tuple
            Tuple containing the minimum and maximum values for the first property.

        y_range: tuple
            Tuple containing the minimum and maximum values for the second property.

        from_weighted_locs: bool
            If True, select from the weighted_localizations dataframe; otherwise, from the filtered_dataframe.

        Returns
        -------

        subset: Union[None, pd.DataFrame]
            A view on a subset of the dataframe defined by the passed properties and ranges, or None if no file
            was loaded.
        """

        # Make sure that the ranges are increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        y_min = y_range[0]
        y_max = y_range[1]
        if y_max < y_min:
            y_max, y_min = y_min, y_max

        if from_weighted_locs:
            if self._weighted_localizations is None:
                return None
            return self._weighted_localizations.loc[
                (self._weighted_localizations[x_prop] >= x_min)
                & (self._weighted_localizations[x_prop] < x_max)
                & (self._weighted_localizations[y_prop] >= y_min)
                & (self._weighted_localizations[y_prop] < y_max)
            ]
        else:
            # Work with currently selected rows
            if self.filtered_dataframe is None:
                return None
            df = self.filtered_dataframe
            return df.loc[
                (df[x_prop] >= x_min)
                & (df[x_prop] < x_max)
                & (df[y_prop] >= y_min)
                & (df[y_prop] < y_max)
            ]

    def filter_by_2d_range(self, x_prop, y_prop, x_range, y_range):
        """Filter dataset by the extracting a rectangular ROI over two parameters and two ranges.

        Parameters
        ----------

        x_prop: str
            First property to be filtered by corresponding x_range.

        y_prop: str
            Second property to be filtered by corresponding y_range.

        x_range: tuple
            Tuple containing the minimum and maximum values for the first property.

        y_range: tuple
            Tuple containing the minimum and maximum values for the second property.
        """

        # Make sure that the ranges are increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        y_min = y_range[0]
        y_max = y_range[1]
        if y_max < y_min:
            y_max, y_min = y_min, y_max

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            self._selected_rows_dict[1] = (
                self._selected_rows_dict[1]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
                & (self.filtered_dataframe[y_prop] >= y_min)
                & (self.filtered_dataframe[y_prop] < y_max)
            )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self._selected_rows_dict[2] = (
                self._selected_rows_dict[2]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
                & (self.filtered_dataframe[y_prop] >= y_min)
                & (self.filtered_dataframe[y_prop] < y_max)
            )

        # Make sure to always apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def _apply_global_filters(self):
        """Apply filters that are defined in the global application configuration."""

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            self._selected_rows_dict[1] = self._filter_by_tid_length(1)

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self._selected_rows_dict[2] = self._filter_by_tid_length(2)

        # Make sure to flag the derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def _filter_by_tid_length(self, index):
        # Make sure to count only currently selected rows
        df = self.full_dataframe.copy()
        df.loc[np.invert(self._selected_rows_dict[index]), "tid"] = np.nan

        # Select all rows where the count of TIDs is larger than self._min_trace_num
        counts = df["tid"].value_counts(normalize=False)
        return df["tid"].isin(counts[counts >= self.min_trace_length].index)

    def filter_by_single_threshold(
        self, prop: str, threshold: Union[int, float], larger_than: bool = True
    ):
        """Apply single threshold to filter values either lower or higher (equal) than threshold for given property."""

        # Apply filter
        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            if larger_than:
                self._selected_rows_dict[1] = self._selected_rows_dict[1] & (
                    self.filtered_dataframe[prop] >= threshold
                )
            else:
                self._selected_rows_dict[1] = self._selected_rows_dict[1] & (
                    self.filtered_dataframe[prop] < threshold
                )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            if larger_than:
                self._selected_rows_dict[2] = self._selected_rows_dict[2] & (
                    self.filtered_dataframe[prop] >= threshold
                )
            else:
                self._selected_rows_dict[2] = self._selected_rows_dict[2] & (
                    self.filtered_dataframe[prop] < threshold
                )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def filter_by_1d_range(self, x_prop: str, x_range: tuple):
        """Apply min and max thresholding to the given property.

        Parameters
        ----------

        x_prop: str
            Name of the property (dataframe column) to filter.

        x_range: tuple
            Tuple containing the minimum and maximum values for the selected property.
        """

        # Make sure that the ranges are increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        # Apply filter
        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            self._selected_rows_dict[1] = (
                self._selected_rows_dict[1]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
            )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self._selected_rows_dict[2] = (
                self._selected_rows_dict[2]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
            )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def filter_by_1d_range_complement(self, prop: str, x_range: tuple):
        """Apply min and max thresholding to the given property but keep the
        data outside the range (i.e., crop the selected range).

        Parameters
        ----------

        prop: str
            Name of the property (dataframe column) to filter.

        x_range: tuple
            Tuple containing the minimum and maximum values for cropping the selected property.
        """

        # Make sure that the ranges are increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        # Apply filter
        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            self._selected_rows_dict[1] = self._selected_rows_dict[1] & (
                (self.filtered_dataframe[prop] < x_min)
                | (self.filtered_dataframe[prop] >= x_max)
            )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self._selected_rows_dict[2] = self._selected_rows_dict[2] & (
                (self.filtered_dataframe[prop] < x_min)
                | (self.filtered_dataframe[prop] >= x_max)
            )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def filter_by_1d_stats(self, x_prop_stats: str, x_range: tuple):
        """Filter TIDs by min and max thresholding using the given property from the stats dataframe.

        Parameters
        ----------

        x_prop_stats: str
            Name of the property (column) from the stats dataframe used to filter.

        x_range: tuple
            Tuple containing the minimum and maximum values for the selected property.
        """

        # Make sure the property exists in the stats dataframe
        if x_prop_stats not in self.filtered_dataframe_stats.columns:
            raise ValueError(
                f"The property {x_prop_stats} does not exist in `filtered_dataframe_stats`."
            )

        # Make sure that the ranges are increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        # Find all TIDs for current fluorophore ID by which the requested stats property is inside the range
        tids_to_keep = self.filtered_dataframe_stats[
            (
                (self.filtered_dataframe_stats[x_prop_stats] >= x_min)
                & (self.filtered_dataframe_stats[x_prop_stats] <= x_max)
            )
        ]["tid"].to_numpy()

        # Rows of the filtered dataframe to keep
        rows_to_keep = self.filtered_dataframe["tid"].isin(tids_to_keep)

        # Apply filter
        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            self._selected_rows_dict[1] = self._selected_rows_dict[1] & rows_to_keep

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self._selected_rows_dict[2] = self._selected_rows_dict[2] & rows_to_keep

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self._stats_to_be_recomputed = True
        self._weighted_localizations_to_be_recomputed = True

    def _calculate_statistics(self):
        """Calculate per-trace statistics."""

        # Make sure we have processed dataframe to work on
        if self.full_dataframe is None:
            return

        # Only recompute statistics if needed
        if not self._stats_to_be_recomputed:
            return

        # Work with currently selected rows
        df = self.filtered_dataframe

        # Calculate the statistics
        df_tid = self.calculate_statistics_on(df, self.reader.is_tracking)

        # Store the results
        self._filtered_stats_dataframe = df_tid

        # Flag the statistics to be computed
        self._stats_to_be_recomputed = False

    @staticmethod
    def calculate_statistics_on(
        df: pd.DataFrame, is_tracking: bool = False
    ) -> pd.DataFrame:
        """Calculate per-trace statistics for the selected dataframe.

        Parameters
        ----------

        df: pd.DataFrame
            DataFrame (view) generated by one of the `select_by_*` methods.

        is_tracking: bool
            Whether the data comes from a tracking instead of a localization experiment.

        Returns
        -------
        df_stats: pd.DataFrame
            Per-trace statistics calculated on the passed DataFrame selection (view).
        """

        # Prepare a dataframe with the statistics
        if is_tracking:
            df_tid = pd.DataFrame(
                columns=MinFluxProcessor.trace_stats_with_tracking_properties()
            )
        else:
            df_tid = pd.DataFrame(columns=MinFluxProcessor.trace_stats_properties())

        # Calculate some statistics per TID on the passed dataframe
        df_grouped = df.groupby("tid")

        # Base statistics
        tid = df_grouped["tid"].first().to_numpy()
        n = df_grouped["tid"].count().to_numpy()
        mx = df_grouped["x"].mean().to_numpy()
        my = df_grouped["y"].mean().to_numpy()
        mz = df_grouped["z"].mean().to_numpy()
        sx = df_grouped["x"].std().to_numpy()
        sy = df_grouped["y"].std().to_numpy()
        sz = df_grouped["z"].std().to_numpy()
        tmp = np.power(sx, 2) + np.power(sy, 2)
        sxy = np.sqrt(tmp)
        rms_xy = np.sqrt(tmp / 2)
        exy = sxy / np.sqrt(n)
        ez = sz / np.sqrt(n)
        fluo = df_grouped["fluo"].agg(lambda x: mode(x, keepdims=True)[0][0]).to_numpy()
        mtim = df_grouped["tim"].mean().to_numpy()
        tot_tim, _, _ = calculate_trace_time(df)

        # Optional tracking statistics
        if is_tracking:
            total_distance, _, _ = calculate_total_distance_traveled(df)
            speeds = (
                total_distance["displacement"].to_numpy()
                / tot_tim["tim_tot"].to_numpy()
            )

        # Store trace stats
        df_tid["tid"] = tid  # Trace ID
        df_tid["n"] = n  # Number of localizations for given trace ID
        df_tid["mx"] = mx  # x mean localization
        df_tid["my"] = my  # y mean localization
        df_tid["mz"] = mz  # z mean localization
        df_tid["sx"] = sx  # x localization precision
        df_tid["sy"] = sy  # y localization precision
        df_tid["sxy"] = sxy  # Lateral (x, y) localization precision
        df_tid["rms_xy"] = rms_xy  # Lateral root mean square
        df_tid["exy"] = exy  # Standard error of sxy
        df_tid["sz"] = sz  # z localization precision
        df_tid["ez"] = ez  # Standard error of ez
        df_tid["fluo"] = fluo  # Assigned fluorophore ID
        df_tid["mtim"] = mtim  # Average time per trace
        df_tid["tim_tot"] = tot_tim["tim_tot"].to_numpy()  # Total time per trace
        if is_tracking:
            df_tid["avg_speed"] = speeds  # Average speed per trace
            df_tid["total_dist"] = total_distance[
                "displacement"
            ].to_numpy()  # Total travelled distance per trace

        # ["sx", "sy", "sxy", "rms_xy", "exy", "sz", "ez"] columns will contain
        # np.nan if n == 1: we replace them with 0.0.
        # @TODO: should this be changed? It could be a global option.
        df_tid[["sx", "sy", "sxy", "rms_xy", "exy", "sz", "ez"]] = df_tid[
            ["sx", "sy", "sxy", "rms_xy", "exy", "sz", "ez"]
        ].fillna(value=0.0)

        # Return the results
        return df_tid

    def _calculate_weighted_positions(self):
        """Calculate per-trace localization weighted by relative photon count."""

        if self.filtered_dataframe is None:
            return

        if not self._weighted_localizations_to_be_recomputed:
            return

        # Work with a copy of a subset of current filtered dataframe
        df = self.filtered_dataframe[
            ["tid", "tim", "eco", "x", "y", "z", "fluo"]
        ].copy()

        if self._use_weighted_localizations:
            # Calculate weights for each coordinate based on 'eco'
            total_eco_per_tid = df.groupby("tid")["eco"].transform("sum")
            eco_rel = df["eco"] / total_eco_per_tid

            # Calculate weighted positions
            df.loc[:, "x_rel"] = df["x"] * eco_rel
            df.loc[:, "y_rel"] = df["y"] * eco_rel
            df.loc[:, "z_rel"] = df["z"] * eco_rel

            # Summing up the relative contributions
            df_grouped = df.groupby("tid")
            x_w = df_grouped["x_rel"].sum()
            y_w = df_grouped["y_rel"].sum()
            z_w = df_grouped["z_rel"].sum()

            # Return the most frequent fluo ID: traces should be homogeneous with respect
            # to their fluorophore assignment, but we search anyway for safety.
            fluo_mode = df_grouped["fluo"].agg(
                lambda x: x.mode()[0] if not x.empty else np.nan
            )

        else:
            # Calculate simple average of localizations by TID
            df_grouped = df.groupby("tid")
            x_w = df_grouped["x"].mean()
            y_w = df_grouped["y"].mean()
            z_w = df_grouped["z"].mean()

            # Return the most frequent fluo ID: traces should be homogeneous with respect
            # to their fluorophore assignment, but we search anyway for safety.
            fluo_mode = df_grouped["fluo"].agg(
                lambda x: x.mode()[0] if not x.empty else np.nan
            )

        # We calculate also the mean timestamp (not weighted)
        tim = df_grouped["tim"].mean()

        # Prepare a dataframe with the weighted localizations
        df_loc = pd.DataFrame(
            {
                "tid": x_w.index,
                "tim": tim.to_numpy(),
                "x": x_w.to_numpy(),
                "y": y_w.to_numpy(),
                "z": z_w.to_numpy(),
                "fluo": fluo_mode.to_numpy(),
            }
        )

        # Update the weighted localization dataframe
        self._weighted_localizations = df_loc

        # Flag the results as up-to-date
        self._weighted_localizations_to_be_recomputed = False
