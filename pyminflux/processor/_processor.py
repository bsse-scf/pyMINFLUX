from typing import Optional, Tuple, Union

import pandas as pd

from pyminflux.reader import MinFluxReader
from pyminflux.state import State


class MinFluxProcessor:
    """Processor of MINFLUX data."""

    def __init__(self, minfluxreader: MinFluxReader):
        """Constructor.

        Parameters
        ----------

        minfluxreader: pyminflux.reader.MinFluxReader
            MinFluxReader.
        """

        # Store a reference to the MinFluxReader
        self._minfluxreader = minfluxreader

        # Keep a reference to the state machine
        self.state = State()

        # Keep track of whether recalculation is needed
        self._must_recalculate = False

        # Cache the filtered dataframes
        self._filtered_dataframe = None
        self._filtered_stats_dataframe = None

        # Apply the parameter filters
        self._apply_thresholds()

    @property
    def is_3d(self):
        """Return True if the acquisition is 3D."""
        return self._minfluxreader.is_3d

    @property
    def num_values(self):
        """Return the number of values in the (filtered) dataframe."""
        if self._filtered_dataframe is None:
            return 0
        return len(self._filtered_dataframe.index)

    @property
    def processed_dataframe(self) -> Union[None, pd.DataFrame]:
        """Return dataframe with all filters applied."""
        if self._must_recalculate:
            raise NotImplementedError("Implement me!")
        return self._filtered_dataframe

    @property
    def processed_dataframe_stats(self) -> Union[None, pd.DataFrame]:
        """Return dataframe stats with all filters applied."""
        if self._must_recalculate:
            self._calculate_statistics()
        return self._filtered_stats_dataframe

    def update_filters(self):
        """Apply filters."""
        # self._must_recalculate = True
        # self._drop_low_tid_count()
        self._apply_thresholds()
        # self._calculate_statistics()
        # self._must_recalculate = False

    def _calculate_statistics(self):
        """Calculate per-trace statistics."""

        # @TODO Debug information: remove
        print("Recalculating statistics.")

        # Make sure we have processed dataframe to work on
        if self._filtered_dataframe is None:
            return

        # Calculate some statistics per TID on the processed dataframe
        df_grouped = self._filtered_dataframe.groupby("tid")

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
        self._filtered_stats_dataframe = df_tid

    def _apply_thresholds(self):
        """Apply the data thresholds."""

        #
        # First, drop TIDs that have less than the minimum number of rows in the original dataframe.
        #

        # Work on a copy of the raw dataframe from the reader
        df = self._minfluxreader.processed_dataframe.copy()

        # Remove all rows where the count of TIDs is lower than self._min_trace_num
        counts = df["tid"].value_counts(normalize=False)
        df = df.loc[
            df["tid"].isin(counts[counts > self.state.min_num_loc_per_trace].index), :
        ]

        #
        # Then apply the EFO and CFR thresholds
        #

        # Apply filters?
        if self.state.enable_filter_efo:
            if self.state.efo_thresholds is not None:
                df = df[
                    (df["efo"] > self.state.efo_thresholds[0])
                    & (df["efo"] < self.state.efo_thresholds[1])
                ]

        if self.state.enable_filter_cfr:
            if self.state.efo_thresholds is not None:
                df = df[
                    (df["cfr"] > self.state.cfr_thresholds[0])
                    & (df["cfr"] < self.state.cfr_thresholds[1])
                ]

        # Cache the result
        self._filtered_dataframe = df

        #
        # Finally, update the statistics
        #

        # Calculate the statistics
        self._calculate_statistics()
