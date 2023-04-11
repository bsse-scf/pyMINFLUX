from PySide6.QtCore import QSettings, Signal, Slot
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QDialog

from pyminflux.state import State

from .ui_options import Ui_Options


class Options(QDialog, Ui_Options):

    # Signal that the options have changed
    min_num_loc_per_trace_option_changed = Signal(
        name="min_num_loc_per_trace_option_changed"
    )
    efo_bin_size_hz_option_changed = Signal(name="efo_bin_size_hz_option_changed")
    weigh_avg_localization_by_eco_option_changed = Signal(
        name="weigh_avg_localization_by_eco_option_changed"
    )

    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_Options()
        self.ui.setupUi(self)

        # Keep a reference to the singleton State class
        self.state = State()

        # Set defaults
        self.ui.leMinTIDNum.setText(str(self.state.min_num_loc_per_trace))
        self.ui.leMinTIDNum.setValidator(QIntValidator(bottom=0))
        self.ui.leEFOBinSize.setText(str(self.state.efo_bin_size_hz))
        self.ui.leEFOBinSize.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leEFOExpectedCutoffFrequency.setText(
            str(self.state.efo_expected_frequency)
        )
        self.ui.leEFOExpectedCutoffFrequency.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.cbWeightAvgLocByECO.setChecked(self.state.weigh_avg_localization_by_eco)

        # Set signal-slot connections
        self.setup_conn()

    def setup_conn(self):
        """Set up signal-slot connections."""
        self.ui.leMinTIDNum.textChanged.connect(self.persist_min_num_loc_per_trace)
        self.ui.pbSetDefault.clicked.connect(self.set_as_new_default)
        self.ui.cbWeightAvgLocByECO.stateChanged.connect(
            self.weigh_avg_localization_by_eco
        )
        self.ui.leEFOBinSize.textChanged.connect(self.persist_efo_bin_size_hz)
        self.ui.leEFOExpectedCutoffFrequency.textChanged.connect(
            self.persist_efo_expected_cutoff
        )

    @Slot(str, name="persist_thresh_factor")
    def persist_min_num_loc_per_trace(self, text):
        try:
            min_num_loc_per_trace = int(text)
        except Exception as _:
            return
        self.state.min_num_loc_per_trace = min_num_loc_per_trace

        # Signal the change
        self.min_num_loc_per_trace_option_changed.emit()

    @Slot(str, name="persist_efo_bin_size_hz")
    def persist_efo_bin_size_hz(self, text):
        try:
            efo_bin_size_hz = float(text)
        except Exception as _:
            return
        self.state.efo_bin_size_hz = efo_bin_size_hz

        # Signal the change
        self.efo_bin_size_hz_option_changed.emit()

    @Slot(str, name="persist_efo_expected_cutoff")
    def persist_efo_expected_cutoff(self, text):
        try:
            efo_expected_cutoff = float(text)
        except Exception as _:
            return
        self.state.efo_expected_frequency = efo_expected_cutoff

    @Slot(str, name="weigh_avg_localization_by_eco")
    def weigh_avg_localization_by_eco(self, state):
        self.state.weigh_avg_localization_by_eco = state != 0

        # Signal the change
        self.weigh_avg_localization_by_eco_option_changed.emit()

    @Slot(str, name="set_as_new_default")
    def set_as_new_default(self, text):
        """Persist current selection as new default options."""

        # Read the application settings
        app_settings = QSettings("ch.ethz.bsse.scf", "pyminflux")
        app_settings.setValue(
            "options/min_num_loc_per_trace", str(self.state.min_num_loc_per_trace)
        )
        app_settings.setValue("options/efo_bin_size_hz", self.state.efo_bin_size_hz)
        app_settings.setValue(
            "options/efo_expected_frequency", self.state.efo_expected_frequency
        )
        app_settings.setValue(
            "options/weigh_avg_localization_by_eco",
            self.state.weigh_avg_localization_by_eco,
        )
