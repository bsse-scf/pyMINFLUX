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

from PySide6.QtCore import QSignalBlocker, Signal, Slot
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog

from pyminflux.state import State

from ..analysis import prepare_histogram
from .ui_wizard import Ui_WizardDialog


class WizardDialog(QDialog, Ui_WizardDialog):
    load_data_triggered = Signal(None, name="load_data_triggered")
    open_unmixer_triggered = Signal(None, name="open_unmixer_triggered")
    open_time_inspector_triggered = Signal(None, name="open_time_inspector_triggered")
    open_analyzer_triggered = Signal(None, name="open_analyzer_triggered")
    fluorophore_id_changed = Signal(int, name="fluorophore_id_changed")
    request_fluorophore_ids_reset = Signal(None, name="request_fluorophore_ids_reset")
    efo_bounds_modified = Signal(None, name="efo_bounds_modified")
    cfr_bounds_modified = Signal(None, name="cfr_bounds_modified")
    cfr_robust_threshold_modified = Signal(float, name="cfr_robust_threshold_modified ")
    wizard_filters_run = Signal(None, name="wizard_filters_run")
    export_data_triggered = Signal(None, name="export_data_triggered")

    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_WizardDialog()
        self.ui.setupUi(self)

        # Keep a reference to the singleton State class
        self.state = State()

        # Keep a reference (initially unset) to the processor
        self._minfluxprocessor = None

        # Disable controls
        self.enable_controls(False)

        # Fill the fields
        self.ui.leEFOLowerBound.setText("")
        self.ui.leEFOLowerBound.setValidator(QDoubleValidator(decimals=0))
        self.ui.leEFOUpperBound.setText("")
        self.ui.leEFOUpperBound.setValidator(QDoubleValidator(decimals=0))
        self.ui.leCFRLowerBound.setText("")
        self.ui.leCFRLowerBound.setValidator(QDoubleValidator(decimals=2))
        self.ui.leCFRUpperBound.setText("")
        self.ui.leCFRUpperBound.setValidator(QDoubleValidator(decimals=2))

        # Set up connections
        self.setup_conn()

    def set_processor(self, processor):
        """Store a reference to the processor."""
        self._minfluxprocessor = processor

        # Prepare and fill the filter ranges
        self.prepare_filter_ranges()

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
        self.ui.leEFOLowerBound.textChanged.connect(
            self.efo_change_lower_bound_and_broadcast
        )
        self.ui.leEFOUpperBound.textChanged.connect(
            self.efo_change_upper_bound_and_broadcast
        )
        self.ui.leCFRLowerBound.textChanged.connect(
            self.cfr_change_lower_bound_and_broadcast
        )
        self.ui.leCFRUpperBound.textChanged.connect(
            self.cfr_change_upper_bound_and_broadcast
        )
        self.ui.pbEFOFilter.clicked.connect(self.run_efo_filter_and_broadcast)
        self.ui.pbCFRFilter.clicked.connect(self.run_cfr_filter_and_broadcast)
        self.ui.pbExportData.clicked.connect(
            lambda _: self.export_data_triggered.emit()
        )

    def prepare_filter_ranges(self):
        """Extract bounds from the EFO and CFR data and prefill the values."""

        if self._minfluxprocessor is None:
            return

        # Get the range for the EFO data
        if self.state.efo_thresholds is None:
            _, efo_bin_edges, _, _ = prepare_histogram(
                self._minfluxprocessor.filtered_dataframe["efo"].values,
                auto_bins=self.state.efo_bin_size_hz == 0,
                bin_size=self.state.efo_bin_size_hz,
            )
            self.state.efo_thresholds = (efo_bin_edges[0], efo_bin_edges[-1])

        # Get the range for the CFR data
        _, cfr_bin_edges, _, _ = prepare_histogram(
            self._minfluxprocessor.filtered_dataframe["cfr"].values,
            auto_bins=True,
            bin_size=0.0,
        )
        self.state.cfr_thresholds = (cfr_bin_edges[0], cfr_bin_edges[-1])

        # Fill the fields
        self.ui.leEFOLowerBound.setText(f"{self.state.efo_thresholds[0]:.0f}")
        self.ui.leEFOUpperBound.setText(f"{self.state.efo_thresholds[1]:.0f}")
        self.ui.leCFRLowerBound.setText(f"{self.state.cfr_thresholds[0]:.2f}")
        self.ui.leCFRUpperBound.setText(f"{self.state.cfr_thresholds[1]:.2f}")

    def enable_controls(self, enabled: bool = False):
        # The Load data button is always visible
        self.ui.pbLoadData.show()

        # Color unmixing
        self.ui.lbColors.setVisible(enabled)
        self.ui.pbSingleColor.setVisible(enabled)
        self.ui.pbColorUnmixer.setVisible(enabled)
        self.ui.lbActiveColor.setVisible(enabled)
        self.ui.cmActiveColor.setVisible(enabled)

        # Time inspector
        self.ui.lbFilters.setVisible(enabled)
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
        self.ui.pbCFRFilter.setVisible(enabled)

        # Export data
        self.ui.pbExportData.setVisible(enabled)

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

    @Slot(None, name="run_efo_filter_and_broadcast")
    def run_efo_filter_and_broadcast(self):
        """Run the EFO filter and broadcast the changes."""

        # Apply the EFO filter if needed
        if self.state.efo_thresholds is not None:
            self._minfluxprocessor.filter_by_1d_range(
                "efo", (self.state.efo_thresholds[0], self.state.efo_thresholds[1])
            )
        # Signal that the external viewers should be updated
        self.wizard_filters_run.emit()

    @Slot(None, name="run_cfr_filter_and_broadcast")
    def run_cfr_filter_and_broadcast(self):
        """Run the CFR filter and broadcast the changes."""

        # Apply the CFR filter if needed
        if self.state.cfr_thresholds is not None:
            self._minfluxprocessor.filter_by_1d_range(
                "cfr", (self.state.cfr_thresholds[0], self.state.cfr_thresholds[1])
            )
        # Signal that the external viewers should be updated
        self.wizard_filters_run.emit()

    @Slot(None, name="efo_change_lower_bound_and_broadcast")
    def efo_change_lower_bound_and_broadcast(self, text):
        """Update the EFO lower bound and broadcast changes."""

        # Get the new value
        try:
            efo_lower_bound = float(text)
        except ValueError as _:
            return
        if self.state.efo_thresholds[0] == efo_lower_bound:
            return

        # Update
        self.state.efo_thresholds = (efo_lower_bound, self.state.efo_thresholds[1])

        # Broadcast
        self.efo_bounds_modified.emit()

    @Slot(None, name="efo_change_upper_bound_and_broadcast")
    def efo_change_upper_bound_and_broadcast(self, text):
        """Update the EFO upper bound and broadcast changes."""

        # Get the new value
        try:
            efo_upper_bound = float(text)
        except ValueError as _:
            return
        if self.state.efo_thresholds[1] == efo_upper_bound:
            return

        # Update
        self.state.efo_thresholds = (self.state.efo_thresholds[0], efo_upper_bound)

        # Broadcast
        self.efo_bounds_modified.emit()

    @Slot(None, name="cfr_change_lower_bound_and_broadcast")
    def cfr_change_lower_bound_and_broadcast(self, text):
        """Update the CFR lower bound and broadcast changes."""

        # Get the new value
        try:
            cfr_lower_bound = float(text)
        except ValueError as _:
            return
        if self.state.cfr_thresholds[0] == cfr_lower_bound:
            return

        # Update
        self.state.cfr_thresholds = (cfr_lower_bound, self.state.cfr_thresholds[1])

        # Broadcast
        self.cfr_bounds_modified.emit()

    @Slot(None, name="cfr_change_upper_bound_and_broadcast")
    def cfr_change_upper_bound_and_broadcast(self, text):
        """Update the CFR upper bound and broadcast changes."""

        # Get the new value
        try:
            cfr_upper_bound = float(text)
        except ValueError as _:
            return
        if self.state.cfr_thresholds[1] == cfr_upper_bound:
            return

        # Update
        self.state.cfr_thresholds = (self.state.cfr_thresholds[0], cfr_upper_bound)

        # Broadcast
        self.cfr_bounds_modified.emit()
