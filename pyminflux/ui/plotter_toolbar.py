from PySide6.QtCore import QSignalBlocker, Signal, Slot
from PySide6.QtWidgets import QWidget

from ..reader import MinFluxReader
from ..state import ColorCode, State
from .ui_plotter_toolbar import Ui_PlotterToolbar


class PlotterToolbar(QWidget, Ui_PlotterToolbar):

    plot_requested_parameters = Signal(None, name="plot_requested_parameters")
    fluorophore_id_changed = Signal(int, name="fluorophore_id_changed")
    color_code_locs_changed = Signal(int, name="color_code_locs_changed")

    def __init__(self):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_PlotterToolbar()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # The main plotter does not focus on temporal measurement
        self.plotting_parameters = MinFluxReader.processed_properties()

        # Add the values to the plot properties combo boxes (without time)
        self.ui.cbFirstParam.addItems(self.plotting_parameters)
        self.ui.cbFirstParam.setCurrentIndex(self.plotting_parameters.index("x"))
        self.ui.cbSecondParam.addItems(self.plotting_parameters)
        self.ui.cbSecondParam.setCurrentIndex(self.plotting_parameters.index("y"))

        self.ui.cbFirstParam.currentIndexChanged.connect(self.persist_first_param)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.persist_second_param)
        self.ui.pbPlot.clicked.connect(self.emit_plot_requested)

        # Color-code combo box
        self.ui.cbColorCodeSelector.setCurrentIndex(0)
        self.ui.cbColorCodeSelector.currentIndexChanged.connect(
            self.persist_color_code_and_broadcast
        )

        # Add callback to the fluorophore combo box
        self.ui.cbFluorophoreIndex.currentIndexChanged.connect(
            self.fluorophore_index_changed
        )

    @Slot(int, name="persist_color_code_and_broadcast")
    def persist_color_code_and_broadcast(self, index):
        """Persist the selection of the color code and broadcast a change."""
        self.state.color_code = ColorCode(index)

        # Broadcast the change
        self.color_code_locs_changed.emit(self.state.color_code.value)

    @Slot(int, name="persist_first_param")
    def persist_first_param(self, index):
        """Persist the selection for the first parameter."""

        # Persist the selection
        self.state.x_param = self.plotting_parameters[index]

    @Slot(int, name="persist_second_param")
    def persist_second_param(self, index):
        """Persist the selection for the second parameter."""

        # Persist the selection
        self.state.y_param = self.plotting_parameters[index]

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

        # The fluorophore index is 1 + the combobox current index
        self.fluorophore_id_changed.emit(index)
