from PySide6.QtCore import QSignalBlocker, Signal, Slot
from PySide6.QtWidgets import QWidget

from ..reader import MinFluxReader
from ..state import State
from .ui_plotter_toolbar import Ui_PlotterToolbar


class PlotterToolbar(QWidget, Ui_PlotterToolbar):

    plot_requested_parameters = Signal(None, name="plot_requested_parameters")
    fluorophore_id_changed = Signal(int, name="fluorophore_id_changed")

    def __init__(self):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_PlotterToolbar()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Add the values to the plot properties combo boxes (without time)
        first_param_wo_time = MinFluxReader.processed_properties()
        first_param_wo_time.remove("tim")
        self.ui.cbFirstParam.addItems(first_param_wo_time)
        self.ui.cbFirstParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("x")
        )
        second_param_wo_time = MinFluxReader.processed_properties()
        second_param_wo_time.remove("tim")
        self.ui.cbSecondParam.addItems(second_param_wo_time)
        self.ui.cbSecondParam.setCurrentIndex(
            MinFluxReader.processed_properties().index("y")
        )

        self.ui.cbFirstParam.currentIndexChanged.connect(self.persist_first_param)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.persist_second_param)
        self.ui.pbPlot.clicked.connect(self.emit_plot_requested)

        # Add callback to the fluorophore combo box
        self.ui.cbFluorophoreIndex.currentIndexChanged.connect(
            self.fluorophore_index_changed
        )

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

        # Signal blocker on self.efo_cfr_roi
        blocker = QSignalBlocker(self.ui.cbFluorophoreIndex)

        # Block signals from the combo box
        blocker.reblock()

        # Remove old items
        self.ui.cbFluorophoreIndex.clear()

        # Add new items
        if num_fluorophores < 2:
            self.ui.cbFluorophoreIndex.addItems(["All"])
        else:
            self.ui.cbFluorophoreIndex.addItems(
                ["All"] + list([str(i + 1) for i in range(num_fluorophores)])
            )

        # Release the blocker
        blocker.unblock()

        # Fall back to no fluorophore id selected.
        # This is allowed to signal.
        self.ui.cbFluorophoreIndex.setCurrentIndex(0)

    @Slot(int, name="fluorophore_index_changed")
    def fluorophore_index_changed(self, index):
        """Emit a signal informing that the fluorophore id has changed."""

        # If the items have just been added, the index will be -1
        if index == -1:
            return

        # An index of 0 means no selection, the others map to the fluorophore id
        self.fluorophore_id_changed.emit(index)
