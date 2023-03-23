from PySide6.QtCore import QPoint, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget

from ..reader import MinFluxReader
from ..state import State
from .ui_plotter_toolbar import Ui_PlotterToolbar


class PlotterToolbar(QWidget, Ui_PlotterToolbar):

    plot_requested_parameters = Signal(int, name="plot_requested_parameters")

    def __init__(self):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_PlotterToolbar()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Add the values to the combo boxes
        self.ui.cbFirstParam.addItems(MinFluxReader.processed_properties())
        self.ui.cbFirstParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("x")
        )
        self.ui.cbSecondParam.addItems(MinFluxReader.processed_properties())
        self.ui.cbSecondParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("y")
        )

        self.ui.cbFirstParam.currentIndexChanged.connect(self.persist_first_param)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.persist_second_param)
        self.ui.pbPlot.clicked.connect(self.emit_plot_requested)

    @Slot(None, name="persist_first_param")
    def persist_first_param(self, index):
        """Persist the selection for the first parameter."""

        # Get property list
        props = MinFluxReader.processed_properties()

        # Persist the selection
        self.state.x_param = props[index]

    @Slot(None, name="persist_second_param")
    def persist_second_param(self, index):
        """Persist the selection for the second parameter."""

        # Get property list
        props = MinFluxReader.processed_properties()

        # Persist the selection
        self.state.y_param = props[index]

    @Slot(None, name="emit_plot_requested")
    def emit_plot_requested(self):
        """Plot the requested parameters."""

        # Emit signal
        self.plot_requested_parameters.emit()

    @Slot(int, name="set_fluorophore_list")
    def set_fluorophore_list(self, num_fluorophores):
        """Update the fluorophores pull-down menu."""

        # Remove old items
        self.ui.cbFluorophoreIndex.clear()

        # Add new items

        self.ui.cbFluorophoreIndex.addItems(["All"] + list([str(i + 1) for i in range(num_fluorophores)]))

        # Fall back to no fluorophore id selected
        self.ui.cbFluorophoreIndex.setCurrentIndex(0)
