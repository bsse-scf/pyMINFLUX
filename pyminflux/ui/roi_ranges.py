from PySide6.QtCore import Signal
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog

from ..state import State
from .ui_roi_ranges import Ui_ROIRanges


class ROIRanges(QDialog, Ui_ROIRanges):

    # Signal that the data viewers should be updated
    data_ranges_changed = Signal(None, name="data_ranges_changed")

    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_ROIRanges()
        self.ui.setupUi(self)

        # Set dialog name
        self.setWindowTitle("ROI ranges")

        # Get a reference to the state
        self.state = State()

        # Initialize the input fields
        self.update_fields()

        # Add validators
        self.ui.leCFRMin.setValidator(QDoubleValidator(decimals=2))
        self.ui.leCFRMax.setValidator(QDoubleValidator(decimals=2))
        self.ui.leEFOMin.setValidator(QDoubleValidator(decimals=0))
        self.ui.leEFOMax.setValidator(QDoubleValidator(decimals=0))

    def update_fields(self):
        """Force an update of the input fields."""
        self.ui.leCFRMin.setText(f"{self.state.cfr_thresholds[0]:.2f}")
        self.ui.leCFRMax.setText(f"{self.state.cfr_thresholds[1]:.2f}")
        self.ui.leEFOMin.setText(f"{self.state.efo_thresholds[0]:.0f}")
        self.ui.leEFOMax.setText(f"{self.state.efo_thresholds[1]:.0f}")

    def accept(self):
        """Override accept slot."""

        # Update ranges in the State
        cfr_min = float(self.ui.leCFRMin.text())
        cfr_max = float(self.ui.leCFRMax.text())
        if cfr_max < cfr_min:
            cfr_min, cfr_max = cfr_max, cfr_min
        efo_min = float(self.ui.leEFOMin.text())
        efo_max = float(self.ui.leEFOMax.text())
        if efo_max < efo_min:
            efo_min, efo_max = efo_max, efo_min
        self.state.cfr_thresholds = (cfr_min, cfr_max)
        self.state.efo_thresholds = (efo_min, efo_max)

        # Inform that the ranges have changed
        self.data_ranges_changed.emit()

        # Call the base class accept() method
        super().accept()
