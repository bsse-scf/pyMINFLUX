#  Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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

"""Dialog for naming fluorophores."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
)

from pyminflux.ui.fluorophore_naming_widget import FluorophoreNamingWidget


class FluorophoreNamingDialog(QDialog):
    """
    Dialog to assign names to fluorophore IDs.
    """
    
    def __init__(self, processor, parent=None):
        """
        Constructor.
        
        Args:
            processor: MinFluxProcessor instance with fluorophore data
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.processor = processor
        self.setWindowTitle("Set Channel Names")
        self.setModal(True)
        self.resize(500, 400)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Explanation text
        explanation = QLabel(
            "Assign custom names to your channels for easier identification.\n\n"
            "These names will appear in the active channel selector and will be "
            "saved with your data in PMX files and as comments in CSV exports.\n\n"
            "Click on a name cell to edit it."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; }")
        layout.addWidget(explanation)
        
        # Get fluorophore IDs from processor
        if self.processor.num_fluorophores > 0:
            fluo_ids = sorted(self.processor.processed_dataframe["fluo"].unique().tolist())
            # Filter out fluorophore ID 0 (unassigned/placeholder)
            fluo_ids = [fid for fid in fluo_ids if fid > 0]
        else:
            fluo_ids = []
        
        # Naming widget
        self.naming_widget = FluorophoreNamingWidget(
            title="Channel Names"
        )
        if fluo_ids:
            self.naming_widget.set_fluorophores(fluo_ids, self.processor.fluorophore_names)
        layout.addWidget(self.naming_widget, stretch=1)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_names(self) -> dict:
        """
        Get the fluorophore names from the widget.
        
        Returns:
            Dictionary mapping fluo_id (int) to name (str)
        """
        return self.naming_widget.get_names()
