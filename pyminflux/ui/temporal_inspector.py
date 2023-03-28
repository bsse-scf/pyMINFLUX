import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QColor, QDoubleValidator, QFont, QIntValidator
from PySide6.QtWidgets import QDialog
from sklearn.mixture import BayesianGaussianMixture

from pyminflux.analysis import prepare_histogram
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

        # Set up ui elements

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.__minfluxprocessor = processor

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Create the plot elements
        self.plot_widget = PlotWidget(parent=self, background="w", title="")

        # Plot the dcr histogram
        self.plot_selected()

        # Add them to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

        # Add connections
        self.ui.pbPlot.clicked.connect(self.plot_selected)

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """

        # Hide the "Plot Options" menu
        self.plot_widget.getPlotItem().ctrlMenu.menuAction().setVisible(False)

    @Slot(None, name="plot_selected")
    def plot_selected(self):
        """Perform and plot the results of the selected analysis."""

        # Do we have something to plot?
        if (
            self.__minfluxprocessor is None
            or self.__minfluxprocessor.full_dataframe is None
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
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)

    def plot_localizations_per_unit_time(self):
        """Plot number of localizations per unit time."""

        # @TODO: This should user-definable
        unit_step = 1
        timepoints_in_min = self.__minfluxprocessor.filtered_dataframe["tim"] / 60

        # Calculate the histogram of localizations per unit time
        n_tim, bin_edges, bin_centers, bin_width = prepare_histogram(
            timepoints_in_min,
            auto_bins=False,
            bin_size=unit_step,
            normalize=False,
        )

        # Plot the histogram
        chart = pg.BarGraphItem(
            x=bin_centers, height=n_tim, width=0.9 * bin_width, brush=self.brush
        )

        # Update the plot
        axis_range = (bin_edges[0], bin_edges[-1])
        self.plot_widget.setXRange(axis_range[0], axis_range[1])
        self.plot_widget.setYRange(0.0, n_tim.max())
        self.plot_widget.setLabel("left", text="Number of localizations per min")
        self.plot_widget.addItem(chart)

        # Create a linear region for setting filtering thresholds
        region = pg.LinearRegionItem(
            values=[axis_range[0], axis_range[1]],
            pen={"color": "k", "width": 3},
        )

        # Add to plot
        self.plot_widget.addItem(region)

        # Add labels with current values of lower and upper thresholds. Attach them
        # to the region to be able to access them from callbacks.
        region.low_thresh_label = pg.InfLineLabel(
            region.lines[0], "{value:.2f}", position=0.95
        )
        self._change_region_label_font(region.low_thresh_label)
        region.high_thresh_label = pg.InfLineLabel(
            region.lines[1], "{value:.2f}", position=0.90
        )
        self._change_region_label_font(region.high_thresh_label)

        # Connect signals
        region.sigRegionChanged.connect(self.region_pos_changed)
        region.sigRegionChangeFinished.connect(self.region_pos_changed_finished)

    def plot_localization_precision_per_unit_time(self):
        """Plot localization precision as a function of time."""
        # @TODO: Implement me!
        self.plot_widget.setLabel("left", text="Localization precision per min")

    @staticmethod
    def _change_region_label_font(region_label):
        """Change the region label font style."""
        text_item = region_label.textItem
        text_item.setDefaultTextColor(QColor("black"))
        font = text_item.font()
        font.setWeight(QFont.Bold)
        font.setPointSize(20)

    def region_pos_changed(self, item):
        """Called when the line region on one of the histogram plots is changing."""

        # # This seems to be a bug in pyqtgraph. When moving a LinearRegionItems with
        # # two InfLineLabels attached to the region boundaries (InfiniteLine), only
        # # the label of the upper bound is automatically updated.
        # region = item.getRegion()
        # low_thresh_label = item.low_thresh_label
        # if low_thresh_label.format == "{value:.2f}":
        #     value = f"{min(region):.2f}"
        # elif low_thresh_label.format == "{value:.0f}":
        #     value = f"{min(region):.0f}"
        # else:
        #     value = f"{min(region)}"
        # low_thresh_label.textItem.setPlainText(value)
        pass

    def region_pos_changed_finished(self, item):
        """Called when the line region on one of the histogram plots has changed."""
        # if item.data_label not in ["efo", "cfr"]:
        #     raise ValueError(f"Unexpected data label {item.data_label}.")
        #
        # # Update the correct thresholds
        # if item.data_label == "efo":
        #     self.state.efo_thresholds = item.getRegion()
        # else:
        #     self.state.cfr_thresholds = item.getRegion()
        pass
