#  Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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

import numpy as np
import pyqtgraph as pg


class TimePlotter:
    """Utility class for time-based plotting shared between TimeInspector and ColorUnmixer."""

    @staticmethod
    def plot_localizations_per_unit_time(
        plot_widget,
        processor,
        time_resolution_sec,
        cache_dict,
        brush,
    ):
        """Plot number of localizations per unit time.
        
        Parameters
        ----------
        plot_widget : PlotWidget
            The PyQtGraph plot widget to plot on
        processor : MinFluxProcessor
            The data processor containing filtered_dataframe
        time_resolution_sec : int
            Time resolution in seconds (typically 60)
        cache_dict : dict
            Dictionary with keys 'data' and 'x_axis' for caching
        brush : QBrush
            Brush for bar coloring
        
        Returns
        -------
        bool
            True if plot was created, False otherwise
        """
        # Is the data cached?
        if cache_dict['data'] is None:
            if len(processor.filtered_dataframe.index) == 0:
                # No data to plot
                return False

            # Create `time_resolution_sec` bins starting from the minimum time
            tim_min = processor.filtered_dataframe["tim"].min()
            tim_max = processor.filtered_dataframe["tim"].max()
            
            # Align the start to a bin boundary
            bin_start = np.floor(tim_min / time_resolution_sec) * time_resolution_sec
            
            bin_edges = np.arange(
                start=bin_start,
                stop=tim_max + time_resolution_sec,
                step=time_resolution_sec,
            )
            bin_centers = bin_edges[:-1] + 0.5 * time_resolution_sec
            bin_width = time_resolution_sec

            # Calculate the histogram of localizations per unit time
            cache_dict['data'], _ = np.histogram(
                processor.filtered_dataframe["tim"].to_numpy(),
                bins=bin_edges,
                density=False,
            )

            # Cache the x range
            cache_dict['x_axis'] = (bin_centers - 0.5 * bin_width) / time_resolution_sec

        # Plot the histogram
        chart = pg.BarGraphItem(
            x=cache_dict['x_axis'],
            height=cache_dict['data'],
            width=0.9 * (cache_dict['x_axis'][1] - cache_dict['x_axis'][0]),
            brush=brush,
        )

        # Update the plot
        plot_widget.setXRange(cache_dict['x_axis'][0], cache_dict['x_axis'][-1])
        plot_widget.setYRange(0.0, cache_dict['data'].max())
        plot_widget.setLabel("left", text="Number of localizations per min")
        plot_widget.addItem(chart)
        
        return True

    @staticmethod
    def plot_localization_precision_per_unit_time(
        plot_widget,
        processor,
        time_resolution_sec,
        cache_dict,
        std_err=False,
    ):
        """Plot localization precision as a function of time.

        Parameters
        ----------
        plot_widget : PlotWidget
            The PyQtGraph plot widget to plot on
        processor : MinFluxProcessor
            The data processor containing filtered_dataframe
        time_resolution_sec : int
            Time resolution in seconds (typically 60)
        cache_dict : dict
            Dictionary with keys 'x', 'y', 'z', 'x_stderr', 'y_stderr', 'z_stderr', 'x_axis'
        std_err : bool
            Set to True to plot the standard error instead of the standard deviation
        
        Returns
        -------
        bool
            True if plot was created, False otherwise
        """
        # Add a legend
        if plot_widget.plotItem.legend is None:
            plot_widget.plotItem.addLegend()

        # Determine which cache keys to use
        cache_key_x = 'x_stderr' if std_err else 'x'
        cache_key_y = 'y_stderr' if std_err else 'y'
        cache_key_z = 'z_stderr' if std_err else 'z'

        # Is the data cached?
        if cache_dict[cache_key_x] is None:
            # Create `time_resolution_sec` bins starting from the minimum time
            tim_min = processor.filtered_dataframe["tim"].min()
            tim_max = processor.filtered_dataframe["tim"].max()
            
            # Align the start to a bin boundary
            bin_start = np.floor(tim_min / time_resolution_sec) * time_resolution_sec
            
            bin_edges = np.arange(
                start=bin_start,
                stop=tim_max + time_resolution_sec,
                step=time_resolution_sec,
            )
            bin_centers = bin_edges[:-1] + 0.5 * time_resolution_sec
            bin_width = time_resolution_sec

            # Allocate space for the results
            x_pr = np.zeros(len(bin_edges) - 1)
            y_pr = np.zeros(len(bin_edges) - 1)
            z_pr = np.zeros(len(bin_edges) - 1)

            # Now process all bins
            for i in range(len(bin_edges) - 1):
                time_range = (bin_edges[i], bin_edges[i + 1])
                df = processor.select_by_1d_range("tim", time_range)
                if len(df.index) > 0:
                    stats = processor.calculate_statistics_on(df)
                    if std_err:
                        x_pr[i] = stats["sx"].mean() / np.sqrt(len(stats["sx"]))
                        y_pr[i] = stats["sy"].mean() / np.sqrt(len(stats["sy"]))
                        z_pr[i] = stats["sz"].mean() / np.sqrt(len(stats["sz"]))
                    else:
                        x_pr[i] = stats["sx"].mean()
                        y_pr[i] = stats["sy"].mean()
                        z_pr[i] = stats["sz"].mean()
                else:
                    x_pr[i] = 0.0
                    y_pr[i] = 0.0
                    z_pr[i] = 0.0

            # Cache results for future plotting
            cache_dict[cache_key_x] = x_pr
            cache_dict[cache_key_y] = y_pr
            cache_dict[cache_key_z] = z_pr

            # Cache the x range
            cache_dict['x_axis'] = (bin_centers - 0.5 * bin_width) / time_resolution_sec

        # Alias
        x_pr = cache_dict[cache_key_x]
        y_pr = cache_dict[cache_key_y]
        z_pr = cache_dict[cache_key_z]

        # Get the max bin number for normalization
        n_max = np.max([x_pr.max(), y_pr.max(), z_pr.max()])

        if processor.is_3d:
            offset = 1 / 3
            bar_width = 0.9 / 3
        else:
            offset = 1 / 2
            bar_width = 0.9 / 2

        # Create the sx bar charts
        chart = pg.BarGraphItem(
            x=cache_dict['x_axis'],
            height=x_pr,
            width=bar_width,
            brush="r",
            alpha=0.5,
            name="σx",
        )
        plot_widget.addItem(chart)

        # Create the sy bar charts
        chart = pg.BarGraphItem(
            x=cache_dict['x_axis'] + offset,
            height=y_pr,
            width=bar_width,
            brush="b",
            alpha=0.5,
            name="σy",
        )
        plot_widget.addItem(chart)

        # Create the sz bar charts if needed
        if processor.is_3d:
            chart = pg.BarGraphItem(
                x=cache_dict['x_axis'] + 2 * offset,
                height=z_pr,
                width=bar_width,
                brush="k",
                alpha=0.5,
                name="σz",
            )
            plot_widget.addItem(chart)

        # Update the plot
        plot_widget.setXRange(cache_dict['x_axis'][0], cache_dict['x_axis'][-1])
        plot_widget.setYRange(0.0, n_max)
        plot_widget.setLabel("left", text="Localization precision (nm) per min")
        
        return True
