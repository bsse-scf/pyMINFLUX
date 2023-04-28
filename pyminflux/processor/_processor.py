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

from typing import Union

import numpy as np
import pandas as pd
from scipy.stats import mode

from pyminflux.reader import MinFluxReader
from pyminflux.state import State


class MinFluxProcessor:
    """Processor of MINFLUX data."""

    __slots__ = [
        "state",
        "__minfluxreader",
        "__current_fluorophore_id",
        "__filtered_stats_dataframe",
        "__fluorophore_ids",
        "__selected_rows_dict",
        "__stats_to_be_recomputed",
        "__weighted_localizations",
        "__weighted_localizations_to_be_recomputed",
        "__use_weighted_localizations",
    ]

    def __init__(self, minfluxreader: MinFluxReader):
        """Constructor.

        Parameters
        ----------

        minfluxreader: pyminflux.reader.MinFluxReader
            MinFluxReader object.
        """

        # Store a reference to the MinFluxReader
        self.__minfluxreader = minfluxreader

        # Keep a reference to the state machine
        self.state = State()

        # Cache the filtered stats dataframe
        self.__filtered_stats_dataframe = None

        # Keep separate arrays of booleans to cache selection state for all fluorophores IDs.
        self.__selected_rows_dict = None
        self.__init_selected_rows_dict()

        # Keep track of the selected fluorophore
        # 0 - All (default)
        # 1 - Fluorophore 1
        # 2 - Fluorophore 2
        self.__current_fluorophore_id = 0

        # Cache the weighted, averaged TID positions
        self.__weighted_localizations = None

        # Keep track whether the statistics and the weighted localizations need to be recomputed
        self.__stats_to_be_recomputed = False
        self.__weighted_localizations_to_be_recomputed = False

        # Whether to use weighted average for localizations
        self.__use_weighted_localizations = False

        # Apply the global filters
        self._apply_global_filters()

    def __init_selected_rows_dict(self):
        """Initialize the selected rows array."""
        # How many fluorophores do we have?
        self.__selected_rows_dict = {
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
    def is_3d(self) -> bool:
        """Return True if the acquisition is 3D.

        Returns
        -------

        is_3d: bool
            True if the acquisition is 3D, False otherwise.
        """
        return self.__minfluxreader.is_3d

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
        return self.__current_fluorophore_id

    @current_fluorophore_id.setter
    def current_fluorophore_id(self, fluorophore_id: int) -> None:
        """Set current fluorophore ID (0 for all)."""

        if fluorophore_id not in [0, 1, 2]:
            raise ValueError(f"Only 1 or 2 are valid fluorophore IDs.")

        # Set the new fluorophore_id
        self.__current_fluorophore_id = fluorophore_id

        # Apply the global filters
        self._apply_global_filters()

        # Flag stats to be recomputed
        self.__stats_to_be_recomputed = True

    @property
    def num_fluorophorses(self) -> int:
        """Return the number of fluorophores."""
        return len(np.unique(self.full_dataframe["fluo"].values))

    @property
    def filtered_numpy_array(self):
        """Return the raw NumPy array."""

        # Copy the raw NumPy array
        raw_array = self.__minfluxreader.valid_raw_data
        if raw_array is None:
            return None

        # Extract combination of fluorophore 1 and 2 filtered dataframes
        mask_1 = (self.full_dataframe["fluo"] == 1) & self.__selected_rows_dict[1]
        mask_2 = (self.full_dataframe["fluo"] == 2) & self.__selected_rows_dict[2]
        return raw_array[mask_1 | mask_2]

    @property
    def full_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return the full dataframe (with valid entries only), with no selections or filters.

        Returns
        -------

        full_dataframe: Union[None, pd.DataFrame]
            A Pandas dataframe or None if no file was loaded.
        """
        return self.__minfluxreader.processed_dataframe

    def _filtered_dataframe_all(self) -> Union[None, pd.DataFrame]:
        """Return joint dataframe for all fluorophores and with all filters applied.

        Returns
        -------

        filtered_dataframe_all: Union[None, pd.DataFrame]
            A Pandas dataframe or None if no file was loaded.
        """
        if self.full_dataframe is None:
            return None

        # Extract combination of fluorophore 1 and 2 filtered dataframes
        mask_1 = (self.full_dataframe["fluo"] == 1) & self.__selected_rows_dict[1]
        mask_2 = (self.full_dataframe["fluo"] == 2) & self.__selected_rows_dict[2]
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
            df = self.full_dataframe.loc[
                self.full_dataframe["fluo"] == self.current_fluorophore_id
            ]
            return df.loc[self.__selected_rows_dict[self.current_fluorophore_id]]

    @property
    def filtered_dataframe_stats(self) -> Union[None, pd.DataFrame]:
        """Return dataframe stats with all filters applied.

        Returns
        -------

        filtered_dataframe_stats: Union[None, pd.DataFrame]
            A Pandas dataframe with all data statistics or None if no file was loaded.
        """
        if self.__stats_to_be_recomputed:
            self._calculate_statistics()
        return self.__filtered_stats_dataframe

    @property
    def weighted_localizations(self) -> Union[None, pd.DataFrame]:
        """Return the average (x, y, z) position per TID weighted by the relative photon count."""
        if self.__weighted_localizations_to_be_recomputed:
            self._calculate_weighted_positions()
        return self.__weighted_localizations

    @property
    def use_weighted_localizations(self) -> bool:
        """Whether to use weighted average to calculate the mean localization per TID."""
        return self.__use_weighted_localizations

    @use_weighted_localizations.setter
    def use_weighted_localizations(self, value: bool):
        """Whether to use weighted average to calculate the mean localization per TID."""
        self.__use_weighted_localizations = value
        self.__weighted_localizations_to_be_recomputed = True

    @classmethod
    def processed_properties(cls):
        """Return the processed dataframe columns."""
        return MinFluxReader.processed_properties()

    def reset(self):
        """Drops all dynamic filters and resets the data to the processed data frame with global filters."""

        # Clear the selection per fluorophore; they will be reinitialized as
        # all selected at the first access.
        self.__init_selected_rows_dict()

        # Reset the mapping to the corresponding fluorophore
        self.full_dataframe["fluo"] = 1

        # Default fluorophore is 0 (no selection)
        self.current_fluorophore_id = 0

        # Apply global filters
        self._apply_global_filters()

    def set_fluorophore_ids(self, fluorophore_ids: np.ndarray[int]):
        """Assign the fluorophore IDs."""
        if len(fluorophore_ids) != len(self.full_dataframe.index):
            raise ValueError(
                "The number of fluorophore IDs does not match the number of entries in the dataframe."
            )
        self.full_dataframe["fluo"] = fluorophore_ids
        self.__init_selected_rows_dict()
        self._apply_global_filters()

    def select_by_indices(
        self, indices, from_weighted_locs: bool = False
    ) -> Union[None, pd.DataFrame]:
        """Return view on a subset of the filtered dataset or the weighted localisations defined by the passed indices.

        The underlying dataframe is not modified.

        Parameters
        ----------

        indices: array
            Logical array for selecting the elements to be returned.

        from_weighted_locs: bool
            If True, select from the weighted_localizations dataframe; otherwise, from the filtered_dataframe.

        Returns
        -------

        subset: Union[None, pd.DataFrame]
            A view on a subset of the dataframe defined by the passed indices, or None if no file was loaded.
        """
        if from_weighted_locs:
            if self.__weighted_localizations is None:
                return None
            return self.__weighted_localizations.iloc[indices]
        else:
            if self.filtered_dataframe is None:
                return None
            return self.filtered_dataframe.iloc[indices]

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
            return self.__weighted_localizations.loc[
                (self.__weighted_localizations[x_prop] >= x_min)
                & (self.__weighted_localizations[x_prop] < x_max)
            ]
        else:
            # Work with currently selected rows
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
            return self.__weighted_localizations.loc[
                (self.__weighted_localizations[x_prop] >= x_min)
                & (self.__weighted_localizations[x_prop] < x_max)
                & (self.__weighted_localizations[y_prop] >= y_min)
                & (self.__weighted_localizations[y_prop] < y_max)
            ]
        else:
            # Work with currently selected rows
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
            self.__selected_rows_dict[1] = (
                self.__selected_rows_dict[1]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
                & (self.filtered_dataframe[y_prop] >= y_min)
                & (self.filtered_dataframe[y_prop] < y_max)
            )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self.__selected_rows_dict[2] = (
                self.__selected_rows_dict[2]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
                & (self.filtered_dataframe[y_prop] >= y_min)
                & (self.filtered_dataframe[y_prop] < y_max)
            )

        # Make sure to always apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def _apply_global_filters(self):
        """Apply filters that are defined in the global application configuration."""

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            self.__selected_rows_dict[1] = self.__filter_by_tid_length(1)

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self.__selected_rows_dict[2] = self.__filter_by_tid_length(2)

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def __filter_by_tid_length(self, index):
        # Make sure to count only currently selected rows
        df = self.full_dataframe.copy()
        df.loc[np.invert(self.__selected_rows_dict[index]), "tid"] = np.nan

        # Select all rows where the count of TIDs is larger than self._min_trace_num
        counts = df["tid"].value_counts(normalize=False)
        return df["tid"].isin(counts[counts >= self.state.min_num_loc_per_trace].index)

    def filter_by_single_threshold(
        self, prop: str, threshold: Union[int, float], larger_than: bool = True
    ):
        """Apply single threshold to filter values either lower or higher (equal) than threshold for given property."""

        # Apply filter
        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 1:
            if larger_than:
                self.__selected_rows_dict[1] = self.__selected_rows_dict[1] & (
                    self.filtered_dataframe[prop] >= threshold
                )
            else:
                self.__selected_rows_dict[1] = self.__selected_rows_dict[1] & (
                    self.filtered_dataframe[prop] < threshold
                )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            if larger_than:
                self.__selected_rows_dict[2] = self.__selected_rows_dict[2] & (
                    self.filtered_dataframe[prop] >= threshold
                )
            else:
                self.__selected_rows_dict[2] = self.__selected_rows_dict[2] & (
                    self.filtered_dataframe[prop] < threshold
                )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

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
            self.__selected_rows_dict[1] = (
                self.__selected_rows_dict[1]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
            )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self.__selected_rows_dict[2] = (
                self.__selected_rows_dict[2]
                & (self.filtered_dataframe[x_prop] >= x_min)
                & (self.filtered_dataframe[x_prop] < x_max)
            )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

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
            self.__selected_rows_dict[1] = self.__selected_rows_dict[1] & (
                (self.filtered_dataframe[prop] < x_min)
                | (self.filtered_dataframe[prop] >= x_max)
            )

        if self.current_fluorophore_id == 0 or self.current_fluorophore_id == 2:
            self.__selected_rows_dict[2] = self.__selected_rows_dict[2] & (
                (self.filtered_dataframe[prop] < x_min)
                | (self.filtered_dataframe[prop] >= x_max)
            )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def _calculate_statistics(self):
        """Calculate per-trace statistics."""

        # Make sure we have processed dataframe to work on
        if self.full_dataframe is None:
            return

        # Only recompute statistics if needed
        if not self.__stats_to_be_recomputed:
            return

        # Work with currently selected rows
        df = self.filtered_dataframe

        # Calculate some statistics per TID on the processed dataframe
        df_grouped = df.groupby("tid")

        tid = df_grouped["tid"].first().values
        n = df_grouped["tid"].count().values
        mx = df_grouped["x"].mean().values
        my = df_grouped["y"].mean().values
        mz = df_grouped["z"].mean().values
        sx = df_grouped["x"].std().values
        sy = df_grouped["y"].std().values
        sz = df_grouped["z"].std().values
        fluo = df_grouped["fluo"].agg(lambda x: mode(x, keepdims=True)[0][0]).values

        # Prepare a dataframe with the statistics
        df_tid = pd.DataFrame(
            columns=["tid", "n", "mx", "my", "mz", "sx", "sy", "sz", "fluo"]
        )

        df_tid["tid"] = tid
        df_tid["n"] = n
        df_tid["mx"] = mx
        df_tid["my"] = my
        df_tid["mz"] = mz
        df_tid["sx"] = sx
        df_tid["sy"] = sy
        df_tid["sz"] = sz
        df_tid["fluo"] = fluo

        # sx, sy sz columns will contain np.nan if n == 1: we replace with 0.0
        df_tid[["sx", "sy", "sz"]] = df_tid[["sx", "sy", "sz"]].fillna(value=0.0)

        # Store the results
        self.__filtered_stats_dataframe = df_tid

        # Flag the statistics to be computed
        self.__stats_to_be_recomputed = False

    @staticmethod
    def calculate_statistics_on(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate per-trace statistics for the selected dataframe.

        Parameters
        ----------

        df: pd.DataFrame
            DataFrame (view) generated by one of the `select_by_*` methods.

        Returns
        -------
        df_stats: pd.DataFrame
            Per-trace statistics calculated on the passed DataFrame selection (view).
        """

        # Calculate some statistics per TID on the passed dataframe
        df_grouped = df.groupby("tid")

        tid = df_grouped["tid"].first().values
        n = df_grouped["tid"].count().values
        mx = df_grouped["x"].mean().values
        my = df_grouped["y"].mean().values
        mz = df_grouped["z"].mean().values
        sx = df_grouped["x"].std().values
        sy = df_grouped["y"].std().values
        sz = df_grouped["z"].std().values
        fluo = df_grouped["fluo"].agg(lambda x: mode(x, keepdims=True)[0][0]).values

        # Prepare a dataframe with the statistics
        df_tid = pd.DataFrame(
            columns=["tid", "n", "mx", "my", "mz", "sx", "sy", "sz", "fluo"]
        )

        df_tid["tid"] = tid
        df_tid["n"] = n
        df_tid["mx"] = mx
        df_tid["my"] = my
        df_tid["mz"] = mz
        df_tid["sx"] = sx
        df_tid["sy"] = sy
        df_tid["sz"] = sz
        df_tid["fluo"] = fluo

        # sx, sy sz columns will contain np.nan is n == 1: we replace with 0.0
        # @TODO: should this be changed?
        df_tid[["sx", "sy", "sz"]] = df_tid[["sx", "sy", "sz"]].fillna(value=0.0)

        # Return the results
        return df_tid

    def _calculate_weighted_positions(self):
        """Calculate per-trace localization weighted by relative photon count."""

        # Make sure we have processed dataframe to work on
        if self.full_dataframe is None:
            return

        # Only recompute weighted localizations if needed
        if not self.__weighted_localizations_to_be_recomputed:
            return

        # Work with currently selected rows
        df = self.filtered_dataframe

        # Normal or weighted averaging?
        if self.__use_weighted_localizations:
            # Calculate weighing factors for TIDs
            df = df.assign(
                eco_rel=df["eco"].groupby(df["tid"]).transform(lambda x: x / x.sum())
            )

            # Calculate relative contributions of (x, y, z)_i for each TID
            df["x_rel"] = df["x"] * df["eco_rel"]
            df["y_rel"] = df["y"] * df["eco_rel"]
            df["z_rel"] = df["z"] * df["eco_rel"]

            # Calculate the weighted localizations
            df_grouped = df.groupby("tid")
            tid = df_grouped["tid"].first().values
            x_w = df_grouped["x_rel"].sum().values
            y_w = df_grouped["y_rel"].sum().values
            z_w = df_grouped["z_rel"].sum().values
            fluo = (
                df_grouped["fluo"].agg(lambda x: mode(x, keepdims=True)[0][0]).values
            )  # Return the most frequent fluo ID

        else:
            # Calculate simple average of localizations by TID
            df_grouped = df.groupby(df["tid"])
            tid = df_grouped["tid"].first().values
            x_w = df_grouped["x"].mean().values
            y_w = df_grouped["y"].mean().values
            z_w = df_grouped["z"].mean().values
            fluo = (
                df_grouped["fluo"].agg(lambda x: mode(x, keepdims=True)[0][0]).values
            )  # Return the most frequent fluo ID

        # Prepare a dataframe with the weighted localizations
        df_loc = pd.DataFrame(columns=["tid", "x", "y", "z", "fluo"])
        df_loc["tid"] = tid
        df_loc["x"] = x_w
        df_loc["y"] = y_w
        df_loc["z"] = z_w
        df_loc["fluo"] = fluo

        # Store the results
        self.__weighted_localizations = df_loc

        # Make sure to flag the derived data to be recomputed
        self.__weighted_localizations_to_be_recomputed = False
