from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from pyminflux.state import State

from .ui_wizard import Ui_WizardDialog


class WizardDialog(QDialog, Ui_WizardDialog):

    load_data_triggered = Signal(None, name="load_data_triggered")
    open_unmixer_triggered = Signal(None, name="open_unmixer_triggered")
    open_time_inspector_triggered = Signal(None, name="open_time_inspector_triggered")
    open_analyzer_triggered = Signal(None, name="open_analyzer_triggered")

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

        # Set up connections
        self.setup_conn()

    def setup_conn(self):

        self.ui.pbLoadData.clicked.connect(lambda _: self.load_data_triggered.emit())
        self.ui.pbSingleColor.clicked.connect(lambda _: self.enable_step(2))
        self.ui.pbColorUnmixer.clicked.connect(
            lambda _: self.open_unmixer_triggered.emit()
        )
        self.ui.pbColorUnmixer.clicked.connect(lambda _: self.enable_step(2))
        self.ui.pbTimeInspector.clicked.connect(
            lambda _: self.open_time_inspector_triggered.emit()
        )
        self.ui.pbTimeInspector.clicked.connect(lambda _: self.enable_step(3))
        self.ui.pbAnalyzer.clicked.connect(
            lambda _: self.open_analyzer_triggered.emit()
        )
        self.ui.pbAnalyzer.clicked.connect(lambda _: self.enable_step(5))

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
