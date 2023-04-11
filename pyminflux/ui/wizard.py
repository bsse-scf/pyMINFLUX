from PySide6.QtCore import QSignalBlocker, Signal, Slot
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog

from pyminflux.state import State

from .ui_wizard import Ui_WizardDialog


class WizardDialog(QDialog, Ui_WizardDialog):

    load_data_triggered = Signal(None, name="load_data_triggered")
    open_unmixer_triggered = Signal(None, name="open_unmixer_triggered")
    open_time_inspector_triggered = Signal(None, name="open_time_inspector_triggered")
    open_analyzer_triggered = Signal(None, name="open_analyzer_triggered")
    fluorophore_id_changed = Signal(int, name="fluorophore_id_changed")
    request_fluorophore_ids_reset = Signal(None, name="request_fluorophore_ids_reset")
    efo_lower_bound_modified = Signal(float, name="efo_lower_bound_modified")
    efo_upper_bound_modified = Signal(float, name="efo_upper_bound_modified")
    cfr_lower_bound_modified = Signal(float, name="cfr_lower_bound_modified")
    cfr_upper_bound_modified = Signal(float, name="cfr_upper_bound_modified")
    cfr_robust_threshold_modified = Signal(float, name="cfr_robust_threshold_modified ")

    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_WizardDialog()
        self.ui.setupUi(self)

        # Keep a reference to the singleton State class
        self.state = State()

        # Disable controls
        self.enable_controls(False)

        # Fill the fields
        self.ui.leEFOLowerBound.setText("")
        self.ui.leEFOUpperBound.setText("")
        self.ui.leCFRLowerBound.setText("")
        self.ui.leCFRUpperBound.setText("")
        self.ui.leCFRSigma.setText(str(self.state.cfr_threshold_factor))
        self.ui.leCFRSigma.setValidator(
            QDoubleValidator(bottom=0.0, top=5.0, decimals=2)
        )
        self.ui.cbCFRLowerBound.setChecked(self.state.enable_cfr_lower_threshold)
        self.ui.cbCFRUpperBound.setChecked(self.state.enable_cfr_upper_threshold)

        # Set up connections
        self.setup_conn()

    def setup_conn(self):

        self.ui.pbLoadData.clicked.connect(lambda _: self.load_data_triggered.emit())
        self.ui.pbSingleColor.clicked.connect(self.reset_fluorophores)
        self.ui.pbColorUnmixer.clicked.connect(
            lambda _: self.open_unmixer_triggered.emit()
        )
        self.ui.pbColorUnmixer.clicked.connect(lambda _: self.enable_controls(True))
        self.ui.pbTimeInspector.clicked.connect(
            lambda _: self.open_time_inspector_triggered.emit()
        )
        self.ui.pbAnalyzer.clicked.connect(
            lambda _: self.open_analyzer_triggered.emit()
        )
        self.ui.cmActiveColor.currentIndexChanged.connect(
            self.fluorophore_index_changed
        )

    def enable_controls(self, enabled: bool = False):

        # The Load data button is always visible
        self.ui.pbLoadData.show()

        # Color unmixing
        self.ui.pbSingleColor.setVisible(enabled)
        self.ui.pbColorUnmixer.setVisible(enabled)
        self.ui.lbActiveColor.setVisible(enabled)
        self.ui.cmActiveColor.setVisible(enabled)

        # Time inspector
        self.ui.pbTimeInspector.setVisible(enabled)

        # Analyzer
        self.ui.pbAnalyzer.setVisible(enabled)

        # EFO filtering
        self.ui.lbEFOFiltering.setVisible(enabled)
        self.ui.lbEFOLowerBound.setVisible(enabled)
        self.ui.leEFOLowerBound.setVisible(enabled)
        self.ui.lbEFOUpperBound.setVisible(enabled)
        self.ui.leEFOUpperBound.setVisible(enabled)
        self.ui.pbEFOFilter.setVisible(enabled)

        # CFR filtering
        self.ui.lbCFRFiltering.setVisible(enabled)
        self.ui.lbCFRLowerBound.setVisible(enabled)
        self.ui.leCFRLowerBound.setVisible(enabled)
        self.ui.lbCFRUpperBound.setVisible(enabled)
        self.ui.leCFRUpperBound.setVisible(enabled)
        self.ui.lbCFRSigma.setVisible(enabled)
        self.ui.leCFRSigma.setVisible(enabled)
        self.ui.cbCFRLowerBound.setVisible(enabled)
        self.ui.cbCFRUpperBound.setVisible(enabled)
        self.ui.pbCFRFilter.setVisible(enabled)

    def reset_fluorophores(self):
        """Reset the fluorophores."""

        # Reset the fluorophore ID assignment
        self.request_fluorophore_ids_reset.emit()

        # Update the color selection combo box
        self.set_fluorophore_list(1)

    @Slot(int, name="set_fluorophore_list")
    def set_fluorophore_list(self, num_fluorophores):
        """Update the fluorophores pull-down menu."""

        # Signal blocker on self.efo_cfr_roi
        blocker = QSignalBlocker(self.ui.cmActiveColor)

        # Block signals from the combo box
        blocker.reblock()

        # Remove old items
        self.ui.cmActiveColor.clear()

        # Add new items
        if num_fluorophores == 1:
            self.ui.cmActiveColor.addItems(["All"])
        else:
            self.ui.cmActiveColor.addItems(
                ["All"] + list([str(i + 1) for i in range(num_fluorophores)])
            )

        # Release the blocker
        blocker.unblock()

        # Fall back to no fluorophore id selected.
        # This is allowed to signal.
        self.ui.cmActiveColor.setCurrentIndex(0)

    @Slot(int, name="fluorophore_index_changed")
    def fluorophore_index_changed(self, index):
        """Emit a signal informing that the fluorophore id has changed."""

        # If the items have just been added, the index will be -1
        if index == -1:
            return

        # The fluorophore index is 1 + the combobox current index
        self.fluorophore_id_changed.emit(index)

    @Slot(None, name="change_cfr_threshold_factor")
    def change_cfr_threshold_factor(self):
        """Update the value of the cfr threshold factor."""
        self.ui.leCFRSigma.setText(str(self.state.cfr_threshold_factor))

    @Slot(None, name="change_cfr_lower_bound_state")
    def change_cfr_lower_bound_state(self):
        """Update the state of the cfr lower bound checkbox."""
        self.ui.cbCFRLowerBound.setChecked(self.state.enable_cfr_lower_threshold)

    @Slot(None, name="change_cfr_upper_bound_state")
    def change_cfr_upper_bound_state(self):
        """Update the state of the cfr upper bound checkbox."""
        self.ui.cbCFRUpperBound.setChecked(self.state.enable_cfr_upper_threshold)

    @Slot(None, name="change_efo_bounds")
    def change_efo_bounds(self):
        """Update the EFO bounds."""
        self.ui.leEFOLowerBound.setText(f"{self.state.efo_thresholds[0]:.0f}")
        self.ui.leEFOUpperBound.setText(f"{self.state.efo_thresholds[1]:.0f}")

    @Slot(None, name="change_cfr_bounds")
    def change_cfr_bounds(self):
        """Update the CFR bounds."""
        self.ui.leCFRLowerBound.setText(f"{self.state.cfr_thresholds[0]:.2f}")
        self.ui.leCFRUpperBound.setText(f"{self.state.cfr_thresholds[1]:.2f}")
