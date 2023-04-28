#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

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

        # Set height explicitly, since only half of the widgets will be displayed
        # at any given time
        self.resize(self.width(), 95)

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

    def set_target(self, target):
        if target not in ["efo", "cfr"]:
            raise ValueError("Expected 'efo' or 'cfr' targets.")

        if target == "efo":
            self.ui.lbCFR.setVisible(False)
            self.ui.lbMinCFR.setVisible(False)
            self.ui.leCFRMin.setVisible(False)
            self.ui.lbCFRMax.setVisible(False)
            self.ui.leCFRMax.setVisible(False)
            self.ui.lbEFO.setVisible(True)
            self.ui.lbEFOMin.setVisible(True)
            self.ui.leEFOMin.setVisible(True)
            self.ui.lbEFOMax.setVisible(True)
            self.ui.leEFOMax.setVisible(True)
            self.setWindowTitle("EFO roi range")
        else:
            self.ui.lbCFR.setVisible(True)
            self.ui.lbMinCFR.setVisible(True)
            self.ui.leCFRMin.setVisible(True)
            self.ui.lbCFRMax.setVisible(True)
            self.ui.leCFRMax.setVisible(True)
            self.ui.lbEFO.setVisible(False)
            self.ui.lbEFOMin.setVisible(False)
            self.ui.leEFOMin.setVisible(False)
            self.ui.lbEFOMax.setVisible(False)
            self.ui.leEFOMax.setVisible(False)
            self.setWindowTitle("CFR roi range")
