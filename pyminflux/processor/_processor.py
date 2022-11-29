from typing import Union

import pandas as pd

from pyminflux.reader import MinFluxReader


class MinFluxProcessor:
    """Processor of MINFLUX data."""

    def __init__(self, minfluxreader: MinFluxReader, min_trace_num: int = 1):
        """Constructor.

        Parameters
        ----------

        minfluxreader: pyminflux.reader.MinFluxReader
            MinFluxReader.
        """

        # Store a reference to the MinFluxReader
        self._minfluxreader = minfluxreader

        # Store the minimum number of traces to consider
        self._min_trace_numb = min_trace_num

        # Keep track of whether recalculation is needed
        self._must_recalculate = False

        # Cache the filtered dataframes
        self._filtered_dataframe = None
        self._filtered_stats_dataframe = None

        # Cache the datadrames with the applied filters
        self.apply_filters()

    @property
    def is_3d(self):
        """Return True if the acquisition is 3D."""
        return self._minfluxreader.is_3d

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
            raise NotImplementedError("Implement me!")
        return self._filtered_stats_dataframe

    def _calculate_statistics(self):
        """Calculate per-trace statistics."""

        # Make sure we have processed dataframe to work on
        if self._minfluxreader.processed_dataframe is None:
            return

        # Calculate some statistics per TID on the processed dataframe
        df_grouped = self._minfluxreader.processed_dataframe.groupby("tid")

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
        df_tid[["sx", "sy", "sz"]] = df_tid[["sx", "sy", "sz"]].fillna(value=0.0)

        return df_tid

    def apply_filters(self):
        """Apply current filters and cache the results."""
        # @TODO Apply filters
        self._filtered_dataframe = self._minfluxreader.processed_dataframe
        self._filtered_stats_dataframe = self._calculate_statistics()
