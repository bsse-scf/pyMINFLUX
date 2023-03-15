from typing import Union

import numpy as np
import pandas as pd

from pyminflux.reader import MinFluxReader
from pyminflux.state import State


class MinFluxProcessor:
    """Processor of MINFLUX data."""

    __slots__ = [
        "__minfluxreader",
        "state",
        "__filtered_stats_dataframe",
        "__selected_rows",
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

        # Keep a separate array of booleans to cache selection state
        self.__selected_rows = pd.Series(
            data=np.ones(self.__minfluxreader.num_valid_entries, dtype=bool),
            index=self.__minfluxreader.processed_dataframe.index,
        )

        # Cache the weighted, averaged TID positions
        self.__weighted_localizations = None

        # Keep track whether the statistics and the weighted localizations need to be recomputed
        self.__stats_to_be_recomputed = False
        self.__weighted_localizations_to_be_recomputed = False

        # Whether to use weighted average for localizations
        self.__use_weighted_localizations = False

        # Apply the global filters
        self._apply_global_filters()

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
    def filtered_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return dataframe with all filters applied.

        Returns
        -------

        filtered_dataframe: Union[None, pd.DataFrame]
            A Pandas dataframe or None if no file was loaded.
        """
        if self.__minfluxreader.processed_dataframe is None:
            return None
        return self.__minfluxreader.processed_dataframe.loc[self.__selected_rows]

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
        self.__selected_rows = pd.Series(
            data=np.ones(self.__minfluxreader.num_valid_entries, dtype=bool),
            index=self.__minfluxreader.processed_dataframe.index,
        )
        self._apply_global_filters()

    def select_dataframe_by_indices(
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

    def select_dataframe_by_2d_range(
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
            Tuple containing the minimum and maximum values for the x coordinates to be selected.

        y_range: tuple
            Tuple containing the minimum and maximum values for the y coordinates to be selected.

        from_weighted_locs: bool
            If True, select from the weighted_localizations dataframe; otherwise, from the filtered_dataframe.

        Returns
        -------

        subset: Union[None, pd.DataFrame]
            A view on a subset of the dataframe defined by the passed x and y ranges, or None if no file was loaded.
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

    def filter_dataframe_by_2d_range(self, x_prop, y_prop, x_range, y_range):
        """Filter dataset by the extracting a rectangular ROI over two parameters and two ranges.

        Parameters
        ----------

        x_prop: str
            First property to be filtered by corresponding x_range.

        y_prop: str
            Second property to be filtered by corresponding y_range.

        x_range: tuple
            Tuple containing the minimum and maximum values for the x coordinates to be selected.

        y_range: tuple
            Tuple containing the minimum and maximum values for the y coordinates to be selected.
        """

        # Make sure to always apply the global filters
        self._apply_global_filters()

        # Alias
        df = self.__minfluxreader.processed_dataframe

        # Make sure that the ranges are increasing
        x_min = x_range[0]
        x_max = x_range[1]
        if x_max < x_min:
            x_max, x_min = x_min, x_max

        y_min = y_range[0]
        y_max = y_range[1]
        if y_max < y_min:
            y_max, y_min = y_min, y_max

        # Apply filter
        self.__selected_rows = (
            self.__selected_rows
            & (df[x_prop] >= x_min)
            & (df[x_prop] < x_max)
            & (df[y_prop] >= y_min)
            & (df[y_prop] < y_max)
        )

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def _apply_global_filters(self):
        """Apply filters that are defined in the global application configuration."""

        # Make sure to count only currently selected rows
        df = self.__minfluxreader.processed_dataframe.copy()
        df.loc[np.invert(self.__selected_rows), "tid"] = np.nan

        # Select all rows where the count of TIDs is larger than self._min_trace_num
        counts = df["tid"].value_counts(normalize=False)
        self.__selected_rows = df["tid"].isin(
            counts[counts >= self.state.min_num_loc_per_trace].index
        )

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def filter_by_single_threshold(
        self, prop: str, threshold: Union[int, float], larger_than: bool = True
    ):
        """Apply single threshold to filter values either lower or higher (equal) than threshold for given property."""

        # Alias
        df = self.__minfluxreader.processed_dataframe

        # Apply filter
        if larger_than:
            self.__selected_rows = self.__selected_rows & (df[prop] >= threshold)
        else:
            self.__selected_rows = self.__selected_rows & (df[prop] < threshold)

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def filter_dataframe_by_1d_range(
        self,
        prop: str,
        min_threshold: Union[int, float],
        max_threshold: Union[int, float],
    ):
        """Apply min and max thresholding to the given property.

        Parameters
        ----------

        prop: str
            Name of the property (dataframe column) to filter.

        min_threshold: Union[int, float]
            Minimum value for prop to retain the row.

        max_threshold: Union[int, float]
            Maximum value for prop to retain the row.
        """

        # Make sure we have valid thresholds
        if min_threshold is None or max_threshold is None:
            return

        # Alias
        df = self.__minfluxreader.processed_dataframe

        # Apply filter
        self.__selected_rows = (
            self.__selected_rows
            & (df[prop] >= min_threshold)
            & (df[prop] < max_threshold)
        )

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def filter_dataframe_by_logical_indexing(self, indices):
        """Apply filter by logical indexing.

        Parameters
        ----------

        indices: array
            Logical array for selecting the elements to be returned.
        """

        # Filter by selected indices
        current_selection_index = self.__selected_rows.index[
            self.__selected_rows
        ].tolist()
        self.__selected_rows = pd.Series(
            data=np.ones(self.__minfluxreader.num_valid_entries, dtype=bool),
            index=self.__minfluxreader.processed_dataframe.index,
        )
        self.__selected_rows.loc[current_selection_index] = indices

        # Apply the global filters
        self._apply_global_filters()

        # Make sure to flag the derived data to be recomputed
        self.__stats_to_be_recomputed = True
        self.__weighted_localizations_to_be_recomputed = True

    def _calculate_statistics(self):
        """Calculate per-trace statistics."""

        # Make sure we have processed dataframe to work on
        if self.__minfluxreader.processed_dataframe is None:
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

        # Prepare a dataframe with the statistics
        df_tid = pd.DataFrame(columns=["tid", "n", "mx", "my", "mz", "sx", "sy", "sz"])

        df_tid["tid"] = tid
        df_tid["n"] = n
        df_tid["mx"] = mx
        df_tid["my"] = my
        df_tid["mz"] = mz
        df_tid["sx"] = sx
        df_tid["sy"] = sy
        df_tid["sz"] = sz

        # sx, sy sz columns will contain np.nan is n == 1: we replace with 0.0
        # @TODO: should this be changed?
        df_tid[["sx", "sy", "sz"]] = df_tid[["sx", "sy", "sz"]].fillna(value=0.0)

        # Store the results
        self.__filtered_stats_dataframe = df_tid

        # Flag the statistics to be computed
        self.__stats_to_be_recomputed = False

    def _calculate_weighted_positions(self):
        """Calculate per-trace localization weighted by relative photon count."""

        # Make sure we have processed dataframe to work on
        if self.__minfluxreader.processed_dataframe is None:
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

        else:

            # Calculate simple average of localizations by TID
            df_grouped = df.groupby(df["tid"])
            tid = df_grouped["tid"].first().values
            x_w = df_grouped["x"].mean().values
            y_w = df_grouped["y"].mean().values
            z_w = df_grouped["z"].mean().values

        # Prepare a dataframe with the weighted localizations
        df_loc = pd.DataFrame(columns=["tid", "x", "y", "z"])
        df_loc["tid"] = tid
        df_loc["x"] = x_w
        df_loc["y"] = y_w
        df_loc["z"] = z_w

        # Store the results
        self.__weighted_localizations = df_loc

        # Make sure to flag the derived data to be recomputed
        self.__weighted_localizations_to_be_recomputed = False
