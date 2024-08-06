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

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, QSignalBlocker, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, Qt
from PySide6.QtWidgets import QDialog, QMenu

from pyminflux.state import State
from pyminflux.ui.helpers import export_plot_interactive
from pyminflux.ui.roi_ranges import ROIRanges
from pyminflux.ui.ui_time_inspector import Ui_TimeInspector


class TimeInspector(QDialog, Ui_TimeInspector):
    """
    A QDialog to perform temporal analysis and selection.
    """

    # Signal that the fluorophore IDs have been assigned
    fluorophore_ids_assigned = Signal(int)
    processing_started = Signal()
    processing_completed = Signal()
    dataset_time_filtered = Signal()

    def __init__(self, processor):
        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_TimeInspector()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Keep a reference to the Processor
        self.processor = processor

        # Keep track of whether there is a plot to export
        self.plot_ready_to_export = False

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep track of the x-axis limits and the selection
        self.x_axis = None
        self.selection_range = None

        # Selection region
        self.selection_region = None

        # Cache plot data
        self.localizations_per_unit_time_cache = None
        self.localization_precision_per_unit_time_cache_x = None
        self.localization_precision_per_unit_time_cache_y = None
        self.localization_precision_per_unit_time_cache_z = None
        self.localization_precision_stderr_per_unit_time_cache_x = None
        self.localization_precision_stderr_per_unit_time_cache_y = None
        self.localization_precision_stderr_per_unit_time_cache_z = None

        # Time resolution

        self.time_resolution_sec = 60

        # Remember visibility status of the region
        self.roi_visible = True

        # Create the main plot widget
        self.plot_widget = PlotWidget(parent=self, background="w", title="")

        # Set data label to the ViewBox to be used when calling ROIRanges()
        self.plot_widget.getViewBox().data_label = "time_inspector"

        # Connect the main plot widget to the context menu callback
        self.plot_widget.scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu
        )

        # Keep a reference to the ROIRanges dialog
        self.roi_ranges_dialog = None

        # Add it to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

        # Add connections
        self.ui.pbPlot.clicked.connect(self.plot_selected)
        self.ui.pbAreaToggleVisibility.clicked.connect(self.toggle_region_visibility)
        self.ui.pbSelectionKeepData.clicked.connect(self.keep_time_region)
        self.ui.pbSelectionCropData.clicked.connect(self.crop_time_region)
        self.processing_started.connect(self.disable_ui_elements)
        self.processing_completed.connect(self.enable_ui_elements)

        # Plot the dcr histogram
        self.plot_selected()

    def invalidate_cache(self):
        """Invalidate the cache."""
        self.localizations_per_unit_time_cache = None
        self.localization_precision_per_unit_time_cache_x = None
        self.localization_precision_per_unit_time_cache_y = None
        self.localization_precision_per_unit_time_cache_z = None
        self.localization_precision_stderr_per_unit_time_cache_x = None
        self.localization_precision_stderr_per_unit_time_cache_y = None
        self.localization_precision_stderr_per_unit_time_cache_z = None

    @Slot()
    def update(self):
        """Update the plots as response to data changes."""

        # Invalidate cache
        self.invalidate_cache()

        # Switch back to the fastest plot
        self.ui.cbAnalysisSelection.setCurrentIndex(0)

        # Plot
        self.plot_selected()

    @Slot()
    def plot_selected(self):
        """Perform and plot the results of the selected analysis."""

        # Do we have something to plot?
        if (
            self.processor is None
            or self.processor.filtered_dataframe is None
            or len(self.processor.filtered_dataframe.index) == 0
        ):
            return

        # Mark that there is no plot ready to export
        self.plot_ready_to_export = False

        # Inform that processing started
        self.processing_started.emit()

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Get the requested plot
        if self.ui.cbAnalysisSelection.currentIndex() == 0:
            self.plot_localizations_per_unit_time()
        elif self.ui.cbAnalysisSelection.currentIndex() == 1:
            self.plot_localization_precision_per_unit_time(std_err=False)
        elif self.ui.cbAnalysisSelection.currentIndex() == 2:
            self.plot_localization_precision_per_unit_time(std_err=True)
        else:
            raise ValueError("Unexpected plotting request.")

        self.plot_widget.setLabel("bottom", text="time (min)")
        self.plot_widget.showAxis("bottom")
        self.plot_widget.showAxis("left")
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.setMenuEnabled(False)

        # Create a linear region for setting filtering thresholds. We create it
        # small enough not to be in the way.
        if self.selection_range is None:
            if self.state.time_thresholds is not None:
                mn, mx = self.state.time_thresholds
            else:
                mn, mx = np.percentile(
                    np.arange(self.x_axis[0], self.x_axis[-1]), [25, 75]
                )
            self.selection_range = (mn, mx)
            self.state.time_thresholds = (mn, mx)
        mn, mx = self.selection_range[0], self.selection_range[1]
        self.selection_region = pg.LinearRegionItem(
            values=[mn, mx],
            pen={"color": "b", "width": 3, "alpha": 0.5},
        )

        # Add to plot
        self.plot_widget.addItem(self.selection_region)

        # Attach labels to the region to be able to access them from callbacks.
        self.selection_region.low_thresh_label = pg.InfLineLabel(
            self.selection_region.lines[0], "{value:.2f}", position=0.95
        )
        self._change_region_label_font(self.selection_region.low_thresh_label)
        self.selection_region.high_thresh_label = pg.InfLineLabel(
            self.selection_region.lines[1], "{value:.2f}", position=0.90
        )
        self._change_region_label_font(self.selection_region.high_thresh_label)

        # Make sure it is visible
        self.selection_region.show()
        self.roi_visible = True

        # Connect signals
        self.selection_region.sigRegionChanged.connect(self.region_pos_changed)
        self.selection_region.sigRegionChangeFinished.connect(
            self.region_pos_changed_finished
        )

        # Mark that there is a plot ready to export
        self.plot_ready_to_export = True

        # Inform that processing completed
        self.processing_completed.emit()

    def plot_localizations_per_unit_time(self):
        """Plot number of localizations per unit time."""

        # Is the data cached?
        if self.localizations_per_unit_time_cache is None:
            if len(self.processor.filtered_dataframe.index) == 0:
                # No data to plot
                return

            # Create `time_resolution_sec` bins starting at 0.0.
            bin_edges = np.arange(
                start=0.0,
                stop=self.processor.filtered_dataframe["tim"].max()
                + self.time_resolution_sec,
                step=self.time_resolution_sec,
            )
            bin_centers = bin_edges[:-1] + 0.5 * self.time_resolution_sec
            bin_width = self.time_resolution_sec

            # Calculate the histogram of localizations per unit time
            self.localizations_per_unit_time_cache, _ = np.histogram(
                self.processor.filtered_dataframe["tim"].to_numpy(),
                bins=bin_edges,
                density=False,
            )

            # Cache the x range
            self.x_axis = (bin_centers - 0.5 * bin_width) / self.time_resolution_sec

        # Plot the histogram
        chart = pg.BarGraphItem(
            x=self.x_axis,
            height=self.localizations_per_unit_time_cache,
            width=0.9 * (self.x_axis[1] - self.x_axis[0]),
            brush=self.brush,
        )

        # Update the plot
        self.plot_widget.setXRange(self.x_axis[0], self.x_axis[-1])
        self.plot_widget.setYRange(0.0, self.localizations_per_unit_time_cache.max())
        self.plot_widget.setLabel("left", text="Number of localizations per min")
        self.plot_widget.addItem(chart)

    def plot_localization_precision_per_unit_time(self, std_err: bool = False):
        """Plot localization precision as a function of time.

        Parameters
        ----------

        std_err: bool
            Set to True to plot the standard error instead of the standard deviation.
        """

        # Add a legend
        if self.plot_widget.plotItem.legend is None:
            self.plot_widget.plotItem.addLegend()

        # Is the data cached?
        if (
            not std_err and self.localization_precision_per_unit_time_cache_x is None
        ) or (
            std_err and self.localization_precision_stderr_per_unit_time_cache_x is None
        ):
            # Create `time_resolution_sec` bins starting at 0.0.
            bin_edges = np.arange(
                start=0.0,
                stop=self.processor.filtered_dataframe["tim"].max()
                + self.time_resolution_sec,
                step=self.time_resolution_sec,
            )
            bin_centers = bin_edges[:-1] + 0.5 * self.time_resolution_sec
            bin_width = self.time_resolution_sec

            # Allocate space for the results
            x_pr = np.zeros(len(bin_edges) - 1)
            y_pr = np.zeros(len(bin_edges) - 1)
            z_pr = np.zeros(len(bin_edges) - 1)

            # Now process all bins
            for i in range(len(bin_edges) - 1):
                time_range = (bin_edges[i], bin_edges[i + 1])
                df = self.processor.select_by_1d_range("tim", time_range)
                if len(df.index) > 0:
                    stats = self.processor.calculate_statistics_on(df)
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
            if std_err:
                self.localization_precision_stderr_per_unit_time_cache_x = x_pr
                self.localization_precision_stderr_per_unit_time_cache_y = y_pr
                self.localization_precision_stderr_per_unit_time_cache_z = z_pr
            else:
                self.localization_precision_per_unit_time_cache_x = x_pr
                self.localization_precision_per_unit_time_cache_y = y_pr
                self.localization_precision_per_unit_time_cache_z = z_pr

            # Cache the x range
            self.x_axis = (bin_centers - 0.5 * bin_width) / self.time_resolution_sec

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Alias
        if std_err:
            x_pr = self.localization_precision_stderr_per_unit_time_cache_x
            y_pr = self.localization_precision_stderr_per_unit_time_cache_y
            z_pr = self.localization_precision_stderr_per_unit_time_cache_z
        else:
            x_pr = self.localization_precision_per_unit_time_cache_x
            y_pr = self.localization_precision_per_unit_time_cache_y
            z_pr = self.localization_precision_per_unit_time_cache_z

        # Get the max bin number for normalization
        n_max = np.max([x_pr.max(), y_pr.max(), z_pr.max()])

        if self.processor.is_3d:
            offset = 1 / 3
            bar_width = 0.9 / 3
        else:
            offset = 1 / 2
            bar_width = 0.9 / 2

        # Create the sx bar charts
        chart = pg.BarGraphItem(
            x=self.x_axis,
            height=x_pr,
            width=bar_width,
            brush="r",
            alpha=0.5,
            name="σx",
        )
        self.plot_widget.addItem(chart)

        # Create the sy bar charts
        chart = pg.BarGraphItem(
            x=self.x_axis + offset,
            height=y_pr,
            width=bar_width,
            brush="b",
            alpha=0.5,
            name="σy",
        )
        self.plot_widget.addItem(chart)

        # Create the sz bar charts if needed
        if self.processor.is_3d:
            chart = pg.BarGraphItem(
                x=self.x_axis + 2 * offset,
                height=z_pr,
                width=bar_width,
                brush="k",
                alpha=0.5,
                name="σz",
            )
            self.plot_widget.addItem(chart)

        # Update the plot
        self.plot_widget.setXRange(self.x_axis[0], self.x_axis[-1])
        self.plot_widget.setYRange(0.0, n_max)
        self.plot_widget.setLabel("left", text="Localization precision (nm) per min")

    @staticmethod
    def _change_region_label_font(region_label):
        """Change the region label font style."""
        text_item = region_label.textItem
        text_item.setDefaultTextColor(QColor("gray"))
        font = text_item.font()
        font.setWeight(QFont.Bold)
        font.setPointSize(20)

    def region_pos_changed(self, item):
        """Called when the line region on one of the histogram plots is changing."""

        # This seems to be a bug in pyqtgraph. When moving a LinearRegionItems with
        # two InfLineLabels attached to the region boundaries (InfiniteLine), only
        # the label of the upper bound is automatically updated.
        region = item.getRegion()
        low_thresh_label = item.low_thresh_label
        if low_thresh_label.format == "{value:.2f}":
            value = f"{min(region):.2f}"
        elif low_thresh_label.format == "{value:.0f}":
            value = f"{min(region):.0f}"
        else:
            value = f"{min(region)}"
        low_thresh_label.textItem.setPlainText(value)

    def region_pos_changed_finished(self, item):
        """Called when the line region on one of the histogram plots has changed."""

        # Get the bounds of the region
        mn, mx = item.getRegion()

        # Update the selection range
        self.selection_range = (mn, mx)

        # Upate the state as well
        self.state.time_thresholds = (mn, mx)

    def toggle_region_visibility(self, b):
        """Toggles the visibility of the line region."""

        if self.selection_region is None:
            return

        if self.roi_visible:
            self.selection_region.hide()
            self.roi_visible = False
            self.ui.pbAreaToggleVisibility.setText("Show")
        else:
            self.selection_region.show()
            self.roi_visible = True
            self.ui.pbAreaToggleVisibility.setText("Hide")

    def crop_time_region(self):
        """Filter away selected time region."""

        # Get the range
        mn, mx = self.selection_region.getRegion()

        # Make sure the selection is up-to-date
        self.selection_range = (mn, mx)

        # Convert to seconds
        mn_s = mn * self.time_resolution_sec
        mx_s = mx * self.time_resolution_sec

        # Filter
        self.processor.filter_by_1d_range_complement("tim", (mn_s, mx_s))

        # Invalidate the cache
        self.invalidate_cache()

        # Inform that the data has been filtered
        self.dataset_time_filtered.emit()

        # Store thresholds
        self.state.applied_time_thresholds = (mn, mx)

        # Update the plot
        self.plot_selected()

    def keep_time_region(self):
        """Keep the selected time region."""

        # Get the range
        mn, mx = self.selection_region.getRegion()

        # Make sure the selection is up-to-date
        self.selection_range = (mn, mx)

        # Convert to seconds
        mn_s = mn * self.time_resolution_sec
        mx_s = mx * self.time_resolution_sec

        # Filter
        self.processor.filter_by_1d_range("tim", (mn_s, mx_s))

        # Invalidate the cache
        self.invalidate_cache()

        # Inform that the data has been filtered
        self.dataset_time_filtered.emit()

        # Store thresholds
        self.state.applied_time_thresholds = (mn, mx)

        # Update the plot
        self.plot_selected()

    def disable_ui_elements(self):
        """Disable elements and inform that a processing is ongoing."""
        self.ui.cbAnalysisSelection.setEnabled(False)
        self.ui.pbPlot.setEnabled(False)
        self.ui.lbSelectionActions.setEnabled(False)
        self.ui.pbAreaToggleVisibility.setEnabled(False)
        self.ui.pbSelectionCropData.setEnabled(False)
        self.ui.pbSelectionKeepData.setEnabled(False)

    def enable_ui_elements(self):
        """Disable elements and inform that a processing is ongoing."""
        self.ui.cbAnalysisSelection.setEnabled(True)
        self.ui.pbPlot.setEnabled(True)
        self.ui.lbSelectionActions.setEnabled(True)
        self.ui.pbAreaToggleVisibility.setEnabled(True)
        self.ui.pbSelectionCropData.setEnabled(True)
        self.ui.pbSelectionKeepData.setEnabled(True)

    def histogram_raise_context_menu(self, ev):
        """Create a context menu on the plot."""
        if ev.button() == Qt.MouseButton.RightButton:
            if not self.plot_ready_to_export:
                return

            menu = QMenu()
            ranges_action = QAction("Set range")
            ranges_action.triggered.connect(
                lambda checked: self.roi_open_ranges_dialog(ev.currentItem.data_label)
            )
            menu.addAction(ranges_action)
            keep_action = QAction("Keep data")
            keep_action.triggered.connect(self.keep_time_region)
            menu.addAction(keep_action)
            drop_action = QAction("Drop data")
            drop_action.triggered.connect(self.crop_time_region)
            menu.addAction(drop_action)
            menu.addSeparator()
            export_action = QAction("Export plot")
            export_action.triggered.connect(
                lambda checked: export_plot_interactive(ev.currentItem)
            )
            menu.addAction(export_action)
            pos = ev.screenPos()
            menu.exec(QPoint(int(pos.x()), int(pos.y())))
            ev.accept()
        else:
            ev.ignore()

    def roi_open_ranges_dialog(self, item):
        """Open dialog to manually set the filter ranges"""
        if self.roi_ranges_dialog is None:
            self.roi_ranges_dialog = ROIRanges()
            self.roi_ranges_dialog.data_ranges_changed.connect(
                self.roi_changes_finished
            )
        else:
            self.roi_ranges_dialog.update_fields()
        self.roi_ranges_dialog.set_target(item)
        self.roi_ranges_dialog.show()
        self.roi_ranges_dialog.activateWindow()

    @Slot()
    def roi_changes_finished(self):
        """Called when the ROIChanges dialog has accepted the changes."""

        # Signal blocker on self.efo_plot, self.cfr_plot and self.tr_len_plot
        plot_blocker = QSignalBlocker(self.plot_widget)

        # Block signals from the plot widget
        plot_blocker.reblock()

        # Update the thresholds
        self.selection_region.setRegion(self.state.time_thresholds)

        # Unblock the self.efo_plot and self.cfr_plot signals
        plot_blocker.unblock()
