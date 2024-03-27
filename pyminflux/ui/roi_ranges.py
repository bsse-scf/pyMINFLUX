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
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_ROIRanges()
        self.ui.setupUi(self)

        # Known ROIs
        self._valid_ROIs = ["efo", "cfr", "tr_len", "time_inspector"]

        # Set dialog name
        self.setWindowTitle("ROI ranges")

        # Get a reference to the state
        self.state = State()

        # Precision
        self.cfr_precision = 2
        self.efo_precision = 2
        self.tr_len_precision = 2
        self.time_precision = 2

        # Initialize the input fields
        self.update_fields()

        # Add validators
        self.ui.leCFRMin.setValidator(QDoubleValidator(decimals=self.cfr_precision))
        self.ui.leCFRMax.setValidator(QDoubleValidator(decimals=self.cfr_precision))
        self.ui.leEFOMin.setValidator(QDoubleValidator(decimals=self.efo_precision))
        self.ui.leEFOMax.setValidator(QDoubleValidator(decimals=self.efo_precision))
        self.ui.leTrLenMin.setValidator(
            QDoubleValidator(decimals=self.tr_len_precision)
        )
        self.ui.leTrLenMax.setValidator(
            QDoubleValidator(decimals=self.tr_len_precision)
        )
        self.ui.leTimeMin.setValidator(QDoubleValidator(decimals=self.time_precision))
        self.ui.leTimeMax.setValidator(QDoubleValidator(decimals=self.time_precision))

        # Set height explicitly, since only one row of widgets will be displayed
        # at any given time
        self.resize(self.width(), 95)

    def update_fields(self):
        """Force an update of the input fields."""
        if self.state.cfr_thresholds is not None:
            self.ui.leCFRMin.setText(
                f"{self.state.cfr_thresholds[0]:.{self.cfr_precision}f}"
            )
            self.ui.leCFRMax.setText(
                f"{self.state.cfr_thresholds[1]:.{self.cfr_precision}f}"
            )

        if self.state.efo_thresholds is not None:
            self.ui.leEFOMin.setText(
                f"{self.state.efo_thresholds[0]:.{self.efo_precision}f}"
            )
            self.ui.leEFOMax.setText(
                f"{self.state.efo_thresholds[1]:.{self.efo_precision}f}"
            )

        if self.state.tr_len_thresholds is not None:
            self.ui.leTrLenMin.setText(
                f"{self.state.tr_len_thresholds[0]:.{self.tr_len_precision}f}"
            )
            self.ui.leTrLenMax.setText(
                f"{self.state.tr_len_thresholds[1]:.{self.tr_len_precision}f}"
            )

        if self.state.time_thresholds is not None:
            self.ui.leTimeMin.setText(
                f"{self.state.time_thresholds[0]:.{self.time_precision}f}"
            )
            self.ui.leTimeMax.setText(
                f"{self.state.time_thresholds[1]:.{self.time_precision}f}"
            )

    def accept(self):
        """Override accept slot."""

        # Update ranges in the State

        # CFR
        cfr_min_t = self.ui.leCFRMin.text()
        cfr_max_t = self.ui.leCFRMax.text()
        if cfr_min_t == "" or cfr_max_t == "":
            self.state.cfr_thresholds = None
        else:
            try:
                # Convert to float
                cfr_min = float(cfr_min_t)
                cfr_max = float(cfr_max_t)

                # Make sure that min < max
                if cfr_max < cfr_min:
                    cfr_min, cfr_max = cfr_max, cfr_min

                # Check if there were changes at the given precision
                if round(cfr_min, self.cfr_precision) == round(
                    self.state.cfr_thresholds[0], self.cfr_precision
                ):
                    cfr_min = self.state.cfr_thresholds[0]
                if round(cfr_max, self.cfr_precision) == round(
                    self.state.cfr_thresholds[1], self.cfr_precision
                ):
                    cfr_max = self.state.cfr_thresholds[1]

                # Update the state
                self.state.cfr_thresholds = (cfr_min, cfr_max)

            except ValueError:
                self.state.cfr_thresholds = None

        # EFO
        efo_min_t = self.ui.leEFOMin.text()
        efo_max_t = self.ui.leEFOMax.text()
        if efo_min_t == "" or efo_max_t == "":
            self.state.efo_thresholds = None
        else:
            try:
                # Convert to float
                efo_min = float(efo_min_t)
                efo_max = float(efo_max_t)

                # Make sure that min < max
                if efo_max < efo_min:
                    efo_min, efo_max = efo_max, efo_min

                # Check if there were changes at the given precision
                if round(efo_min, self.efo_precision) == round(
                    self.state.efo_thresholds[0], self.efo_precision
                ):
                    efo_min = self.state.efo_thresholds[0]
                if round(efo_max, self.efo_precision) == round(
                    self.state.efo_thresholds[1], self.efo_precision
                ):
                    efo_max = self.state.efo_thresholds[1]

                # Update the state only if the values changed
                self.state.efo_thresholds = (efo_min, efo_max)

            except ValueError:
                self.state.efo_thresholds = None

        # TR_LEN
        tr_len_min_t = self.ui.leTrLenMin.text()
        tr_len_max_t = self.ui.leTrLenMax.text()
        if tr_len_min_t == "" or tr_len_max_t == "":
            self.state.tr_len_thresholds = None
        else:
            try:
                # Convert to float
                tr_len_min = float(tr_len_min_t)
                tr_len_max = float(tr_len_max_t)

                # Make sure that min < max
                if tr_len_max < tr_len_min:
                    tr_len_min, tr_len_max = tr_len_max, tr_len_min

                # Check if there were changes at the given precision
                if round(tr_len_min, self.tr_len_precision) == round(
                    self.state.tr_len_thresholds[0], self.tr_len_precision
                ):
                    tr_len_min = self.state.tr_len_thresholds[0]
                if round(tr_len_max, self.tr_len_precision) == round(
                    self.state.tr_len_thresholds[1], self.tr_len_precision
                ):
                    tr_len_max = self.state.tr_len_thresholds[1]

                # Update the state
                self.state.tr_len_thresholds = (tr_len_min, tr_len_max)

            except ValueError:
                self.state.tr_len_thresholds = None

        # TIME
        time_min_t = self.ui.leTimeMin.text()
        time_max_t = self.ui.leTimeMax.text()
        if time_min_t == "" or time_max_t == "":
            self.state.time_thresholds = None
        else:
            try:
                # Convert to float
                time_min = float(time_min_t)
                time_max = float(time_max_t)

                # Make sure that min < max
                if time_max < time_min:
                    time_min, time_max = time_max, time_min

                # Check if there were changes at the given precision
                if round(time_min, self.time_precision) == round(
                    self.state.time_thresholds[0], self.time_precision
                ):
                    time_min = self.state.time_thresholds[0]
                if round(time_max, self.time_precision) == round(
                    self.state.time_thresholds[1], self.time_precision
                ):
                    time_max = self.state.time_thresholds[1]

                # Update the state
                self.state.time_thresholds = (time_min, time_max)

            except ValueError:
                self.state.time_thresholds = None

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
        elif target == "time_inspector":
            self._toggle_ui_elements(time_inspector_b=True)
            self.setWindowTitle("Time interval")
        else:
            raise ValueError("Unexpected ROI target.")

    def _toggle_ui_elements(
        self,
        cfr_b: bool = False,
        efo_b: bool = False,
        tr_len_b: bool = False,
        time_inspector_b: bool = False,
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
        # Time inspector
        self.ui.lbTime.setVisible(time_inspector_b)
        self.ui.lbTimeMin.setVisible(time_inspector_b)
        self.ui.leTimeMin.setVisible(time_inspector_b)
        self.ui.lbTimeMax.setVisible(time_inspector_b)
        self.ui.leTimeMax.setVisible(time_inspector_b)
