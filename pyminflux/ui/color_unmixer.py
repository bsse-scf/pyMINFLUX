import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QDialog
from sklearn.mixture import BayesianGaussianMixture

from pyminflux.analysis import prepare_histogram
from pyminflux.state import State
from pyminflux.ui.ui_color_unmixer import Ui_ColorUnmixer


class ColorUnmixer(QDialog, Ui_ColorUnmixer):
    """
    A QDialog to display the dcr histogram and to assigning the fluorophore ids.
    """

    # Signal that the fluorophore IDs have been assigned
    fluorophore_ids_assigned = Signal(int, name="fluorophore_ids_assigned")

    def __init__(self, processor, parent):

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_ColorUnmixer()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Set up ui elements
        self.ui.pbAssign.setEnabled(False)
        self.ui.leNumFluorophores.setValidator(QIntValidator(bottom=1))
        self.ui.leNumFluorophores.setText(str(self.state.num_fluorophores))
        self.ui.leBinSize.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leBinSize.setText(str(self.state.dcr_bin_size))

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.__minfluxprocessor = processor

        # Keep track of the global data range and step
        self.n_dcr_max = None
        self.dcr_bin_edges = None
        self.dcr_bin_centers = None
        self.dcr_bin_width = None

        # Keep track of the fluorophore ID assignments
        self.assigned_fluorophore_ids = None

        # Create the plot elements
        self.plot_widget = PlotWidget(parent=self, background="w", title="dcr")

        # Plot the dcr histogram
        self.plot_dcr_histogram()

        # Add them to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

        # Add connections
        self.ui.leNumFluorophores.textChanged.connect(self.persist_num_fluorophores)
        self.ui.leBinSize.textChanged.connect(self.persist_dcr_bin_size)
        self.ui.leBinSize.editingFinished.connect(self.plot_dcr_histogram)
        self.ui.pbDetect.clicked.connect(self.detect_fluorophores)
        self.ui.pbAssign.clicked.connect(self.assign_fluorophores_ids)

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
            if num_fluorophores < 1:
                num_fluorophores = 1
            self.ui.leNumFluorophores.setText(str(num_fluorophores))
        except ValueError as _:
            return
        self.state.num_fluorophores = num_fluorophores
        self.ui.pbAssign.setEnabled(False)

    @Slot(None, name="plot_dcr_histogram")
    def plot_dcr_histogram(self):
        """Plot the dcr histogram. This is always performed assuming all data belongs to one fluorophore."""

        # Do we have something to plot?
        if (
            self.__minfluxprocessor is None
            or self.__minfluxprocessor.full_dataframe is None
        ):
            return

        if self.state.dcr_bin_size == 0:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.__minfluxprocessor.full_dataframe["dcr"].values,
                auto_bins=True,
            )
        else:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.__minfluxprocessor.full_dataframe["dcr"].values,
                auto_bins=False,
                bin_size=self.state.dcr_bin_size,
            )

        # Remember the global histogram range and step
        self.n_dcr_max = n_dcr.max()
        self.dcr_bin_edges = dcr_bin_edges
        self.dcr_bin_centers = dcr_bin_centers
        self.dcr_bin_width = dcr_bin_width

        # Update the state and the ui element
        self.state.dcr_bin_size = self.dcr_bin_width
        self.ui.leBinSize.setText(f"{self.dcr_bin_width:.5f}")

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Create the bar chart
        chart = pg.BarGraphItem(
            x=self.dcr_bin_centers,
            height=n_dcr,
            width=0.9 * self.dcr_bin_width,
            brush=self.brush,
        )
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setXRange(self.dcr_bin_centers[0], self.dcr_bin_centers[-1])
        self.plot_widget.setYRange(0.0, self.n_dcr_max)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.addItem(chart)

    @Slot(None, name="detect_fluorophores")
    def detect_fluorophores(self):
        """Detect fluorophores."""

        # Get the data
        dcr = self.__minfluxprocessor.full_dataframe["dcr"].values
        if len(dcr) == 0:
            return

        # Prepare the data
        values = dcr.reshape(-1, 1)

        # Keep track of the total number of elements for normalisation
        n_total = len(values)

        # Fit a Bayesian Gaussian Mixture Model with self.state.num_fluorophores components
        model = BayesianGaussianMixture(
            n_components=self.state.num_fluorophores,
            init_params="k-means++",
            covariance_type="full",
            max_iter=1000,
            random_state=42,
        ).fit(values)

        # Predict with the selected model
        y_pred = model.predict(values)

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Prepare some colors
        brushes = ["r", "b", "g", "m", "c"]

        # Calculate the bar width as a function of the number of fluorophores
        bar_width = 0.9 / self.state.num_fluorophores
        offset = self.dcr_bin_width / self.state.num_fluorophores

        # Create new histograms
        for f in range(self.state.num_fluorophores):
            data = values[y_pred == f]
            if len(data) == 0:
                continue

            # Calculate the dcr histogram using the global bins
            n_dcr, _ = np.histogram(data, bins=self.dcr_bin_edges, density=False)

            # Normalize by the total count
            n_dcr = n_dcr / n_total

            # Create the bar chart
            chart = pg.BarGraphItem(
                x=self.dcr_bin_centers + f * offset,
                height=n_dcr,
                width=bar_width * self.dcr_bin_width,
                brush=brushes[f],
                alpha=0.5,
            )
            self.plot_widget.addItem(chart)

        # Store the predictions (1-shifted)
        self.assigned_fluorophore_ids = y_pred + 1

        # Make sure to enable the assign button
        self.ui.pbAssign.setEnabled(True)

    @Slot(None, name="assign_fluorophores_ids")
    def assign_fluorophores_ids(self):
        """Assign the fluorophores ids."""

        if self.assigned_fluorophore_ids is None:
            return

        # Assign the IDs via the processor
        self.__minfluxprocessor.set_fluorophore_ids(self.assigned_fluorophore_ids)

        # Inform that the fluorophore IDs have been assigned
        self.fluorophore_ids_assigned.emit(
            len(np.unique(self.assigned_fluorophore_ids))
        )

        # Disable the button until the new detection is run
        self.ui.pbAssign.setEnabled(False)
