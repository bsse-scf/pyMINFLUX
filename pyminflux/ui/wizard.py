from PySide6.QtWidgets import QDialog

from pyminflux.state import State

from .ui_wizard import Ui_WizardDialog


class WizardDialog(QDialog, Ui_WizardDialog):
    def __init__(self, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_WizardDialog()
        self.ui.setupUi(self)

        # Keep a reference to the singleton State class
        self.state = State()

        # Enable step 0
        self.enable_step(0)

    def enable_step(self, step: int = 0):

        if step < 0 or step > 5:
            raise ValueError("Step must be between 0 and 4.")

        # The Load data button is always active
        self.ui.pbLoadData.setEnabled(True)

        # Disable all other elements for step 0

        # Color unmixing
        self.ui.pbSingleColor.setEnabled(False)
        self.ui.pbColorUnmixer.setEnabled(False)

        # Time inspector
        self.ui.pbTimeInspector.setEnabled(False)

        # Analyzer
        self.ui.pbAnalyzer.setEnabled(False)

        # EFO filtering
        self.ui.lbEFOFiltering.setEnabled(False)
        self.ui.lbEFOLowerBound.setEnabled(False)
        self.ui.leEFOLowerBound.setEnabled(False)
        self.ui.lbEFOUpperBound.setEnabled(False)
        self.ui.leEFOUpperBound.setEnabled(False)
        self.ui.lbFrequencySingleEmitters.setEnabled(False)
        self.ui.leFrequencySingleEmitters.setEnabled(False)
        self.ui.pbEFOFilter.setEnabled(False)

        # CFR filtering
        self.ui.lbCFRFiltering.setEnabled(False)
        self.ui.lbCFRLowerBound.setEnabled(False)
        self.ui.leCFRLowerBound.setEnabled(False)
        self.ui.lbCFRUpperBound.setEnabled(False)
        self.ui.leCFRUpperBound.setEnabled(False)
        self.ui.lbCFRSigma.setEnabled(False)
        self.ui.leCFRSigma.setEnabled(False)
        self.ui.cbCFRLowerBound.setEnabled(False)
        self.ui.cbCFRUpperBound.setEnabled(False)
        self.ui.pbCFRFilter.setEnabled(False)

        if step == 0:
            return

        # Activate elements for step 1
        self.ui.pbSingleColor.setEnabled(True)
        self.ui.pbColorUnmixer.setEnabled(True)
        if step == 1:
            return

        # Activate elements for step 2
        self.ui.pbTimeInspector.setEnabled(True)
        if step == 2:
            return

        # Activate elements for step 3
        self.ui.pbAnalyzer.setEnabled(True)
        if step == 3:
            return

        # Activate elements for step 4
        self.ui.lbEFOFiltering.setEnabled(True)
        self.ui.lbEFOLowerBound.setEnabled(True)
        self.ui.leEFOLowerBound.setEnabled(True)
        self.ui.lbEFOUpperBound.setEnabled(True)
        self.ui.leEFOUpperBound.setEnabled(True)
        self.ui.lbFrequencySingleEmitters.setEnabled(True)
        self.ui.leFrequencySingleEmitters.setEnabled(True)
        self.ui.pbEFOFilter.setEnabled(True)
        if step == 4:
            return

        # Activate elements for step 5
        self.ui.lbCFRFiltering.setEnabled(True)
        self.ui.lbCFRLowerBound.setEnabled(True)
        self.ui.leCFRLowerBound.setEnabled(True)
        self.ui.lbCFRUpperBound.setEnabled(True)
        self.ui.leCFRUpperBound.setEnabled(True)
        self.ui.lbCFRSigma.setEnabled(True)
        self.ui.leCFRSigma.setEnabled(True)
        self.ui.cbCFRLowerBound.setEnabled(True)
        self.ui.cbCFRUpperBound.setEnabled(True)
        self.ui.pbCFRFilter.setEnabled(True)
