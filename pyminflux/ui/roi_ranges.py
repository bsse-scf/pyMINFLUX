#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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

        # Known ROIs
        self._valid_ROIs = ["efo", "cfr", "tr_len"]

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
        self.ui.leTrLenMin.setValidator(QDoubleValidator(decimals=2))
        self.ui.leTrLenMax.setValidator(QDoubleValidator(decimals=2))

        # Set height explicitly, since only half of the widgets will be displayed
        # at any given time
        self.resize(self.width(), 95)

    def update_fields(self):
        """Force an update of the input fields."""
        if self.state.cfr_thresholds is not None:
            self.ui.leCFRMin.setText(f"{self.state.cfr_thresholds[0]:.2f}")
            self.ui.leCFRMax.setText(f"{self.state.cfr_thresholds[1]:.2f}")

        if self.state.efo_thresholds is not None:
            self.ui.leEFOMin.setText(f"{self.state.efo_thresholds[0]:.0f}")
            self.ui.leEFOMax.setText(f"{self.state.efo_thresholds[1]:.0f}")

        if self.state.tr_len_thresholds is not None:
            self.ui.leTrLenMin.setText(f"{self.state.tr_len_thresholds[0]:.2f}")
            self.ui.leTrLenMax.setText(f"{self.state.tr_len_thresholds[1]:.2f}")

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
        tr_len_min = float(self.ui.leTrLenMin.text())
        tr_len_max = float(self.ui.leTrLenMax.text())
        if tr_len_max < tr_len_min:
            tr_len_min, tr_len_max = tr_len_max, tr_len_min
        self.state.cfr_thresholds = (cfr_min, cfr_max)
        self.state.efo_thresholds = (efo_min, efo_max)
        self.state.tr_len_thresholds = (tr_len_min, tr_len_max)

        # Inform that the ranges have changed
        self.data_ranges_changed.emit()

        # Call the base class accept() method
        super().accept()

    def set_target(self, target):
        if target not in self._valid_ROIs:
            raise ValueError("Unexpected ROI target.")

        if target == "efo":
            self._toggle_ui_elements(efo_b=True)
            self.setWindowTitle("EFO roi range")
        elif target == "cfr":
            self._toggle_ui_elements(cfr_b=True)
            self.setWindowTitle("CFR roi range")
        elif target == "tr_len":
            self._toggle_ui_elements(tr_len_b=True)
            self.setWindowTitle("Trace lengths roi range")
        else:
            raise ValueError("Unexpected ROI target.")

    def _toggle_ui_elements(
        self, cfr_b: bool = False, efo_b: bool = False, tr_len_b: bool = False
    ):
        """Toggle on/off the requested UI elements."""
        # CFR elements
        self.ui.lbCFR.setVisible(cfr_b)
        self.ui.lbMinCFR.setVisible(cfr_b)
        self.ui.leCFRMin.setVisible(cfr_b)
        self.ui.lbCFRMax.setVisible(cfr_b)
        self.ui.leCFRMax.setVisible(cfr_b)
        # EFO elements
        self.ui.lbEFO.setVisible(efo_b)
        self.ui.lbEFOMin.setVisible(efo_b)
        self.ui.leEFOMin.setVisible(efo_b)
        self.ui.lbEFOMax.setVisible(efo_b)
        self.ui.leEFOMax.setVisible(efo_b)
        # Trace length elements
        self.ui.lbTrLen.setVisible(tr_len_b)
        self.ui.lbTrLenMin.setVisible(tr_len_b)
        self.ui.leTrLenMin.setVisible(tr_len_b)
        self.ui.lbTrLenMax.setVisible(tr_len_b)
        self.ui.leTrLenMax.setVisible(tr_len_b)
