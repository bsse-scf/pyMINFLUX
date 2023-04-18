#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QDialog, QMessageBox

from pyminflux import __APP_NAME__
from pyminflux.state import State

from ..settings import Settings
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

        # Keep track of the validity of all entries
        self.valid = {
            "leMinTIDNum": True,
            "leEFOBinSize": True,
            "leEFOSingleEmitterFrequency": True,
            "cbWeightAvgLocByECO": True,
            "leEFORangeMin": True,
            "leEFORangeMax": True,
            "leCFRRangeMin": True,
            "leCFRRangeMax": True,
            "leLocPrecRangeMin": True,
            "leLocPrecRangeMax": True,
        }

        # Set defaults
        self.ui.leMinTIDNum.setText(str(self.state.min_num_loc_per_trace))
        self.ui.leMinTIDNum.setValidator(QIntValidator(bottom=0))
        self.ui.leEFOBinSize.setText(str(self.state.efo_bin_size_hz))
        self.ui.leEFOBinSize.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leEFOSingleEmitterFrequency.setText(
            str(self.state.efo_expected_frequency)
        )
        self.ui.leEFOSingleEmitterFrequency.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.cbWeightAvgLocByECO.setChecked(self.state.weigh_avg_localization_by_eco)

        if self.state.efo_range is None:
            self.ui.leEFORangeMin.setText("")
            self.ui.leEFORangeMax.setText("")
        else:
            self.ui.leEFORangeMin.setText(str(self.state.efo_range[0]))
            self.ui.leEFORangeMax.setText(str(self.state.efo_range[1]))
        self.ui.leEFORangeMin.setValidator(QDoubleValidator(bottom=0.0, decimals=1))
        self.ui.leEFORangeMax.setValidator(QDoubleValidator(bottom=0.0, decimals=1))

        if self.state.cfr_range is None:
            self.ui.leCFRRangeMin.setText("")
            self.ui.leCFRRangeMax.setText("")
        else:
            self.ui.leCFRRangeMin.setText(str(self.state.cfr_range[0]))
            self.ui.leCFRRangeMax.setText(str(self.state.cfr_range[1]))
        self.ui.leCFRRangeMin.setValidator(QDoubleValidator(bottom=0.0, decimals=1))
        self.ui.leCFRRangeMax.setValidator(QDoubleValidator(bottom=0.0, decimals=1))

        if self.state.loc_precision_range is None:
            self.ui.leLocPrecRangeMin.setText("")
            self.ui.leLocPrecRangeMax.setText("")
        else:
            self.ui.leLocPrecRangeMin.setText(str(self.state.loc_precision_range[0]))
            self.ui.leLocPrecRangeMax.setText(str(self.state.loc_precision_range[1]))
        self.ui.leLocPrecRangeMin.setValidator(QDoubleValidator(bottom=0.0, decimals=1))
        self.ui.leLocPrecRangeMax.setValidator(QDoubleValidator(bottom=0.0, decimals=1))

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
        self.ui.leEFOSingleEmitterFrequency.textChanged.connect(
            self.persist_efo_expected_cutoff
        )

        self.ui.leCFRRangeMin.textChanged.connect(self.persist_cfr_range)
        self.ui.leCFRRangeMax.textChanged.connect(self.persist_cfr_range)
        self.ui.leEFORangeMin.textChanged.connect(self.persist_efo_range)
        self.ui.leEFORangeMax.textChanged.connect(self.persist_efo_range)
        self.ui.leLocPrecRangeMin.textChanged.connect(self.persist_loc_prec_range)
        self.ui.leLocPrecRangeMax.textChanged.connect(self.persist_loc_prec_range)

    @Slot(str, name="persist_min_num_loc_per_trace")
    def persist_min_num_loc_per_trace(self, text):
        try:
            min_num_loc_per_trace = int(text)
        except Exception as _:
            self.ui.leMinTIDNum.setStyleSheet("background-color: red;")
            self.valid["leMinTIDNum"] = False
            return
        self.ui.leMinTIDNum.setStyleSheet("")
        self.valid["leMinTIDNum"] = True
        self.state.min_num_loc_per_trace = min_num_loc_per_trace

        # Signal the change
        self.min_num_loc_per_trace_option_changed.emit()

    @Slot(str, name="persist_efo_bin_size_hz")
    def persist_efo_bin_size_hz(self, text):
        try:
            efo_bin_size_hz = float(text)
        except Exception as _:
            self.ui.leEFOBinSize.setStyleSheet("background-color: red;")
            self.valid["hlEFOBinSize"] = False
            return
        self.ui.leEFOBinSize.setStyleSheet("")
        self.valid["hlEFOBinSize"] = True
        self.state.efo_bin_size_hz = efo_bin_size_hz

        # Signal the change
        self.efo_bin_size_hz_option_changed.emit()

    @Slot(str, name="persist_efo_expected_cutoff")
    def persist_efo_expected_cutoff(self, text):
        try:
            efo_expected_frequency = float(text)
        except Exception as _:
            self.ui.leEFOSingleEmitterFrequency.setStyleSheet("background-color: red;")
            self.valid["leEFOSingleEmitterFrequency"] = False
            return
        self.ui.leEFOSingleEmitterFrequency.setStyleSheet("")
        self.valid["leEFOSingleEmitterFrequency"] = True
        self.state.efo_expected_frequency = efo_expected_frequency

    @Slot(str, name="persist_cfr_range")
    def persist_cfr_range(self, _):
        cfr_min = self.ui.leCFRRangeMin.text()
        if cfr_min == "":
            self.ui.leCFRRangeMin.setStyleSheet("background-color: red;")
            self.valid["leCFRRangeMin"] = False
        else:
            cfr_min = float(cfr_min)
            self.ui.leCFRRangeMin.setStyleSheet("")
            self.valid["leCFRRangeMin"] = True

        cfr_max = self.ui.leCFRRangeMax.text()
        if cfr_max == "":
            self.ui.leCFRRangeMax.setStyleSheet("background-color: red;")
            self.valid["leCFRRangeMax"] = False
        else:
            cfr_max = float(cfr_max)
            self.ui.leCFRRangeMax.setStyleSheet("")
            self.valid["leCFRRangeMax"] = True

        # If both values are not empty, check if min_value is greater than max_value
        if cfr_min != "" and cfr_max != "":
            try:
                if float(cfr_min) > float(cfr_max):
                    self.ui.leCFRRangeMin.setStyleSheet("background-color: red;")
                    self.valid["leCFRRangeMin"] = False
            except ValueError:
                # If the input is not a valid number, set the background to red
                self.ui.leCFRRangeMin.setStyleSheet("background-color: red;")
                self.valid["leCFRRangeMin"] = False
                self.ui.leCFRRangeMax.setStyleSheet("background-color: red;")
                self.valid["leCFRRangeMax"] = False

        if cfr_min != "" and cfr_max != "" and cfr_min < cfr_max:
            self.state.cfr_range = (cfr_min, cfr_max)
            self.valid["leCFRRangeMin"] = True
            self.valid["leCFRRangeMax"] = True

    @Slot(str, name="persist_efo_range")
    def persist_efo_range(self, _):
        efo_min = self.ui.leEFORangeMin.text()
        if efo_min == "":
            self.ui.leEFORangeMin.setStyleSheet("background-color: red;")
            self.valid["leEFORangeMin"] = False
        else:
            efo_min = float(efo_min)
            self.ui.leEFORangeMin.setStyleSheet("")
            self.valid["leEFORangeMin"] = True

        efo_max = self.ui.leEFORangeMax.text()
        if efo_max == "":
            self.ui.leEFORangeMax.setStyleSheet("background-color: red;")
            self.valid["leEFORangeMax"] = False
        else:
            efo_max = float(efo_max)
            self.ui.leEFORangeMax.setStyleSheet("")
            self.valid["leEFORangeMax"] = True

        # If both values are not empty, check if min_value is greater than max_value
        if efo_min != "" and efo_max != "":
            try:
                if float(efo_min) > float(efo_max):
                    self.ui.leEFORangeMin.setStyleSheet("background-color: red;")
                    self.valid["leEFORangeMax"] = False
            except ValueError:
                # If the input is not a valid number, set the background to red
                self.ui.leEFORangeMin.setStyleSheet("background-color: red;")
                self.valid["leEFORangeMax"] = False
                self.ui.leEFORangeMax.setStyleSheet("background-color: red;")
                self.valid["leEFORangeMax"] = False

        if efo_min != "" and efo_max != "" and efo_min < efo_max:
            self.state.efo_range = (efo_min, efo_max)
            self.valid["leEFORangeMin"] = True
            self.valid["leEFORangeMax"] = True

    @Slot(str, name="persist_loc_prec_range")
    def persist_loc_prec_range(self, _):
        loc_prec_min = self.ui.leLocPrecRangeMin.text()
        if loc_prec_min == "":
            self.ui.leLocPrecRangeMin.setStyleSheet("background-color: red;")
            self.valid["leLocPrecRangeMin"] = False
        else:
            loc_prec_min = float(loc_prec_min)
            self.ui.leLocPrecRangeMin.setStyleSheet("")
            self.valid["leLocPrecRangeMin"] = True

        loc_prec_max = self.ui.leLocPrecRangeMax.text()
        if loc_prec_max == "":
            self.ui.leLocPrecRangeMax.setStyleSheet("background-color: red;")
            self.valid["leLocPrecRangeMax"] = False
        else:
            loc_prec_max = float(loc_prec_max)
            self.ui.leLocPrecRangeMax.setStyleSheet("")
            self.valid["leLocPrecRangeMax"] = True

        # If both values are not empty, check if min_value is greater than max_value
        if loc_prec_min != "" and loc_prec_max != "":
            try:
                if float(loc_prec_min) > float(loc_prec_max):
                    self.ui.leLocPrecRangeMin.setStyleSheet("background-color: red;")
                    self.valid["leLocPrecRangeMin"] = False
            except ValueError:
                # If the input is not a valid number, set the background to red
                self.ui.leLocPrecRangeMin.setStyleSheet("background-color: red;")
                self.valid["leLocPrecRangeMin"] = False
                self.ui.leLocPrecRangeMax.setStyleSheet("background-color: red;")
                self.valid["leLocPrecRangeMax"] = False

        if loc_prec_min != "" and loc_prec_max != "" and loc_prec_min < loc_prec_max:
            self.state.loc_precision_range = (loc_prec_min, loc_prec_max)
            self.valid["leLocPrecRangeMin"] = True
            self.valid["leLocPrecRangeMax"] = True

    @Slot(str, name="weigh_avg_localization_by_eco")
    def weigh_avg_localization_by_eco(self, state):
        self.state.weigh_avg_localization_by_eco = state != 0

        # Signal the change
        self.weigh_avg_localization_by_eco_option_changed.emit()

    @Slot(str, name="set_as_new_default")
    def set_as_new_default(self, text):
        """Persist current selection as new default options."""

        # Only save if all fields are properly set
        all_true = all(self.valid.values())

        if not all_true:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Please fix all invalid entries before saving!")
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec_()
            return

        # Update the application settings
        settings = Settings()
        settings.instance.setValue(
            "options/min_num_loc_per_trace", int(self.state.min_num_loc_per_trace)
        )
        settings.instance.setValue(
            "options/efo_bin_size_hz", float(self.state.efo_bin_size_hz)
        )
        settings.instance.setValue(
            "options/efo_expected_frequency", float(self.state.efo_expected_frequency)
        )
        settings.instance.setValue(
            "options/weigh_avg_localization_by_eco",
            self.state.weigh_avg_localization_by_eco,
        )
        settings.instance.setValue("options/efo_range", list(self.state.efo_range))
        settings.instance.setValue("options/cfr_range", list(self.state.cfr_range))
        settings.instance.setValue(
            "options/loc_precision_range", list(self.state.loc_precision_range)
        )

    def closeEvent(self, event):
        """Make sure to call the parent closeEvent()."""
        super().closeEvent(event)
