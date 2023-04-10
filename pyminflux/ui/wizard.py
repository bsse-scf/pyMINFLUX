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
