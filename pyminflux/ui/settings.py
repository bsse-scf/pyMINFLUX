import os
from PySide6 import QtGui
from PySide6.QtUiTools import QUiLoader

from PySide6.QtCore import Signal, QFile
from PySide6.QtWidgets import QDialog

from analysis.defaults import DEFAULT_FACTOR_AREA, \
    DEFAULT_MAX_PENALTY,  DEFAULT_DRIFT, DEFAULT_JUMP_PENALTY, \
    DEFAULT_MAX_JUMP, DEFAULT_GROWTH_PENALTY, DEFAULT_DISPLACEMENT_PENALTY,\
    DEFAULT_FACTOR_ORIENTATION, DEFAULT_FILTER_SUPPORT, DEFAULT_QC


# Ui_SettingsDlg, QDialog = loadUiType(os.path.join(
#     os.path.dirname(__file__), 'settings_dialog.ui'))


class Settings(QDialog):

    signal_settings_changed = Signal(dict,
                                         name='signal_settings_changed')

    def __init__(self, settings_dictionary, parent=None):
        """
        Constructor.
        """

        # Call the base constructor
        super(Settings, self).__init__()

        # Load the dialog
        loader = QUiLoader()
        ui_file = QFile(os.path.join(os.path.dirname(__file__), 'settings_dialog.ui'))
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

        # self.setupUi(self)

        # Store the reference to the __settings dictionary passed from
        # the caller.
        self.settings_dictionary = settings_dictionary

        # Add validators
        self.leAreaFactor.setValidator(QtGui.QDoubleValidator(bottom=0.0))
        self.leOrientFactor.setValidator(QtGui.QDoubleValidator(bottom=0.0))
        self.leDrift.setValidator(QtGui.QDoubleValidator(bottom=0.0))
        self.leMaxJump.setValidator(QtGui.QIntValidator(bottom=0))
        self.leJumpPenalty.setValidator(QtGui.QDoubleValidator(bottom=0))
        self.leDisplPenalty.setValidator(QtGui.QDoubleValidator(bottom=0.0))
        self.leGrowthPenalty.setValidator(QtGui.QDoubleValidator(bottom=0.0))
        self.leMaxPenalty.setValidator(QtGui.QDoubleValidator(bottom=0.0))
        self.leFilterSupport.setValidator(QtGui.QDoubleValidator(bottom=0.0))

        # Set values
        self.leAreaFactor.setText(
            str(settings_dictionary["factor_area"]))
        self.leOrientFactor.setText(
            str(settings_dictionary["factor_orientation"]))
        self.leDrift.setText(
            str(settings_dictionary["drift"]))
        self.leMaxJump.setText(
            str(settings_dictionary["max_jump"]))
        self.leJumpPenalty.setText(
            str(settings_dictionary["jump_penalty"]))
        self.leDisplPenalty.setText(
            str(settings_dictionary["displacement_penalty"]))
        self.leGrowthPenalty.setText(
            str(settings_dictionary["growth_penalty"]))
        self.leMaxPenalty.setText(
            str(settings_dictionary["max_penalty"]))
        self.leFilterSupport.setText(
            str(settings_dictionary["filter_support"]))
        self.cbQc.setChecked(
            settings_dictionary["qc"])

        # Connection
        self.pbAccept.clicked.connect(self.accept_parameters)
        self.pbDefault.clicked.connect(self.reset_defaults)
        self.pbCancel.clicked.connect(self.reject_parameters)

        # Make it visible
        self.setVisible(True)

    def accept_parameters(self):
        """
        Set the parameters in the dialog into the __settings dictionary.
        :return: void
        """

        # Keep track of whether the settings are changes
        changed = False

        # Fill the dictionary
        factor_area = float(self.leAreaFactor.text())
        if self.settings_dictionary["factor_area"] != factor_area:
            self.settings_dictionary["factor_area"] = factor_area
            changed = True

        factor_orientation = float(self.leOrientFactor.text())
        if self.settings_dictionary["factor_orientation"] != factor_orientation:
            self.settings_dictionary["factor_orientation"] = factor_orientation
            changed = True

        drift = float(self.leDrift.text())
        if self.settings_dictionary["drift"] != drift:
            self.settings_dictionary["drift"] = drift
            changed = True

        max_jump = int(self.leMaxJump.text())
        if self.settings_dictionary["max_jump"] != max_jump:
            self.settings_dictionary["max_jump"] = max_jump
            changed = True

        jump_penalty = float(self.leJumpPenalty.text())
        if self.settings_dictionary["jump_penalty"] != jump_penalty:
            self.settings_dictionary["jump_penalty"] = jump_penalty
            changed = True

        displ_penalty = float(self.leDisplPenalty.text())
        if self.settings_dictionary["displacement_penalty"] != displ_penalty:
            self.settings_dictionary["displacement_penalty"] = displ_penalty
            changed = True

        growth_penalty = float(self.leGrowthPenalty.text())
        if self.settings_dictionary["growth_penalty"] != growth_penalty:
            self.settings_dictionary["growth_penalty"] = growth_penalty
            changed = True

        max_penalty = float(self.leMaxPenalty.text())
        if self.settings_dictionary["max_penalty"] != max_penalty:
            self.settings_dictionary["max_penalty"] = max_penalty
            changed = True

        filter_support = float(self.leFilterSupport.text())
        if self.settings_dictionary["filter_support"] != filter_support:
            self.settings_dictionary["filter_support"] = filter_support
            changed = True

        qc = self.cbQc.isChecked()
        if self.settings_dictionary["qc"] != qc:
            self.settings_dictionary["qc"] = qc
            changed = True

        # Emit a signal
        if changed:
            self.signal_settings_changed.emit(self.settings_dictionary)

        # Close the dialog
        self.close()

    def reset_defaults(self):
        """
        Reset the parameters in the dialog to the default values.
        :return: void
        """

        # Set default values
        self.leAreaFactor.setText(str(DEFAULT_FACTOR_AREA))
        self.leOrientFactor.setText(str(DEFAULT_FACTOR_ORIENTATION))
        self.leDrift.setText(str(DEFAULT_DRIFT))
        self.leMaxJump.setText(str(DEFAULT_MAX_JUMP))
        self.leJumpPenalty.setText(str(DEFAULT_JUMP_PENALTY))
        self.leDisplPenalty.setText(str(DEFAULT_DISPLACEMENT_PENALTY))
        self.leGrowthPenalty.setText(str(DEFAULT_GROWTH_PENALTY))
        self.leMaxPenalty.setText(str(DEFAULT_MAX_PENALTY))
        self.leFilterSupport.setText(str(DEFAULT_FILTER_SUPPORT))
        self.cbQc.setChecked(DEFAULT_QC)

    def reject_parameters(self):
        """
        Discard the parameters in the dialog and close it.
        :return: void
        """
        self.close()

    def closeEvent(self, event):
        """
        QDialog close event
        :param event: a QCloseEvent
        :return:
        """
        self.close()

