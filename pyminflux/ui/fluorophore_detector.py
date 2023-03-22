import pyqtgraph as pg
from pyqtgraph import PlotWidget, ViewBox
from PySide6.QtCore import Slot
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QComboBox, QDialog

from pyminflux.analysis import prepare_histogram
from pyminflux.reader import MinFluxReader
from pyminflux.state import State
from pyminflux.ui.ui_fluorophore_detector import Ui_FluorophoreDetector


class FluorophoreDetector(QDialog, Ui_FluorophoreDetector):
    """
    A QDialog to display the dcr histogram and to assigning the fluorophore ids.
    """

    def __init__(self, processor, parent):

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_FluorophoreDetector()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Set up ui elements
        self.ui.pbAssign.setEnabled(False)
        self.ui.leNumFluorophores.setValidator(QIntValidator(bottom=1))
        self.ui.leNumFluorophores.setText(str(self.state.num_fluorophores))
        self.ui.leNumFluorophores.textChanged.connect(self.persist_num_fluorophores)
        self.ui.leBinSize.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leBinSize.setText(str(self.state.dcr_bin_size))
        self.ui.leBinSize.textChanged.connect(self.persist_dcr_bin_size)
        self.ui.leBinSize.editingFinished.connect(self.plot_dcr_histogram)

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.__minfluxprocessor = processor

        # Create the plot elements
        self.plot_widget = PlotWidget(parent=self, background="w", title="dcr")
        self.chart = None

        # Plot the dcr histogram
        self.plot_dcr_histogram()

        # Add them to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

        # Add connections
        self.ui.pbDetect.clicked.connect(self.detect_fluorophores)

    def customize_context_menu(self):
        """Remove some default context menu actions.

        See: https://stackoverflow.com/questions/44402399/how-to-disable-the-default-context-menu-of-pyqtgraph#44420152
        """

        # Hide the "Plot Options" menu
        self.plot_widget.getPlotItem().ctrlMenu.menuAction().setVisible(False)

    @Slot(str, name="persist_dcr_bin_size")
    def persist_dcr_bin_size(self, text):
        try:
            dcr_bin_size = float(text)
        except ValueError as _:
            return
        self.state.dcr_bin_size = dcr_bin_size

    @Slot(str, name="persist_num_fluorophores")
    def persist_num_fluorophores(self, text):
        try:
            num_fluorophores = int(text)
        except ValueError as _:
            return
        self.state.num_fluorophores = num_fluorophores

    @Slot(None, name="plot_dcr_histogram")
    def plot_dcr_histogram(self):
        """Plot the dcr histogram."""

        # Do we have something to plot?
        if self.__minfluxprocessor is None or self.__minfluxprocessor.num_values == 0:
            return

        if self.state.dcr_bin_size == 0:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.__minfluxprocessor.filtered_dataframe["dcr"].values,
                auto_bins=True,
            )
        else:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.__minfluxprocessor.filtered_dataframe["dcr"].values,
                auto_bins=False,
                bin_size=self.state.dcr_bin_size,
            )

        # Update the plot title
        self.plot_widget.setTitle(f"dcr (bin size = {dcr_bin_width:.4f})")

        # It a chart already exists, remove it
        if self.chart is not None:
            self.plot_widget.removeItem(self.chart)
            self.chart.deleteLater()
            self.chart = None

        # Create the bar chart
        self.chart = pg.BarGraphItem(
            x=dcr_bin_centers, height=n_dcr, width=0.9 * dcr_bin_width, brush=self.brush
        )
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setXRange(dcr_bin_centers[0], dcr_bin_centers[-1])
        self.plot_widget.setYRange(0.0, n_dcr.max())
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.addItem(self.chart)

    @Slot(None, name="detect_fluorophores")
    def detect_fluorophores(self):
        """Detect fluorophores."""
        pass
