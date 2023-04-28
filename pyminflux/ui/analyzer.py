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

from typing import Optional, Tuple

import numpy as np
import pyqtgraph as pg
from pyqtgraph import AxisItem, ViewBox
from PySide6 import QtCore
from PySide6.QtCore import QPoint, QSignalBlocker, Signal, Slot
from PySide6.QtGui import QAction, QColor, QDoubleValidator, QFont, Qt
from PySide6.QtWidgets import QDialog, QLabel, QMenu

from ..analysis import find_cutoff_near_value, get_robust_threshold, prepare_histogram
from ..processor import MinFluxProcessor
from ..state import State
from .roi_ranges import ROIRanges
from .ui_analyzer import Ui_Analyzer


class Analyzer(QDialog, Ui_Analyzer):
    # Signal that the data viewers should be updated
    data_filters_changed = Signal(name="data_filters_changed")
    plotting_started = Signal(name="plotting_started")
    plotting_completed = Signal(name="plotting_completed")
    efo_bounds_changed = Signal(name="efo_bounds_changed")
    cfr_bounds_changed = Signal(name="cfr_bounds_changed")
    cfr_threshold_factor_changed = Signal(name="cfr_threshold_factor_changed")
    cfr_lower_bound_state_changed = Signal(name="cfr_lower_bound_state_changed")
    cfr_upper_bound_state_changed = Signal(name="cfr_upper_bound_state_changed")

    def __init__(self, minfluxprocessor: MinFluxProcessor, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_Analyzer()
        self.ui.setupUi(self)

        # Store the reference to the reader
        self._minfluxprocessor = minfluxprocessor

        # Reference to the communications label
        self.communication_label = None

        # Keep references to the plots
        self.efo_plot = None
        self.cfr_plot = None
        self.sx_plot = None
        self.sy_plot = None
        self.sz_plot = None
        self.efo_region = None
        self.cfr_region = None

        # Keep a reference to the singleton State class
        self.state = State()

        # Remember the data ranges (default to the options)
        self.efo_range = self.state.efo_range
        self.cfr_range = self.state.cfr_range
        self.loc_precision_range = self.state.loc_precision_range

        # Create widgets
        self.create_widgets()

        #
        # Set defaults
        #

        # EFO cutoff frequency tab
        self.ui.leEFOExpectedCutoff.setText(str(self.state.efo_expected_frequency))
        self.ui.leEFOExpectedCutoff.setValidator(
            QDoubleValidator(bottom=0.0, decimals=2)
        )

        # CFR filtering tab
        self.ui.checkCFRLowerThreshold.setChecked(self.state.enable_cfr_lower_threshold)
        self.ui.checkCFRUpperThreshold.setChecked(self.state.enable_cfr_upper_threshold)
        self.ui.leCFRFilterThreshFactor.setText(str(self.state.cfr_threshold_factor))
        self.ui.leCFRFilterThreshFactor.setValidator(
            QDoubleValidator(bottom=0.0, top=5.0, decimals=2)
        )

        # Keep a reference to the ROIRanges dialog
        self.roi_ranges_dialog = None

        # Set signal-slot connections
        self.setup_conn()

    def setup_conn(self):
        """Set up signal-slot connections."""

        # EFO peak detection tab
        self.ui.pbDetectCutoffFrequency.clicked.connect(
            self.run_efo_cutoff_frequency_detection
        )
        self.ui.pbEFORunFilter.clicked.connect(
            self.run_efo_filter_and_broadcast_viewers_update
        )
        self.ui.leEFOExpectedCutoff.textChanged.connect(
            self.persist_efo_expected_frequency
        )

        # CFR filtering tab
        self.ui.pbCFRRunFilter.clicked.connect(
            self.run_cfr_filter_and_broadcast_viewers_update
        )
        self.ui.checkCFRLowerThreshold.stateChanged.connect(
            self.persist_cfr_lower_threshold
        )
        self.ui.checkCFRUpperThreshold.stateChanged.connect(
            self.persist_cfr_upper_threshold
        )
        self.ui.pbCFRRunAutoThreshold.clicked.connect(self.run_cfr_auto_threshold)
        self.ui.leCFRFilterThreshFactor.textChanged.connect(
            self.persist_cfr_threshold_factor
        )

        # Others
        self.ui.pbReset.clicked.connect(self.reset_filters)
        self.plotting_started.connect(self.disable_buttons)
        self.plotting_completed.connect(self.enable_buttons)

    def closeEvent(self, ev):
        """Close event."""
        if self.roi_ranges_dialog is not None:
            self.roi_ranges_dialog.close()
        super().closeEvent(ev)

    def create_widgets(self):
        """Create widgets."""

        # Communications layout
        self.communication_label = QLabel("Sorry, no data.")
        self.communication_label.setAlignment(QtCore.Qt.AlignCenter)
        font = self.communication_label.font()
        font.setPointSize(16)
        self.communication_label.setFont(font)
        self.ui.communication_layout.addWidget(self.communication_label)
        self.communication_label.hide()

        # Parameters Layout
        self.efo_plot = pg.PlotWidget(parent=self, background="w", title="EFO")
        self.efo_plot.setMouseEnabled(x=True, y=False)
        self.efo_plot.setMenuEnabled(False)
        self.efo_plot.scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu_with_filtering
        )

        self.cfr_plot = pg.PlotWidget(parent=self, background="w", title="CFR")
        self.cfr_plot.setMouseEnabled(x=True, y=False)
        self.cfr_plot.setMenuEnabled(False)
        self.cfr_plot.scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu_with_filtering
        )

        self.ui.parameters_layout.addWidget(self.efo_plot)
        self.efo_plot.hide()
        self.ui.parameters_layout.addWidget(self.cfr_plot)
        self.cfr_plot.hide()

        # Localizations layout
        self.sx_plot = pg.PlotWidget(parent=self, background="w", title="σx")
        self.sx_plot.setMouseEnabled(x=True, y=False)
        self.sx_plot.setMenuEnabled(False)
        self.sx_plot.scene().sigMouseClicked.connect(self.histogram_raise_context_menu)

        self.sy_plot = pg.PlotWidget(parent=self, background="w", title="σy")
        self.sy_plot.setMouseEnabled(x=True, y=False)
        self.sy_plot.setMenuEnabled(False)
        self.sy_plot.scene().sigMouseClicked.connect(self.histogram_raise_context_menu)

        self.sz_plot = pg.PlotWidget(parent=self, background="w", title="σz")
        self.sz_plot.setMouseEnabled(x=True, y=False)
        self.sz_plot.setMenuEnabled(False)
        self.sz_plot.scene().sigMouseClicked.connect(self.histogram_raise_context_menu)

        self.ui.localizations_layout.addWidget(self.sx_plot)
        self.sx_plot.hide()
        self.ui.localizations_layout.addWidget(self.sy_plot)
        self.sy_plot.hide()
        self.ui.localizations_layout.addWidget(self.sz_plot)
        self.sz_plot.hide()

    def keyPressEvent(self, ev):
        """Key press event."""

        # Do not capture key events for now
        ev.ignore()

    def set_processor(self, minfluxprocessor: MinFluxProcessor):
        """Reset the internal state."""
        self._minfluxprocessor = minfluxprocessor
        self.efo_region = None
        self.cfr_region = None
        self.efo_range = None
        self.cfr_range = None

    @Slot(name="run_efo_cutoff_frequency_detection")
    def run_efo_cutoff_frequency_detection(self):
        """Run EFO cutoff frequency detection."""

        # Get the approximate frequency
        frequency = 2.0 * float(self.ui.leEFOExpectedCutoff.text())

        # Extract current min_efo
        if self.state.efo_thresholds is None:
            min_efo = self._minfluxprocessor.filtered_dataframe["efo"].values.min()
        else:
            min_efo = self.state.efo_thresholds[0]

        # Histogram bin settings
        efo_auto_bins = self.state.efo_bin_size_hz == 0

        # Calculate thresholds for EFO
        n_efo, _, b_efo, _ = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["efo"].values,
            auto_bins=efo_auto_bins,
            bin_size=self.state.efo_bin_size_hz,
        )
        cutoff_frequency = find_cutoff_near_value(
            counts=n_efo,
            bins=b_efo,
            expected_value=frequency,
        )

        # If the search failed, we return
        if cutoff_frequency is None:
            return

        # Set the new upper bound
        max_efo = cutoff_frequency
        self.state.efo_thresholds = (min_efo, max_efo)

        # Update plot
        self.efo_region.setRegion(self.state.efo_thresholds)

    @Slot(name="run_cfr_auto_threshold")
    def run_cfr_auto_threshold(self):
        """Run auto-threshold on EFO and CFR values and update the plots."""

        # Is there something to calculate?
        if (
            not self.state.enable_cfr_lower_threshold
            and not self.state.enable_cfr_upper_threshold
        ):
            print("Both lower and upper CFR thresholds are disabled.")
            return

        # Initialize values
        if self.state.cfr_thresholds is None:
            min_cfr = self._minfluxprocessor.filtered_dataframe["cfr"].values.min()
            max_cfr = self._minfluxprocessor.filtered_dataframe["cfr"].values.max()
        else:
            min_cfr = self.state.cfr_thresholds[0]
            max_cfr = self.state.cfr_thresholds[1]

        # Calculate thresholds for CFR
        upper_thresh_cfr, lower_thresh_cfr, _, _ = get_robust_threshold(
            self._minfluxprocessor.filtered_dataframe["cfr"].values,
            factor=self.state.cfr_threshold_factor,
        )
        if self.state.enable_cfr_lower_threshold:
            min_cfr = lower_thresh_cfr
        if self.state.enable_cfr_upper_threshold:
            max_cfr = upper_thresh_cfr
        self.state.cfr_thresholds = (min_cfr, max_cfr)

        # Update plot
        self.cfr_region.setRegion(self.state.cfr_thresholds)

    @Slot(int, name="persist_cfr_lower_threshold")
    def persist_cfr_lower_threshold(self, state):
        self.state.enable_cfr_lower_threshold = state != 0
        self.cfr_lower_bound_state_changed.emit()

    @Slot(int, name="persist_cfr_upper_threshold")
    def persist_cfr_upper_threshold(self, state):
        self.state.enable_cfr_upper_threshold = state != 0
        self.cfr_upper_bound_state_changed.emit()

    @Slot(str, name="persist_efo_expected_frequency")
    def persist_efo_expected_frequency(self, text):
        try:
            efo_expected_frequency = float(text)
        except ValueError as _:
            return
        self.state.efo_expected_frequency = efo_expected_frequency

    @Slot(str, name="persist_cfr_threshold_factor")
    def persist_cfr_threshold_factor(self, text):
        try:
            cfr_threshold_factor = float(text)
        except ValueError as _:
            return
        self.state.cfr_threshold_factor = cfr_threshold_factor

        # Broadcast
        self.cfr_threshold_factor_changed.emit()

    @Slot(name="reset_filters")
    def reset_filters(self):
        """Reset efo and cfr filters."""

        # Reset filters and data
        self._minfluxprocessor.reset()
        self.state.efo_thresholds = None
        self.state.cfr_thresholds = None

        # Update the plots
        self.plot()

        # Signal that the external viewers should be updated
        self.data_filters_changed.emit()

    @Slot(name="run_efo_filter_and_broadcast_viewers_update")
    def run_efo_filter_and_broadcast_viewers_update(self):
        """Apply the EFO filter and inform the rest of the application that the data viewers should be updated."""

        # Apply the EFO filter if needed
        if self.state.efo_thresholds is not None:
            self._minfluxprocessor.filter_by_1d_range(
                "efo", (self.state.efo_thresholds[0], self.state.efo_thresholds[1])
            )

        # Update the histograms
        self.plot()

        # Signal that the external viewers should be updated
        self.data_filters_changed.emit()

    @Slot(name="run_cfr_filter_and_broadcast_viewers_update")
    def run_cfr_filter_and_broadcast_viewers_update(self):
        """Apply the CFR filter and inform the rest of the application that the data viewers should be updated."""

        # Apply the CFR filter if needed
        if self.state.cfr_thresholds is not None:
            self._minfluxprocessor.filter_by_1d_range(
                "cfr", (self.state.cfr_thresholds[0], self.state.cfr_thresholds[1])
            )

        # Update the histograms
        self.plot()

        # Signal that the external viewers should be updated
        self.data_filters_changed.emit()

    @Slot(name="disable_buttons")
    def disable_buttons(self):
        self.ui.pbReset.setEnabled(False)
        self.ui.pbDetectCutoffFrequency.setEnabled(False)
        self.ui.pbCFRRunAutoThreshold.setEnabled(False)
        self.ui.pbEFORunFilter.setEnabled(False)
        self.ui.pbCFRRunFilter.setEnabled(False)

    @Slot(name="enable_buttons")
    def enable_buttons(self):
        self.ui.pbReset.setEnabled(True)
        self.ui.pbDetectCutoffFrequency.setEnabled(True)
        self.ui.pbCFRRunAutoThreshold.setEnabled(True)
        self.ui.pbEFORunFilter.setEnabled(True)
        self.ui.pbCFRRunFilter.setEnabled(True)

    def plot(self):
        """Plot histograms."""

        # Hide the communications label
        self.communication_label.hide()

        # Make sure there is data to plot
        is_data = True
        if self._minfluxprocessor is None:
            is_data = False

        if self._minfluxprocessor.filtered_dataframe is None:
            is_data = False

        if self._minfluxprocessor.num_values == 0:
            is_data = False

        # Announce that the plotting has started
        self.plotting_started.emit()

        for item in self.efo_plot.allChildItems():
            self.efo_plot.removeItem(item)
        for item in self.cfr_plot.allChildItems():
            self.cfr_plot.removeItem(item)
        for item in self.sx_plot.allChildItems():
            self.sx_plot.removeItem(item)
        for item in self.sy_plot.allChildItems():
            self.sy_plot.removeItem(item)
        for item in self.sz_plot.allChildItems():
            self.sz_plot.removeItem(item)

        # Is there data to plot?
        if not is_data:
            # Show the communication label
            self.communication_label.show()

            # Announce that the plotting has completed
            self.plotting_completed.emit()

            return

        # Histogram bin settings
        efo_auto_bins = self.state.efo_bin_size_hz == 0

        # Calculate the proper aspect ratio and view ranges for the relevant plots
        n_efo, efo_bin_edges, efo_bin_centers, efo_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["efo"].values,
            auto_bins=efo_auto_bins,
            bin_size=self.state.efo_bin_size_hz,
        )
        n_cfr, cfr_bin_edges, cfr_bin_centers, cfr_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["cfr"].values,
            auto_bins=True,
            bin_size=0.0,
        )

        #
        # Get "efo" and "cfr" measurements, and "sx", "sy" and "sz" localization jitter
        #

        # "efo"
        if self.state.efo_thresholds is None:
            self.state.efo_thresholds = (efo_bin_edges[0], efo_bin_edges[-1])

        self.efo_region = self._create_histogram_plot(
            "efo",
            self.efo_plot,
            n_efo,
            efo_bin_edges,
            efo_bin_centers,
            efo_bin_width,
            axis_range=self.efo_range,
            brush="b",
            fmt="{value:.0f}",
            support_thresholding=True,
            thresholds=self.state.efo_thresholds,
        )
        self.efo_plot.show()

        # cfr
        if self.state.cfr_thresholds is None:
            self.state.cfr_thresholds = (cfr_bin_edges[0], cfr_bin_edges[-1])

        self.cfr_region = self._create_histogram_plot(
            "cfr",
            self.cfr_plot,
            n_cfr,
            cfr_bin_edges,
            cfr_bin_centers,
            cfr_bin_width,
            axis_range=self.cfr_range,
            brush="r",
            fmt="{value:.2f}",
            support_thresholding=True,
            thresholds=self.state.cfr_thresholds,
            force_min_x_range_to_zero=False,
        )
        self.cfr_plot.show()

        # sx
        n_sx, sx_bin_edges, sx_bin_centers, sx_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe_stats["sx"].values,
            auto_bins=True,
            bin_size=0.0,
        )
        _ = self._create_histogram_plot(
            "sx",
            self.sx_plot,
            n_sx,
            sx_bin_edges,
            sx_bin_centers,
            sx_bin_width,
            axis_range=self.loc_precision_range,
            brush="k",
            support_thresholding=False,
        )
        self._add_median_line(
            self.sx_plot, self._minfluxprocessor.filtered_dataframe_stats["sx"].values
        )
        self.sx_plot.show()

        # sy
        n_sy, sy_bin_edges, sy_bin_centers, sy_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe_stats["sy"].values,
            auto_bins=True,
            bin_size=0.0,
        )
        _ = self._create_histogram_plot(
            "sy",
            self.sy_plot,
            n_sy,
            sy_bin_edges,
            sy_bin_centers,
            sy_bin_width,
            axis_range=self.loc_precision_range,
            brush="k",
            support_thresholding=False,
        )
        self._add_median_line(
            self.sy_plot, self._minfluxprocessor.filtered_dataframe_stats["sy"].values
        )
        self.sy_plot.show()

        # sz
        if self._minfluxprocessor.is_3d:
            n_sz, sz_bin_edges, sz_bin_centers, sz_bin_width = prepare_histogram(
                self._minfluxprocessor.filtered_dataframe_stats["sz"].values,
                auto_bins=True,
                bin_size=0.0,
            )
            _ = self._create_histogram_plot(
                "sz",
                self.sz_plot,
                n_sz,
                sz_bin_edges,
                sz_bin_centers,
                sz_bin_width,
                axis_range=self.loc_precision_range,
                brush="k",
                support_thresholding=False,
            )
            self._add_median_line(
                self.sz_plot,
                self._minfluxprocessor.filtered_dataframe_stats["sz"].values,
            )
            self.sz_plot.show()
        else:
            self.sz_plot.hide()

        # Announce that the plotting has completed
        self.plotting_completed.emit()

    def _create_histogram_plot(
        self,
        plot_id,
        plot_widget,
        n: np.ndarray,
        bin_edges: np.ndarray,
        bin_centers: np.ndarray,
        bin_width: np.ndarray,
        *,
        axis_range: Optional[tuple] = None,
        brush: str = "b",
        fmt: str = "{value:0.2f}",
        support_thresholding: bool = False,
        thresholds: Optional[Tuple] = None,
        force_min_x_range_to_zero: bool = True,
    ):
        """Create a histogram plot and return it to be added to the layout."""

        # Check for consistency
        if support_thresholding and thresholds is None:
            raise ValueError(
                "If 'support_thresholding' is True, 'thresholds' must be a tuple with two values."
            )
        if thresholds is not None and len(thresholds) != 2:
            raise ValueError(
                "If 'support_thresholding' is True, 'thresholds' must be a tuple with two values."
            )

        chart = pg.BarGraphItem(
            x=bin_centers, height=n, width=0.9 * bin_width, brush=brush
        )

        if axis_range is None:
            axis_range = (bin_edges[0], bin_edges[-1])

        # Range values
        if force_min_x_range_to_zero:
            x0 = 0.0
        else:
            x0 = axis_range[0]
        plot_widget.setXRange(x0, axis_range[1])  # setXRange()'s padding misbehaves
        plot_widget.setYRange(0.0, n.max())
        plot_widget.addItem(chart)

        region = None
        if support_thresholding:
            # Create a linear region for setting filtering thresholds
            region = pg.LinearRegionItem(
                values=[thresholds[0], thresholds[1]],
                pen={"color": "k", "width": 3},
            )

            # Mark region with data label for callbacks
            region.data_label = plot_id

            # Add to plot
            plot_widget.addItem(region)

            # Add labels with current values of lower and upper thresholds. Attach them
            # to the region to be able to access them from callbacks.
            region.low_thresh_label = pg.InfLineLabel(
                region.lines[0], fmt, position=0.95
            )
            self._change_region_label_font(region.low_thresh_label)
            region.high_thresh_label = pg.InfLineLabel(
                region.lines[1], fmt, position=0.90
            )
            self._change_region_label_font(region.high_thresh_label)

            # Connect signals
            region.sigRegionChanged.connect(self.region_pos_changed)
            region.sigRegionChangeFinished.connect(self.region_pos_changed_finished)

        # Make sure the viewbox remembers its own y range
        viewbox = plot_widget.getPlotItem().getViewBox()
        viewbox.y_min = 0.0
        viewbox.y_max = n.max()
        viewbox.sigXRangeChanged.connect(self.fix_viewbox_y_range)

        # Mark viewbox with data label for callbacks
        viewbox.data_label = plot_id

        return region

    def histogram_raise_context_menu(self, ev):
        """Create a context menu on the efo vs cfr scatter/histogram plot ROI."""
        if ev.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            reset_action = QAction("Reset default axis range")
            reset_action.triggered.connect(
                lambda checked: self.reset_default_axis_range(ev.currentItem)
            )
            menu.addAction(reset_action)
            shift_action = QAction("Move x axis origin to 0")
            shift_action.triggered.connect(
                lambda checked: self.shift_x_axis_origin_to_zero(ev.currentItem)
            )
            menu.addAction(shift_action)
            pos = ev.screenPos()
            menu.exec(QPoint(int(pos.x()), int(pos.y())))
            ev.accept()
        else:
            ev.ignore()

    def histogram_raise_context_menu_with_filtering(self, ev):
        """Create a context menu on the efo vs cfr scatter/histogram plot ROI."""
        if ev.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            ranges_action = QAction("Set ROI ranges")
            ranges_action.triggered.connect(
                lambda checked: self.roi_open_ranges_dialog(ev.currentItem.data_label)
            )
            menu.addAction(ranges_action)
            filter_action = QAction("Filter")
            filter_action.triggered.connect(
                lambda checked: self.trigger_filter_action(ev.currentItem)
            )
            menu.addAction(filter_action)
            menu.addSeparator()
            reset_action = QAction("Reset default axis range")
            reset_action.triggered.connect(
                lambda checked: self.reset_default_axis_range(ev.currentItem)
            )
            menu.addAction(reset_action)
            shift_action = QAction("Move x axis origin to 0")
            shift_action.triggered.connect(
                lambda checked: self.shift_x_axis_origin_to_zero(ev.currentItem)
            )
            menu.addAction(shift_action)
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

    def _add_median_line(self, plot, values):
        """Add median line to plot (with median +/- mad as label)."""
        _, _, med, mad = get_robust_threshold(values, 0.0)
        line = pg.InfiniteLine(
            pos=med,
            movable=False,
            angle=90,
            pen={"color": (200, 50, 50), "width": 3},
            label=f"median={med:.2f} ± {mad:.2f} nm",
            labelOpts={
                "position": 0.95,
                "color": (200, 50, 50),
                "fill": (200, 50, 50, 10),
                "movable": True,
            },
        )
        plot.addItem(line)

    def shift_x_axis_origin_to_zero(self, item):
        """Set the lower range of the x axis of the passed viewbox to 0."""
        if isinstance(item, ViewBox):
            view_box = item
        elif isinstance(item, AxisItem):
            view_box = item.getViewBox()
        else:
            return
        view_range = view_box.viewRange()
        view_box.setRange(xRange=(0.0, view_range[0][1]))

    def reset_default_axis_range(self, item):
        if isinstance(item, ViewBox):
            view_box = item
        elif isinstance(item, AxisItem):
            view_box = item.getViewBox()
        else:
            return
        if item.data_label == "efo":
            view_box.setRange(xRange=(self.state.efo_range[0], self.state.efo_range[1]))
            self.efo_range = self.state.efo_range
        elif item.data_label == "cfr":
            view_box.setRange(xRange=(self.state.cfr_range[0], self.state.cfr_range[1]))
            self.cfr_range = self.state.cfr_range
        elif item.data_label in ["sx", "sy", "sz"]:
            view_box.setRange(
                xRange=(
                    self.state.loc_precision_range[0],
                    self.state.loc_precision_range[1],
                )
            )
        else:
            pass

    def trigger_filter_action(self, item):
        """Set the lower range of the x axis of the passed viewbox to 0."""
        if isinstance(item, ViewBox):
            view_box = item
        elif isinstance(item, AxisItem):
            view_box = item.getViewBox()
        else:
            return
        plot_id = view_box.data_label
        if plot_id == "efo":
            self.run_efo_filter_and_broadcast_viewers_update()
        elif plot_id == "cfr":
            self.run_cfr_filter_and_broadcast_viewers_update()
        else:
            raise ValueError(f"Unexpected `plot_id` {plot_id}.")

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

    @Slot(None, name="roi_changes_finished")
    def roi_changes_finished(self):
        """Called when the ROIChanges dialog has accepted the changes."""

        # Signal blocker on self.efo_plot and self.cfr_plot
        cfr_plot_blocker = QSignalBlocker(self.cfr_plot)
        efo_plot_blocker = QSignalBlocker(self.efo_plot)

        # Block signals from self.efo_plot and self.cfr_plot
        cfr_plot_blocker.reblock()
        efo_plot_blocker.reblock()

        # Update the thresholds in the EFO and CFR histograms.
        self.efo_region.setRegion(self.state.efo_thresholds)
        self.cfr_region.setRegion(self.state.cfr_thresholds)

        # Unblock the self.efo_plot and self.cfr_plot signals
        cfr_plot_blocker.unblock()
        efo_plot_blocker.unblock()

    def region_pos_changed_finished(self, item):
        """Called when the line region on one of the histogram plots has changed."""
        if item.data_label not in ["efo", "cfr"]:
            raise ValueError(f"Unexpected data label {item.data_label}.")

        # Update the correct thresholds
        if item.data_label == "efo":
            self.state.efo_thresholds = item.getRegion()
            self.efo_bounds_changed.emit()
        else:
            self.state.cfr_thresholds = item.getRegion()
            self.cfr_bounds_changed.emit()

    @staticmethod
    def _change_region_label_font(region_label):
        """Change the region label font style."""
        text_item = region_label.textItem
        text_item.setDefaultTextColor(QColor("black"))
        font = text_item.font()
        font.setWeight(QFont.Bold)
        font.setPointSize(20)

    def fix_viewbox_y_range(self, viewbox, x_range_limits):
        """Reset the y axis range whenever the x range changes."""
        viewbox.setYRange(viewbox.y_min, viewbox.y_max)
        viewbox.setAutoVisible(y=True)

    def change_efo_bounds(self):
        """Update the efo bounds on the histogram (without broadcasting any events)."""

        # Signal blocker on self.efo_plot
        efo_plot_blocker = QSignalBlocker(self.efo_plot)

        # Block signals from self.efo_plot and self.cfr_plot
        efo_plot_blocker.reblock()

        # Update the thresholds in the EFO and CFR histograms.
        self.efo_region.setRegion(self.state.efo_thresholds)

        # Unblock the self.efo_plot and self.cfr_plot signals
        efo_plot_blocker.unblock()

    def change_cfr_bounds(self):
        """Update the cfr bounds on the histogram (without broadcasting any events)."""

        # Signal blocker on self.efo_plot
        cfr_plot_blocker = QSignalBlocker(self.cfr_plot)

        # Block signals from self.efo_plot and self.cfr_plot
        cfr_plot_blocker.reblock()

        # Update the thresholds in the EFO and CFR histograms.
        self.cfr_region.setRegion(self.state.cfr_thresholds)

        # Unblock the self.efo_plot and self.cfr_plot signals
        cfr_plot_blocker.unblock()
