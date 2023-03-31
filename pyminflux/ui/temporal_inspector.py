import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, Qt
from PySide6.QtWidgets import QDialog, QMenu

from pyminflux.state import State
from pyminflux.ui.ui_temporal_inspector import Ui_TemporalInspector


class TemporalInspector(QDialog, Ui_TemporalInspector):
    """
    A QDialog to perform temporal analysis and selection.
    """

    # Signal that the fluorophore IDs have been assigned
    fluorophore_ids_assigned = Signal(int, name="fluorophore_ids_assigned")

    def __init__(self, processor, parent):

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_TemporalInspector()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Keep a reference to the Processor
        self.minfluxprocessor = processor

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep track of the x-axis limits and the selection
        self.x_range = None
        self.selection_range = None

        # Selection region
        self.selection_region = None

        # Time resolution
        # @TODO: This should be user definable!
        self.time_resolution_sec = 60

        # Remember visibility status of the region
        self.roi_visible = True

        # Create the plot elements
        self.plot_widget = PlotWidget(parent=self, background="w", title="")

        # Plot the dcr histogram
        self.plot_selected()

        # Add them to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

        # Add connections
        self.ui.pbPlot.clicked.connect(self.plot_selected)

    @Slot(None, name="plot_selected")
    def plot_selected(self):
        """Perform and plot the results of the selected analysis."""

        # Do we have something to plot?
        if (
            self.minfluxprocessor is None
            or self.minfluxprocessor.full_dataframe is None
        ):
            return

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Get the requested plot
        if self.ui.cbAnalysisSelection.currentIndex() == 0:
            self.plot_localizations_per_unit_time()
        elif self.ui.cbAnalysisSelection.currentIndex() == 1:
            self.plot_localization_precision_per_unit_time()
        else:
            raise ValueError("Unexpected plotting request.")

        self.plot_widget.setLabel("bottom", text="time (min)")
        self.plot_widget.showAxis("bottom")
        self.plot_widget.showAxis("left")
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.getPlotItem().scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu
        )

        # Create a linear region for setting filtering thresholds. We create it
        # small enough not to be in the way.
        if self.selection_range is None:
            mn, mx = np.percentile(
                np.arange(self.x_range[0], self.x_range[1]), [25, 75]
            )
            self.selection_range = (mn, mx)
        mn, mx = self.selection_range[0], self.selection_range[1]
        self.selection_region = pg.LinearRegionItem(
            values=[mn, mx],
            pen={"color": "m", "width": 3, "alpha": 0.5},
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

        # Connect signals
        self.selection_region.sigRegionChanged.connect(self.region_pos_changed)
        self.selection_region.sigRegionChangeFinished.connect(
            self.region_pos_changed_finished
        )

    def plot_localizations_per_unit_time(self):
        """Plot number of localizations per unit time."""

        # Create `time_resolution_sec` bins starting at 0.0.
        bin_edges = np.arange(
            start=0.0,
            stop=self.minfluxprocessor.filtered_dataframe["tim"].max()
            + self.time_resolution_sec,
            step=self.time_resolution_sec,
        )
        bin_centers = bin_edges[:-1] + 0.5 * self.time_resolution_sec
        bin_width = self.time_resolution_sec

        # Calculate the histogram of localizations per unit time
        n_tim, _ = np.histogram(
            self.minfluxprocessor.filtered_dataframe["tim"].values,
            bins=bin_edges,
            density=False,
        )

        # Plot the results per minute
        time_axis = (bin_centers - 0.5 * bin_width) / self.time_resolution_sec
        time_width = time_axis[1] - time_axis[0]

        # Plot the histogram
        chart = pg.BarGraphItem(
            x=time_axis, height=n_tim, width=0.9 * time_width, brush=self.brush
        )

        # Update the plot
        if self.x_range is None:
            self.x_range = (time_axis[0], time_axis[-1])
            self.plot_widget.setXRange(self.x_range[0], self.x_range[1])
        self.plot_widget.setYRange(0.0, n_tim.max())
        self.plot_widget.setLabel("left", text="Number of localizations per min")
        self.plot_widget.addItem(chart)

    def plot_localization_precision_per_unit_time(self):
        """Plot localization precision as a function of time."""

        # Add a legend
        if self.plot_widget.plotItem.legend is None:
            self.plot_widget.plotItem.addLegend()

        # Create `time_resolution_sec` bins starting at 0.0.
        bin_edges = np.arange(
            start=0.0,
            stop=self.minfluxprocessor.filtered_dataframe["tim"].max()
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
            df = self.minfluxprocessor.select_dataframe_by_1d_range("tim", time_range)
            if len(df.index) > 0:
                stats = self.minfluxprocessor.calculate_statistics_on(df)
                x_pr[i] = stats["sx"].mean()
                y_pr[i] = stats["sy"].mean()
                z_pr[i] = stats["sz"].mean()
            else:
                x_pr[i] = 0.0
                y_pr[i] = 0.0
                z_pr[i] = 0.0

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Plot the results per minute
        time_axis = (bin_centers - 0.5 * bin_width) / self.time_resolution_sec

        # Get the max bin number for normalization (and add 10%)
        n_max = np.max([x_pr.max(), y_pr.max(), z_pr.max()])
        n_max += 0.1 * n_max

        if self.minfluxprocessor.is_3d:
            offset = bin_width / self.time_resolution_sec / 3
            bar_width = 0.9 / 3
        else:
            offset = bin_width / self.time_resolution_sec / 2
            bar_width = 0.9 / 2

        # Create the sx bar charts
        chart = pg.BarGraphItem(
            x=time_axis,
            height=x_pr,
            width=bar_width * bin_width / self.time_resolution_sec,
            brush="r",
            alpha=0.5,
            name="σx",
        )
        self.plot_widget.addItem(chart)

        # Create the sy bar charts
        chart = pg.BarGraphItem(
            x=time_axis + offset,
            height=y_pr,
            width=bar_width * bin_width / self.time_resolution_sec,
            brush="b",
            alpha=0.5,
            name="σy",
        )
        self.plot_widget.addItem(chart)

        # Create the sz bar charts if needed
        if self.minfluxprocessor.is_3d:
            chart = pg.BarGraphItem(
                x=time_axis + 2 * offset,
                height=z_pr,
                width=bar_width * bin_width / self.time_resolution_sec,
                brush="k",
                alpha=0.5,
                name="σz",
            )
            self.plot_widget.addItem(chart)

        # Update the plot
        if self.x_range is None:
            self.x_range = (time_axis[0], time_axis[-1])
            self.plot_widget.setXRange(self.x_range[0], self.x_range[-1])
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
        mn, mx = item.getRegion()
        self.selection_range = (mn, mx)

    def histogram_raise_context_menu(self, ev):
        """Create a context menu on the efo vs cfr scatter/histogram plot ROI."""
        if ev.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            keep_action = QAction("Keep data within region")
            keep_action.triggered.connect(self.keep_time_region)
            menu.addAction(keep_action)
            crop_action = QAction("Crop data within region")
            crop_action.triggered.connect(self.crop_time_region)
            menu.addAction(crop_action)
            menu.addSeparator()
            if self.roi_visible:
                text = "Hide region"
            else:
                text = "Show region"
            toggle_visibility_action = QAction(text)
            toggle_visibility_action.triggered.connect(self.toggle_region_visibility)
            menu.addAction(toggle_visibility_action)
            pos = ev.screenPos()
            menu.exec(QPoint(int(pos.x()), int(pos.y())))
            ev.accept()
        else:
            ev.ignore()

    def toggle_region_visibility(self, action):
        """Toggles the visibility of the line region."""

        if self.selection_region is None:
            return

        if self.roi_visible:
            self.selection_region.hide()
            self.roi_visible = False
        else:
            self.selection_region.show()
            self.roi_visible = True

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
        self.minfluxprocessor.filter_dataframe_by_1d_range_complement(
            "tim", (mn_s, mx_s)
        )

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
        self.minfluxprocessor.filter_dataframe_by_1d_range("tim", (mn_s, mx_s))

        # Update the plot
        self.plot_selected()
