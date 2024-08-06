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
#  limitations under the License.

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QDialog, QMessageBox

from pyminflux.state import State

from ..settings import Settings
from .ui_options import Ui_Options


class Options(QDialog, Ui_Options):
    # Signal that the options have changed
    min_trace_length_option_changed = Signal()
    efo_bin_size_hz_option_changed = Signal()
    weigh_avg_localization_by_eco_option_changed = Signal()

    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_Options()
        self.ui.setupUi(self)

        # Keep a reference to the singleton State class
        self.state = State()

        # Add the help text edit
        self.ui.teHelp.setReadOnly(True)
        font_metrics = self.ui.teHelp.fontMetrics()
        self.ui.teHelp.setMaximumHeight(font_metrics.height() * 3)
        self.ui.teHelp.setText('Click on a "?" button to get help.')

        # Hide the border and change the background color
        self.ui.teHelp.setStyleSheet(
            """
            QTextEdit {
                border: none;
                background-color: transparent;
                font-style: italic;
            }
        """
        )

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
            "leZScalingFactor": True,
            "lePlotExportDPI": True,
        }

        # Set defaults
        self.ui.leMinTIDNum.setText(str(self.state.min_trace_length))
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

        self.ui.leZScalingFactor.setText(str(self.state.z_scaling_factor))
        self.ui.leZScalingFactor.setValidator(QDoubleValidator(bottom=0.0, decimals=2))

        self.ui.lePlotExportDPI.setText(str(self.state.plot_export_dpi))
        self.ui.lePlotExportDPI.setValidator(QIntValidator(bottom=72))

        self.ui.cbOpenConsoleAtStart.setChecked(self.state.open_console_at_start)

        # Set signal-slot connections
        self.setup_conn()

    def setup_conn(self):
        """Set up signal-slot connections."""
        self.ui.leMinTIDNum.textChanged.connect(self.persist_min_trace_length)
        self.ui.pbSetDefault.clicked.connect(self.set_as_new_default)
        self.ui.cbWeightAvgLocByECO.stateChanged.connect(
            self.persist_weigh_avg_localization_by_eco
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

        self.ui.leZScalingFactor.textChanged.connect(self.persist_z_scaling_factor)

        self.ui.lePlotExportDPI.textChanged.connect(self.persist_plot_export_dpi)

        self.ui.cbOpenConsoleAtStart.stateChanged.connect(
            self.persist_open_console_at_start
        )

        self.ui.pbMinTIDNumHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Minimum number of localizations within a trace to be considered for "
                "plotting and precision calculation."
            )
        )
        self.ui.pbZScalingFactorHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Scales the z positions to compensate for the refractive index mismatch "
                "between the coverglass and the sample."
            )
        )
        self.ui.pbEFOBinSizeHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Bin size to be used for EFO distribution plotting on the Analyzer. "
                "Set to 0 for automatic estimation."
            )
        )
        self.ui.pbEFOSingleEmitterFrequencyHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Expected default frequency for single emitters to be used for automated "
                "EFO threshold selection."
            )
        )
        self.ui.pbEFORangeHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Default plot range for the EFO histogram in the Analyzer."
            )
        )
        self.ui.pbCFRRangeHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Default plot range for the CFR histogram in the Analyzer."
            )
        )
        self.ui.pbLocPrecRangeHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Default plot range for the localization precision histograms in the Analyzer."
            )
        )
        self.ui.pbWeightAvgLocByECOHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Whether to use the ECO value as weighting factor during the calculation of the "
                "average localization position for each trace ID."
            )
        )
        self.ui.pbPlotExportDPIHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Resolution (in dots per inch) for the all plots when exported as .png images."
            )
        )
        self.ui.pbOpenConsoleAtStartHelp.clicked.connect(
            lambda _: self.ui.teHelp.setText(
                "Whether to open the console at application start."
            )
        )

    @Slot(str)
    def persist_min_trace_length(self, text):
        try:
            min_trace_length = int(text)
        except Exception as _:
            self.ui.leMinTIDNum.setStyleSheet("background-color: red;")
            self.valid["leMinTIDNum"] = False
            return
        self.ui.leMinTIDNum.setStyleSheet("")
        self.valid["leMinTIDNum"] = True
        self.state.min_trace_length = min_trace_length

        # Signal the change
        self.min_trace_length_option_changed.emit()

    @Slot(str)
    def persist_z_scaling_factor(self, text):
        try:
            z_scaling_factor = float(text)
        except Exception as _:
            self.ui.leZScalingFactor.setStyleSheet("background-color: red;")
            self.valid["leZScalingFactor"] = False
            return
        self.ui.leZScalingFactor.setStyleSheet("")
        self.valid["leZScalingFactor"] = True
        self.state.z_scaling_factor = z_scaling_factor

    @Slot(str)
    def persist_plot_export_dpi(self, text):
        try:
            plot_export_dpi = int(text)
        except Exception as _:
            self.ui.lePlotExportDPI.setStyleSheet("background-color: red;")
            self.valid["lePlotExportDPI"] = False
            return
        self.ui.lePlotExportDPI.setStyleSheet("")
        self.valid["lePlotExportDPI"] = True
        self.state.plot_export_dpi = plot_export_dpi

    @Slot(str)
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

    @Slot(str)
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

    @Slot(str)
    def persist_cfr_range(self, _):
        """Persist CFR range."""

        # Initialize the status to valid
        self.valid["leCFRRangeMin"] = True
        self.valid["leCFRRangeMax"] = True

        # Get current values
        cfr_min = self.ui.leCFRRangeMin.text()
        cfr_max = self.ui.leCFRRangeMax.text()

        # Validate them
        cfr_min = self._validate(cfr_min, self.ui.leCFRRangeMin)
        cfr_max = self._validate(cfr_max, self.ui.leCFRRangeMax)

        # Check that min and max values are consistent
        if cfr_min != "" and cfr_max != "":
            if cfr_min < cfr_max:
                self.state.cfr_range = (cfr_min, cfr_max)
                stylesheet = ""
            else:
                stylesheet = "background-color: red;"
                self.valid["leCFRRangeMin"] = False
                self.valid["leCFRRangeMax"] = False
                self.state.cfr_range = None
            self.ui.leCFRRangeMin.setStyleSheet(stylesheet)
            self.ui.leCFRRangeMax.setStyleSheet(stylesheet)
        elif cfr_min == "" and cfr_max == "":
            self.state.cfr_range = None
        else:
            self.state.cfr_range = None
            if cfr_min == "":
                self.ui.leCFRRangeMin.setStyleSheet("background-color: red;")
                self.valid["leCFRRangeMin"] = False
            if cfr_max == "":
                self.ui.leCFRRangeMax.setStyleSheet("background-color: red;")
                self.valid["leCFRRangeMax"] = False

    @Slot(str)
    def persist_efo_range(self, _):
        """Persist EFO range."""

        # Initialize the status to valid
        self.valid["leEFORangeMin"] = True
        self.valid["leEFORangeMax"] = True

        # Get current values
        efo_min = self.ui.leEFORangeMin.text()
        efo_max = self.ui.leEFORangeMax.text()

        # Validate them
        efo_min = self._validate(efo_min, self.ui.leEFORangeMin)
        efo_max = self._validate(efo_max, self.ui.leEFORangeMax)

        # Check that min and max values are consistent
        if efo_min != "" and efo_max != "":
            if efo_min < efo_max:
                self.state.efo_range = (efo_min, efo_max)
                stylesheet = ""
            else:
                stylesheet = "background-color: red;"
                self.valid["leEFORangeMin"] = False
                self.valid["leEFORangeMax"] = False
                self.state.efo_range = None
            self.ui.leEFORangeMin.setStyleSheet(stylesheet)
            self.ui.leEFORangeMax.setStyleSheet(stylesheet)
        elif efo_min == "" and efo_max == "":
            self.state.efo_range = None
        else:
            self.state.efo_range = None
            if efo_min == "":
                self.ui.leEFORangeMin.setStyleSheet("background-color: red;")
                self.valid["leEFORangeMin"] = False
            if efo_max == "":
                self.ui.leEFORangeMax.setStyleSheet("background-color: red;")
                self.valid["leEFORangeMax"] = False

    @Slot(str)
    def persist_loc_prec_range(self, _):
        """Persist localization precision range."""

        # Initialize the status to valid
        self.valid["leLocPrecRangeMin"] = True
        self.valid["leLocPrecRangeMax"] = True

        # Get current values
        loc_prec_min = self.ui.leLocPrecRangeMin.text()
        loc_prec_max = self.ui.leLocPrecRangeMax.text()

        # Validate them
        loc_prec_min = self._validate(loc_prec_min, self.ui.leLocPrecRangeMin)
        loc_prec_max = self._validate(loc_prec_max, self.ui.leLocPrecRangeMax)

        # Check that min and max values are consistent
        if loc_prec_min != "" and loc_prec_max != "":
            if loc_prec_min < loc_prec_max:
                self.state.loc_precision_range = (loc_prec_min, loc_prec_max)
                stylesheet = ""
            else:
                stylesheet = "background-color: red;"
                self.valid["leLocPrecRangeMin"] = False
                self.valid["leLocPrecRangeMax"] = False
                self.state.loc_precision_range = None
            self.ui.leLocPrecRangeMin.setStyleSheet(stylesheet)
            self.ui.leLocPrecRangeMax.setStyleSheet(stylesheet)
        elif loc_prec_min == "" and loc_prec_max == "":
            self.state.loc_precision_range = None
        else:
            self.state.loc_precision_range = None
            if loc_prec_min == "":
                self.ui.leLocPrecRangeMin.setStyleSheet("background-color: red;")
                self.valid["leLocPrecRangeMin"] = False
            if loc_prec_max == "":
                self.ui.leLocPrecRangeMax.setStyleSheet("background-color: red;")
                self.valid["leLocPrecRangeMax"] = False

    @Slot(str)
    def persist_weigh_avg_localization_by_eco(self, state):
        self.state.weigh_avg_localization_by_eco = state != 0

        # Signal the change
        self.weigh_avg_localization_by_eco_option_changed.emit()

    @Slot(str)
    def persist_open_console_at_start(self, state):
        self.state.open_console_at_start = state != 0

    @Slot(str)
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
            "options/min_trace_length", int(self.state.min_trace_length)
        )
        settings.instance.setValue(
            "options/z_scaling_factor", float(self.state.z_scaling_factor)
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
        if self.state.efo_range is None:
            settings.instance.setValue("options/efo_range", "None")
        else:
            settings.instance.setValue("options/efo_range", list(self.state.efo_range))
        if self.state.cfr_range is None:
            settings.instance.setValue("options/cfr_range", "None")
        else:
            settings.instance.setValue("options/cfr_range", list(self.state.cfr_range))
        if self.state.loc_precision_range is None:
            settings.instance.setValue("options/loc_precision_range", "None")
        else:
            settings.instance.setValue(
                "options/loc_precision_range", list(self.state.loc_precision_range)
            )
        settings.instance.setValue(
            "options/open_console_at_start",
            self.state.open_console_at_start,
        )
        settings.instance.setValue(
            "options/plot_export_dpi", int(self.state.plot_export_dpi)
        )

        # This property was superseded by "options/min_trace_length"
        if settings.instance.contains("options/min_num_loc_per_trace"):
            settings.instance.remove("options/min_num_loc_per_trace")

        # Sync the settings with file
        settings.instance.sync()

    def _validate(self, value, line_edit):
        """Check that the value in the QLineEdit is a valid float, or reset it and visually mark it otherwise."""
        if value == "":
            line_edit.setStyleSheet("")
            return value

        try:
            value = float(value)
            line_edit.setStyleSheet("")
        except ValueError:
            value = ""
            line_edit.setText("")
            line_edit.setStyleSheet("background-color: red;")
        return value
