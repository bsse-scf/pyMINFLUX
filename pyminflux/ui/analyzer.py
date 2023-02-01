from typing import Optional, Tuple

import numpy as np
import pyqtgraph as pg
from pyqtgraph import ROI, AxisItem, Point, ViewBox
from PySide6.QtCore import QPoint, QSignalBlocker, Signal, Slot
from PySide6.QtGui import QAction, QColor, QDoubleValidator, QFont, QIntValidator, Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QMenu,
    QSizePolicy,
)

from ..analysis import (
    calculate_2d_histogram,
    find_first_peak_bounds,
    get_robust_threshold,
    prepare_histogram,
    select_by_bgmm_fitting,
    select_by_gmm_fitting,
)
from ..processor import MinFluxProcessor
from ..state import State
from .roi_ranges import ROIRanges
from .ui_analyzer import Ui_Analyzer


class Analyzer(QDialog, Ui_Analyzer):

    # Signal that the data viewers should be updated
    data_filters_changed = Signal(name="data_filters_changed")
    plotting_started = Signal(name="plotting_started")
    plotting_completed = Signal(name="plotting_completed")

    def __init__(self, minfluxprocessor: MinFluxProcessor, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_Analyzer()
        self.ui.setupUi(self)

        # Store the reference to the reader
        self._minfluxprocessor = minfluxprocessor

        # Keep references to the plots
        self.efo_plot = None
        self.cfr_plot = None
        self.sx_plot = None
        self.sy_plot = None
        self.sz_plot = None
        self.cfr_efo_plot = None
        self.efo_region = None
        self.cfr_region = None
        self.efo_cfr_roi = None
        self.efo_cfr_scatter = None
        self.efo_cfr_plot_view = None

        # Keep track of whether we are plotting the EFO vs. CFR scatter plot or 2D histogram
        self.plotting_efo_cfr_scatter_plot = True
        self.efo_cfr_histogram_log_scale = False

        # Store the data aspect ratio
        self.efo_range = None
        self.cfr_range = None
        self.efo_scale = 1.0
        self.cfr_scale = 1.0
        self.efo_cfr_data_aspect_ratio = 1.0

        # Keep track of the axis ranges
        self.efo_cfr_x_range = None
        self.efo_cfr_y_range = None

        # Keep a reference to the singleton State class
        self.state = State()

        #
        # Set defaults
        #

        # EFO peak detection tab
        self.ui.checkEFOLowerThreshold.setChecked(self.state.enable_efo_lower_threshold)
        self.ui.checkEFOUpperThreshold.setChecked(self.state.enable_efo_upper_threshold)
        self.ui.leEFOMedianFilterSupport.setText(
            str(self.state.median_efo_filter_support)
        )
        self.ui.leEFOMedianFilterSupport.setValidator(QIntValidator(bottom=0))
        self.ui.leEFOMinRelativeProminence.setText(
            str(self.state.min_efo_relative_peak_prominence)
        )
        self.ui.leEFOMinRelativeProminence.setValidator(
            QDoubleValidator(bottom=0.0, top=1.0, decimals=6)
        )

        # EFO sub-population detection tab
        self.ui.leEFOGMMMaxClusters.setText(str(self.state.gmm_efo_num_clusters))
        self.ui.leEFOGMMMaxClusters.setValidator(QIntValidator(bottom=1))
        self.ui.cbEFOUseBGMM.setChecked(self.state.gmm_efo_use_bayesian)
        self.ui.cbEFOIncludeCFR.setChecked(self.state.gmm_include_cfr)

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
        self.ui.pbEFORunAutoPeakDetection.clicked.connect(self.run_efo_peak_detection)
        self.ui.checkEFOLowerThreshold.stateChanged.connect(
            self.persist_efo_lower_threshold
        )
        self.ui.checkEFOUpperThreshold.stateChanged.connect(
            self.persist_efo_upper_threshold
        )
        self.ui.pbEFORunFilter.clicked.connect(
            self.run_efo_filter_and_broadcast_viewers_update
        )
        self.ui.leEFOMedianFilterSupport.textChanged.connect(
            self.persist_median_efo_filter_support
        )
        self.ui.leEFOMinRelativeProminence.textChanged.connect(
            self.persist_min_efo_relative_peak_prominence
        )

        # EFO sub-population detection tab
        self.ui.pbEFOGMMDetect.clicked.connect(self.run_efo_gmm_detect_sub_population)
        self.ui.pbEFOGMMFilter.clicked.connect(self.run_efo_gmm_filter_sub_population)
        self.ui.leEFOGMMMaxClusters.textChanged.connect(
            self.persist_gmm_efo_num_clusters
        )
        self.ui.cbEFOUseBGMM.stateChanged.connect(self.persist_gmm_efo_use_bayesian)
        self.ui.cbEFOIncludeCFR.stateChanged.connect(self.persist_gmm_include_cfr)

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

    def update_efo_cfr_plot_type(self):
        """Toggle the efo vs. cfr plot."""

        # Set the options
        self.plotting_efo_cfr_scatter_plot = not self.plotting_efo_cfr_scatter_plot

        # Plot
        self.update_efo_cfr_plot()

    def update_efo_cfr_plot_scale(self):
        """Toggle the efo vs. cfr plot intensity scale."""

        # Set the options
        self.efo_cfr_histogram_log_scale = not self.efo_cfr_histogram_log_scale

        # Plot
        if not self.plotting_efo_cfr_scatter_plot:
            self.update_efo_cfr_plot()

    def update_efo_cfr_plot(self):
        """Update the efo_cfr plot."""

        # Create it
        if self.plotting_efo_cfr_scatter_plot:

            # Remove previous widget if it exists
            self.delete_efo_cfr_plot_widgets()

            # Now plot the scatter plot
            self.cfr_efo_plot = self._create_scatter_plot(
                x=self._minfluxprocessor.filtered_dataframe["efo"],
                y=self._minfluxprocessor.filtered_dataframe["cfr"],
                efo_axis_range=self.efo_range,
                cfr_axis_range=self.cfr_range,
                title="CFR vs. EFO",
                x_label="EFO",
                y_label="CFR",
                brush=pg.mkBrush(QColor(62, 175, 118, 128)),
                roi_color=QColor(36, 60, 253, 255),
                thresholds_efo=self.state.efo_thresholds,
                thresholds_cfr=self.state.cfr_thresholds,
            )
            self.ui.parameters_layout.addWidget(self.cfr_efo_plot)

        else:

            # Toggle plotting 2D histogram
            self.plotting_efo_cfr_scatter_plot = False

            # Remove previous widget if it exists
            self.delete_efo_cfr_plot_widgets()

            # Extract the bin edges
            _, efo_bin_edges, _, _ = prepare_histogram(
                self._minfluxprocessor.filtered_dataframe["efo"].values
            )
            _, cfr_bin_edges, _, _ = prepare_histogram(
                self._minfluxprocessor.filtered_dataframe["cfr"].values
            )

            # Not plot the 2D histogram
            self.cfr_efo_plot = self._create_2d_histogram_plot(
                x=self._minfluxprocessor.filtered_dataframe["efo"],
                y=self._minfluxprocessor.filtered_dataframe["cfr"],
                efo_bin_edges=efo_bin_edges,
                cfr_bin_edges=cfr_bin_edges,
                efo_axis_range=self.efo_range,
                cfr_axis_range=self.cfr_range,
                use_log_scale=self.efo_cfr_histogram_log_scale,
                title="CFR vs. EFO",
                x_label="EFO",
                y_label="CFR",
                roi_color=QColor(36, 60, 253, 255),
                thresholds_efo=self.state.efo_thresholds,
                thresholds_cfr=self.state.cfr_thresholds,
            )
            self.ui.parameters_layout.addWidget(self.cfr_efo_plot)

        self.cfr_efo_plot.show()

    def keyPressEvent(self, ev):
        """Key press event."""

        # Do not capture key events for now
        ev.ignore()

    def delete_efo_cfr_plot_widgets(self):
        """Checks if the scatter-plot/2D histogram plot exists in the parameters_layout
        and deletes it if it does."""

        # Are there items already?
        n_items = self.ui.parameters_layout.count()
        if n_items == 0:
            return

        # Get the last widget
        widget = self.ui.parameters_layout.itemAt(n_items - 1).widget()

        # Remove it from the layout
        self.ui.parameters_layout.removeWidget(widget)

        # Delete it
        widget.deleteLater()

        # Delete ROI
        if self.efo_cfr_roi is not None:
            self.ui.parameters_layout.removeWidget(widget)
            self.efo_cfr_roi.deleteLater()
        self.efo_cfr_roi = None

        # Now also delete the references
        self.cfr_efo_plot = None
        self.efo_cfr_scatter = None

    def calculate_efo_cfr_aspect_ratio(self, efo_bin_edges, cfr_bin_edges):

        # Ratio of the bin widths: this will make sure that the 2D histogram will
        # have properly scaled pixels.
        self.efo_scale = (efo_bin_edges[-1] - efo_bin_edges[0]) / (
            len(efo_bin_edges) - 1
        )
        self.cfr_scale = (cfr_bin_edges[-1] - cfr_bin_edges[0]) / (
            len(cfr_bin_edges) - 1
        )
        self.efo_cfr_data_aspect_ratio = self.cfr_scale / self.efo_scale

        # Store default x and y ranges for EFO and CFR
        self.efo_range = (efo_bin_edges[0], efo_bin_edges[-1])
        self.cfr_range = (cfr_bin_edges[0], cfr_bin_edges[-1])

    @Slot(name="run_efo_gmm_detect_sub_population")
    def run_efo_gmm_detect_sub_population(self):
        """Run EFO (B)GMM-based sub-population detection."""

        # Get the data
        if self.state.gmm_include_cfr:
            efo = self._minfluxprocessor.filtered_dataframe[["efo", "cfr"]].values
        else:
            efo = self._minfluxprocessor.filtered_dataframe["efo"].values
        if len(efo) == 0:
            return

        # Is there data already plotted
        if self.efo_cfr_scatter is None:
            return

        if self.state.gmm_efo_use_bayesian:
            sel, labels, means = select_by_bgmm_fitting(
                efo, num_test_components=self.state.gmm_efo_num_clusters
            )
        else:
            sel, labels, means = select_by_gmm_fitting(
                efo, num_test_components=self.state.gmm_efo_num_clusters
            )

        # Make sure we have a scatter plot to update
        if not self.plotting_efo_cfr_scatter_plot:
            self.plotting_efo_cfr_scatter_plot = True
            self.update_efo_cfr_plot()

        # Create brushes lookup table
        brushes_table = [
            pg.mkBrush(QColor(0, 0, 0, 128)),
            pg.mkBrush(QColor(62, 175, 118, 128)),
        ]
        brushes = [brushes_table[int(i)] for i in sel]

        # Apply brushes (set color of non-selected values to black)
        self.efo_cfr_scatter.setBrush(brushes)

    @Slot(name="run_efo_gmm_filter_sub_population")
    def run_efo_gmm_filter_sub_population(self):
        """Run EFO (B)GMM-based sub-population detection and filtering."""

        # Get the data
        if self.state.gmm_include_cfr:
            efo = self._minfluxprocessor.filtered_dataframe[["efo", "cfr"]].values
        else:
            efo = self._minfluxprocessor.filtered_dataframe["efo"].values
        if len(efo) == 0:
            return

        # Is there data already plotted
        if self.efo_cfr_scatter is None:
            return

        if self.state.gmm_efo_use_bayesian:
            sel, labels, means = select_by_bgmm_fitting(
                efo, num_test_components=self.state.gmm_efo_num_clusters
            )
        else:
            sel, labels, means = select_by_gmm_fitting(
                efo, num_test_components=self.state.gmm_efo_num_clusters
            )

        # Filter the data by the selected indices
        self._minfluxprocessor.apply_filter_by_indices(sel)

        # Update the EFO thresholds
        self.state.efo_thresholds = (
            self.state.efo_thresholds[0],
            self._minfluxprocessor.filtered_dataframe["efo"].max(),
        )

        # Update plot
        self.efo_region.setRegion(self.state.efo_thresholds)

        # Update the histograms
        self.plot()

        # Signal that the external viewers should be updated
        self.data_filters_changed.emit()

    @Slot(name="run_efo_peak_detection")
    def run_efo_peak_detection(self):
        """Run EFO peak detection."""

        # Is there something to calculate?
        if (
            not self.state.enable_efo_lower_threshold
            and not self.state.enable_efo_upper_threshold
        ):
            print("Both lower and upper EFO thresholds are disabled.")
            return

        # Initialize values
        if self.state.efo_thresholds is None:
            min_efo = self._minfluxprocessor.filtered_dataframe["efo"].values.min()
            max_efo = self._minfluxprocessor.filtered_dataframe["efo"].values.max()
        else:
            min_efo = self.state.efo_thresholds[0]
            max_efo = self.state.efo_thresholds[1]

        # Calculate thresholds for EFO
        n_efo, _, b_efo, _ = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["efo"].values
        )
        lower_thresh_efo, upper_thresh_efo = find_first_peak_bounds(
            counts=n_efo,
            bins=b_efo,
            min_rel_prominence=self.state.min_efo_relative_peak_prominence,
            med_filter_support=self.state.median_efo_filter_support,
        )
        if self.state.enable_efo_lower_threshold:
            min_efo = lower_thresh_efo
        if self.state.enable_efo_upper_threshold:
            max_efo = upper_thresh_efo
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

    @Slot(int, name="persist_gmm_efo_use_bayesian")
    def persist_gmm_efo_use_bayesian(self, state):
        self.state.gmm_efo_use_bayesian = state != 0

    @Slot(int, name="persist_gmm_include_cfr")
    def persist_gmm_include_cfr(self, state):
        self.state.gmm_include_cfr = state != 0

    @Slot(int, name="persist_cfr_lower_threshold")
    def persist_cfr_lower_threshold(self, state):
        self.state.enable_cfr_lower_threshold = state != 0

    @Slot(int, name="persist_cfr_upper_threshold")
    def persist_cfr_upper_threshold(self, state):
        self.state.enable_cfr_upper_threshold = state != 0

    @Slot(int, name="persist_efo_lower_threshold")
    def persist_efo_lower_threshold(self, state):
        self.state.enable_efo_lower_threshold = state != 0

    @Slot(int, name="persist_efo_upper_threshold")
    def persist_efo_upper_threshold(self, state):
        self.state.enable_efo_upper_threshold = state != 0

    @Slot(str, name="persist_gmm_efo_num_clusters")
    def persist_gmm_efo_num_clusters(self, text):
        try:
            persist_gmm_efo_num_clusters = int(text)
        except ValueError as _:
            return
        self.state.gmm_efo_num_clusters = persist_gmm_efo_num_clusters

    @Slot(str, name="persist_median_efo_filter_support")
    def persist_median_efo_filter_support(self, text):
        try:
            median_efo_filter_support = int(text)
        except ValueError as _:
            return
        self.state.median_efo_filter_support = median_efo_filter_support

    @Slot(str, name="persist_min_efo_relative_peak_prominence")
    def persist_min_efo_relative_peak_prominence(self, text):
        try:
            min_efo_relative_peak_prominence = float(text)
        except ValueError as _:
            return
        self.state.min_efo_relative_peak_prominence = min_efo_relative_peak_prominence

    @Slot(str, name="persist_cfr_threshold_factor")
    def persist_cfr_threshold_factor(self, text):
        try:
            cfr_threshold_factor = float(text)
        except ValueError as _:
            return
        self.state.cfr_threshold_factor = cfr_threshold_factor

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
            self._minfluxprocessor.apply_range_filter(
                "efo", self.state.efo_thresholds[0], self.state.efo_thresholds[1]
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
            self._minfluxprocessor.apply_range_filter(
                "cfr", self.state.cfr_thresholds[0], self.state.cfr_thresholds[1]
            )

        # Update the histograms
        self.plot()

        # Signal that the external viewers should be updated
        self.data_filters_changed.emit()

    @Slot(name="disable_buttons")
    def disable_buttons(self):
        self.ui.pbReset.setEnabled(False)
        self.ui.pbEFORunAutoPeakDetection.setEnabled(False)
        self.ui.pbEFOGMMDetect.setEnabled(False)
        self.ui.pbEFOGMMFilter.setEnabled(False)
        self.ui.pbCFRRunAutoThreshold.setEnabled(False)
        self.ui.pbEFORunFilter.setEnabled(False)
        self.ui.pbCFRRunFilter.setEnabled(False)

    @Slot(name="enable_buttons")
    def enable_buttons(self):
        self.ui.pbReset.setEnabled(True)
        self.ui.pbEFORunAutoPeakDetection.setEnabled(True)
        self.ui.pbEFOGMMDetect.setEnabled(True)
        self.ui.pbEFOGMMFilter.setEnabled(True)
        self.ui.pbCFRRunAutoThreshold.setEnabled(True)
        self.ui.pbEFORunFilter.setEnabled(True)
        self.ui.pbCFRRunFilter.setEnabled(True)

    def plot(self):
        """Plot histograms."""

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

        # Remove previous plots quickly, if they exist
        param_widgets = []
        for i in reversed(range(self.ui.parameters_layout.count())):
            widget = self.ui.parameters_layout.itemAt(i).widget()
            param_widgets.append(widget)
            self.ui.parameters_layout.removeWidget(widget)

        localization_widgets = []
        for i in reversed(range(self.ui.localizations_layout.count())):
            widget = self.ui.localizations_layout.itemAt(i).widget()
            localization_widgets.append(widget)
            self.ui.localizations_layout.removeWidget(widget)

        # Now properly delete them (slow)
        for widget in param_widgets:
            widget.deleteLater()

        for widget in localization_widgets:
            widget.deleteLater()

        # Is there data to plot?
        if not is_data:
            label = QLabel("Sorry, no data.")
            font = label.font()
            font.setPointSize(16)
            label.setFont(font)
            self.ui.parameters_layout.addWidget(label)
            self.plotting_completed.emit()
            return

        # Calculate the proper aspect ratio and view ranges for the relevant plots
        n_efo, efo_bin_edges, efo_bin_centers, efo_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["efo"].values
        )
        n_cfr, cfr_bin_edges, cfr_bin_centers, cfr_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["cfr"].values
        )
        self.calculate_efo_cfr_aspect_ratio(efo_bin_edges, cfr_bin_edges)

        #
        # Get "efo" and "cfr" measurements, and "sx", "sy" and "sz" localization jitter
        #

        # "efo"
        if self.state.efo_thresholds is None:
            self.state.efo_thresholds = (efo_bin_edges[0], efo_bin_edges[-1])

        self.efo_plot, self.efo_region = self._create_histogram_plot(
            n_efo,
            efo_bin_edges,
            efo_bin_centers,
            efo_bin_width,
            axis_range=self.efo_range,
            title="EFO",
            brush="b",
            fmt="{value:.0f}",
            support_thresholding=True,
            thresholds=self.state.efo_thresholds,
        )
        self.ui.parameters_layout.addWidget(self.efo_plot)
        self.efo_plot.show()

        # cfr
        if self.state.cfr_thresholds is None:
            self.state.cfr_thresholds = (cfr_bin_edges[0], cfr_bin_edges[-1])

        self.cfr_plot, self.cfr_region = self._create_histogram_plot(
            n_cfr,
            cfr_bin_edges,
            cfr_bin_centers,
            cfr_bin_width,
            axis_range=self.cfr_range,
            title="CFR",
            brush="r",
            fmt="{value:.2f}",
            support_thresholding=True,
            thresholds=self.state.cfr_thresholds,
            force_min_x_range_to_zero=False,
        )
        self.ui.parameters_layout.addWidget(self.cfr_plot)
        self.cfr_plot.show()

        # cfr vs. efo
        if self.plotting_efo_cfr_scatter_plot:
            self.cfr_efo_plot = self._create_scatter_plot(
                x=self._minfluxprocessor.filtered_dataframe["efo"],
                y=self._minfluxprocessor.filtered_dataframe["cfr"],
                efo_axis_range=self.efo_range,
                cfr_axis_range=self.cfr_range,
                title="CFR vs. EFO",
                x_label="EFO",
                y_label="CFR",
                brush=pg.mkBrush(QColor(62, 175, 118, 128)),
                roi_color=QColor(36, 60, 253, 255),
                thresholds_efo=self.state.efo_thresholds,
                thresholds_cfr=self.state.cfr_thresholds,
            )
        else:
            self.cfr_efo_plot = self._create_2d_histogram_plot(
                x=self._minfluxprocessor.filtered_dataframe["efo"],
                y=self._minfluxprocessor.filtered_dataframe["cfr"],
                efo_bin_edges=efo_bin_edges,
                cfr_bin_edges=cfr_bin_edges,
                efo_axis_range=self.efo_range,
                cfr_axis_range=self.cfr_range,
                use_log_scale=self.efo_cfr_histogram_log_scale,
                title="CFR vs. EFO",
                x_label="EFO",
                y_label="CFR",
                roi_color=QColor(36, 60, 253, 255),
                thresholds_efo=self.state.efo_thresholds,
                thresholds_cfr=self.state.cfr_thresholds,
            )
        self.ui.parameters_layout.addWidget(self.cfr_efo_plot)
        self.cfr_efo_plot.show()

        # sx
        n_sx, sx_bin_edges, sx_bin_centers, sx_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe_stats["sx"].values
        )
        self.sx_plot, _ = self._create_histogram_plot(
            n_sx,
            sx_bin_edges,
            sx_bin_centers,
            sx_bin_width,
            title="σx",
            brush="k",
            support_thresholding=False,
        )
        self._add_median_line(
            self.sx_plot, self._minfluxprocessor.filtered_dataframe_stats["sx"].values
        )
        self.ui.localizations_layout.addWidget(self.sx_plot)
        self.sx_plot.show()

        # sy
        n_sy, sy_bin_edges, sy_bin_centers, sy_bin_width = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe_stats["sy"].values
        )
        self.sy_plot, _ = self._create_histogram_plot(
            n_sy,
            sy_bin_edges,
            sy_bin_centers,
            sy_bin_width,
            title="σy",
            brush="k",
            support_thresholding=False,
        )
        self._add_median_line(
            self.sy_plot, self._minfluxprocessor.filtered_dataframe_stats["sy"].values
        )
        self.ui.localizations_layout.addWidget(self.sy_plot)
        self.sy_plot.show()

        # sz
        if self._minfluxprocessor.is_3d:
            n_sz, sz_bin_edges, sz_bin_centers, sz_bin_width = prepare_histogram(
                self._minfluxprocessor.filtered_dataframe_stats["sz"].values
            )
            self.sz_plot, _ = self._create_histogram_plot(
                n_sz,
                sz_bin_edges,
                sz_bin_centers,
                sz_bin_width,
                title="σz",
                brush="k",
                support_thresholding=False,
            )
            self._add_median_line(
                self.sz_plot,
                self._minfluxprocessor.filtered_dataframe_stats["sz"].values,
            )
            self.ui.localizations_layout.addWidget(self.sz_plot)
            self.sz_plot.show()

        # Announce that the plotting has completed
        self.plotting_completed.emit()

    def _create_histogram_plot(
        self,
        n: np.ndarray,
        bin_edges: np.ndarray,
        bin_centers: np.ndarray,
        bin_width: np.ndarray,
        *,
        axis_range: Optional[tuple] = None,
        title: str = "",
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
        plot = pg.PlotWidget(parent=self, background="w", title=title)
        plot.setMouseEnabled(x=True, y=False)

        if axis_range is None:
            axis_range = (bin_edges[0], bin_edges[-1])

        # Range values
        if force_min_x_range_to_zero:
            x0 = 0.0
        else:
            x0 = axis_range[0]
        plot.setXRange(x0, axis_range[1])  # setXRange()'s padding misbehaves
        plot.setYRange(0.0, n.max())
        plot.setMenuEnabled(False)
        plot.scene().sigMouseClicked.connect(self.histogram_raise_context_menu)
        plot.addItem(chart)

        region = None
        if support_thresholding:

            # Create a linear region for setting filtering thresholds
            region = pg.LinearRegionItem(
                values=[thresholds[0], thresholds[1]],
                pen={"color": "k", "width": 3},
            )

            # Mark region with data label for callbacks
            region.data_label = title.lower().replace(" ", "_")

            # Add to plot
            plot.addItem(region)

            # Add labels with current values of lower and upper thresholds
            low_thresh_label = pg.InfLineLabel(region.lines[0], fmt, position=0.95)
            self._change_region_label_font(low_thresh_label)
            high_thresh_label = pg.InfLineLabel(region.lines[1], fmt, position=0.95)
            self._change_region_label_font(high_thresh_label)

            # Connect signals
            region.sigRegionChanged.connect(self.region_pos_changed)
            region.sigRegionChangeFinished.connect(self.region_pos_changed_finished)

        # Make sure the viewbox remembers its own y range
        viewbox = plot.getPlotItem().getViewBox()
        viewbox.y_min = 0.0
        viewbox.y_max = n.max()
        viewbox.sigXRangeChanged.connect(self.fix_viewbox_y_range)

        return plot, region

    def _create_2d_histogram_plot(
        self,
        x: np.ndarray,
        y: np.ndarray,
        efo_bin_edges: np.ndarray,
        cfr_bin_edges: np.ndarray,
        *,
        efo_axis_range: Optional[tuple] = None,
        cfr_axis_range: Optional[tuple] = None,
        use_log_scale: bool = False,
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        roi_color: str = "r",
        thresholds_efo: tuple = None,
        thresholds_cfr: tuple = None,
    ):
        # Create 2D histogram plot
        density = calculate_2d_histogram(x, y, efo_bin_edges, cfr_bin_edges)[0]

        # Apply log scale to the intensities?
        if use_log_scale:
            density = np.log10(1.0 + density)

        # Create plot
        self.efo_cfr_scatter = pg.PlotItem(
            labels={"bottom": x_label, "left": y_label}, title=title
        )
        self.efo_cfr_scatter.setMenuEnabled(False)

        # Create an ImageView
        view = pg.ImageView(view=self.efo_cfr_scatter)
        view.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        cm = pg.colormap.get("viridis")
        view.setColorMap(cm)
        view.ui.histogram.hide()
        view.ui.roiBtn.hide()
        view.ui.menuBtn.hide()
        view.setImage(
            density,
            pos=[efo_bin_edges[0], cfr_bin_edges[0]],
            scale=[self.efo_scale, self.cfr_scale],
        )
        self.efo_cfr_scatter.setAspectLocked(True, ratio=self.efo_cfr_data_aspect_ratio)
        self.efo_cfr_scatter.invertY(False)

        # Add ROI with thresholds
        if thresholds_efo is not None and thresholds_cfr is not None:
            self.efo_cfr_roi = ROI(
                pos=Point(thresholds_efo[0], thresholds_cfr[0]),
                size=Point(
                    thresholds_efo[1] - thresholds_efo[0],
                    thresholds_cfr[1] - thresholds_cfr[0],
                ),
                parent=self.efo_cfr_scatter,
                pen={"color": roi_color, "width": 3},
                hoverPen={"color": roi_color, "width": 5},
                movable=True,
                rotatable=False,
                resizable=True,
                removable=False,
            )
            self.efo_cfr_roi.setAcceptedMouseButtons(Qt.MouseButton.RightButton)
            self.efo_cfr_roi.sigClicked.connect(self.roi_mouse_click_event)
            self.efo_cfr_roi.sigRegionChanged.connect(self.roi_changed)
            self.efo_cfr_roi.sigRegionChangeFinished.connect(self.roi_changed_finished)
            view.getView().addItem(self.efo_cfr_roi)

        # Set the efo axis range
        if efo_axis_range is None:
            efo_axis_range = (efo_bin_edges[0], efo_bin_edges[-1])
        view.getView().setXRange(min=efo_axis_range[0], max=efo_axis_range[1])

        # Set the cfr axis range
        if cfr_axis_range is None:
            cfr_axis_range = (cfr_bin_edges[0], cfr_bin_edges[-1])
        view.getView().setYRange(min=cfr_axis_range[0], max=cfr_axis_range[1])

        # Add context menu
        view.scene.sigMouseClicked.connect(self.efo_cfr_plot_click_event)

        # Keep a reference to the view
        self.efo_cfr_plot_view = view.getView().getViewBox()

        # Keep track of manual changes of the view
        self.efo_cfr_plot_view.sigRangeChangedManually.connect(
            self.efo_cfr_plot_store_view_ranges
        )

        return view

    def _create_scatter_plot(
        self,
        x: np.ndarray,
        y: np.ndarray,
        *,
        efo_axis_range: Optional[tuple] = None,
        cfr_axis_range: Optional[tuple] = None,
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        brush: str = "b",
        roi_color: str = "r",
        thresholds_efo: tuple = None,
        thresholds_cfr: tuple = None,
    ):
        """Create a scatter plot and return it to be added to the layout."""
        plot = pg.PlotWidget(parent=self, background="w", title=title)
        plot.setLabel("bottom", text=x_label)
        plot.setLabel("left", text=y_label)
        plot.setMouseEnabled(x=True, y=True)
        plot.setMenuEnabled(False)

        # Fix plot ratio
        plot.getPlotItem().getViewBox().setAspectLocked(
            lock=True, ratio=self.efo_cfr_data_aspect_ratio
        )

        # Create scatter plot
        self.efo_cfr_scatter = pg.ScatterPlotItem(
            size=3,
            pen=None,
            brush=brush,
            hoverable=False,
        )
        self.efo_cfr_scatter.setData(x=x, y=y)
        plot.addItem(self.efo_cfr_scatter)
        plot.showAxis("bottom")
        plot.showAxis("left")

        # Add ROI with thresholds
        if thresholds_efo is not None and thresholds_cfr is not None:
            self.efo_cfr_roi = ROI(
                pos=Point(thresholds_efo[0], thresholds_cfr[0]),
                size=Point(
                    thresholds_efo[1] - thresholds_efo[0],
                    thresholds_cfr[1] - thresholds_cfr[0],
                ),
                parent=self.efo_cfr_scatter,
                pen={"color": roi_color, "width": 3},
                hoverPen={"color": roi_color, "width": 5},
                movable=True,
                rotatable=False,
                resizable=True,
                removable=False,
            )
            self.efo_cfr_roi.setAcceptedMouseButtons(Qt.MouseButton.RightButton)
            self.efo_cfr_roi.sigClicked.connect(self.roi_mouse_click_event)
            self.efo_cfr_roi.sigRegionChanged.connect(self.roi_changed)
            self.efo_cfr_roi.sigRegionChangeFinished.connect(self.roi_changed_finished)

        # Set the efo axis range
        if efo_axis_range is None:
            efo_axis_range = (x.min(), x.max())
        plot.getPlotItem().getViewBox().setXRange(
            min=efo_axis_range[0], max=efo_axis_range[1]
        )

        # Set the cfr axis range
        if cfr_axis_range is None:
            cfr_axis_range = (y.min(), y.max())
        plot.getPlotItem().getViewBox().setYRange(
            min=cfr_axis_range[0], max=cfr_axis_range[1]
        )

        # Add context menu
        plot.scene().sigMouseClicked.connect(self.efo_cfr_plot_click_event)

        # Keep a reference to the view
        self.efo_cfr_plot_view = plot.getPlotItem().getViewBox()

        # Keep track of manual changes of the view
        self.efo_cfr_plot_view.sigRangeChangedManually.connect(
            self.efo_cfr_plot_store_view_ranges
        )

        return plot

    def efo_cfr_plot_store_view_ranges(self):
        """Keep track of the X and Y ranges of the efo_cfr_plot viewbox after manual change."""
        view_range = self.efo_cfr_plot_view.viewRange()
        self.efo_range = view_range[0]
        self.cfr_range = view_range[1]

    def histogram_raise_context_menu(self, ev):
        """Create a context menu on the efo vs cfr scatter/histogram plot ROI."""
        if ev.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
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

    def roi_mouse_click_event(self, roi, ev):
        """Right-click event on the efo vs cfr scatter/histogram plot ROI."""
        if ev.button() == Qt.MouseButton.RightButton and self.efo_cfr_roi.isMoving:
            # Make sure the ROI is not moving
            self.efo_cfr_roi.isMoving = False
            self.efo_cfr_roi.movePoint(self.efo_cfr_roi.startPos, finish=True)
            ev.accept()
        elif self.efo_cfr_roi.acceptedMouseButtons() & ev.button():
            ev.accept()
            if ev.button() == Qt.MouseButton.RightButton:
                self.roi_raise_context_menu(ev)
        else:
            ev.ignore()

    def efo_cfr_plot_click_event(self, ev):
        if ev.accepted:
            "This propagated from the ROI mouse event."
            return

        """Right-click event on the efo vs. cfr scatter/histogram plot."""
        if ev.button() == Qt.MouseButton.RightButton:
            ev.accept()
            self.efo_cfr_plot_raise_context_menu(ev)
        else:
            ev.ignore()

    def roi_raise_context_menu(self, ev):
        """Create a context menu on the efo vs. cfr scatter/histogram plot ROI."""
        # Open context menu
        menu = QMenu()
        ranges_action = QAction("Set ROI ranges")
        ranges_action.triggered.connect(self.roi_open_ranges_dialog)
        menu.addAction(ranges_action)
        pos = ev.screenPos()
        menu.exec(QPoint(int(pos.x()), int(pos.y())))

    def efo_cfr_plot_raise_context_menu(self, ev):
        """Create a context menu on the efo vs cfr scatterplot ROI."""
        # Open context menu
        menu = QMenu()
        if self.plotting_efo_cfr_scatter_plot:
            toggle_plot_type_action = QAction("Change to 2D histogram")
        else:
            toggle_plot_type_action = QAction("Change to scatter plot")
        toggle_plot_type_action.triggered.connect(self.update_efo_cfr_plot_type)
        menu.addAction(toggle_plot_type_action)
        if not self.plotting_efo_cfr_scatter_plot:
            menu.addSeparator()
            if self.efo_cfr_histogram_log_scale:
                toggle_intensity_scale_action = QAction("Switch to linear scale")
            else:
                toggle_intensity_scale_action = QAction("Switch to logarithmic scale")
            toggle_intensity_scale_action.triggered.connect(
                self.update_efo_cfr_plot_scale
            )
            menu.addAction(toggle_intensity_scale_action)
        pos = ev.screenPos()
        menu.exec(QPoint(int(pos.x()), int(pos.y())))

    def roi_open_ranges_dialog(self, item):
        """Open dialog to manually set the filter ranges"""
        if self.roi_ranges_dialog is None:
            self.roi_ranges_dialog = ROIRanges()
            self.roi_ranges_dialog.data_ranges_changed.connect(
                self.roi_changes_finished
            )
        else:
            self.roi_ranges_dialog.update_fields()
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

    def region_pos_changed(self, item):
        """Called when the line region on one of the histogram plots is changing."""
        pass

    @Slot(None, name="roi_changes_finished")
    def roi_changes_finished(self):
        """Called when the ROIChanges dialog has accepted the changes."""

        # Signal blocker on self.efo_plot and self.cfr_plot
        cfr_plot_blocker = QSignalBlocker(self.cfr_plot)
        efo_plot_blocker = QSignalBlocker(self.efo_plot)

        # Block signals from self.efo_plot and self.cfr_plot
        cfr_plot_blocker.reblock()
        efo_plot_blocker.reblock()

        # Update the thresholds in the EFO and CFR histograms. This will automatically
        # update the ROI, that won't need to change and will not trigger another update.
        self.efo_region.setRegion(self.state.efo_thresholds)
        self.cfr_region.setRegion(self.state.cfr_thresholds)

        # Unblock the self.efo_cfr_roi, self.efo_plot and self.cfr_plot signals
        cfr_plot_blocker.unblock()
        efo_plot_blocker.unblock()

    def region_pos_changed_finished(self, item):
        """Called when the line region on one of the histogram plots has changed."""
        if item.data_label not in ["efo", "cfr"]:
            raise ValueError(f"Unexpected data label {item.data_label}.")

        # Signal blocker on self.efo_cfr_roi
        efo_cfr_roi_blocker = QSignalBlocker(self.efo_cfr_roi)

        # Block signals from efo_cfr_roi
        efo_cfr_roi_blocker.reblock()

        # Update the correct thresholds
        if item.data_label == "efo":
            self.state.efo_thresholds = item.getRegion()
        else:
            self.state.cfr_thresholds = item.getRegion()

        # Update the ROI in the scatter plot without emitting signals
        self.update_efo_cfr_roi()

        # Unblock the efo_cfr_roi signals
        efo_cfr_roi_blocker.unblock()

    def roi_changed(self, item):
        """Called when the line region on one of the histogram plots has changed."""
        pass

    def roi_changed_finished(self, item):
        """Called when the ROI in the scatter plot has changed."""
        pos = self.efo_cfr_roi.pos()
        size = self.efo_cfr_roi.size()
        self.state.efo_thresholds = (pos[0], pos[0] + size[0])
        self.state.cfr_thresholds = (pos[1], pos[1] + size[1])

        # Update plot
        self.efo_region.setRegion(self.state.efo_thresholds)
        self.cfr_region.setRegion(self.state.cfr_thresholds)

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

    def update_efo_cfr_roi(self):
        """Update the efo_cfr roi with to match current threshold values."""
        if self.state.efo_thresholds is None or self.state.cfr_thresholds is None:
            return
        if self.efo_cfr_roi is None:
            return
        self.efo_cfr_roi.setPos(
            Point(self.state.efo_thresholds[0], self.state.cfr_thresholds[0])
        )
        self.efo_cfr_roi.setSize(
            Point(
                self.state.efo_thresholds[1] - self.state.efo_thresholds[0],
                self.state.cfr_thresholds[1] - self.state.cfr_thresholds[0],
            )
        )
