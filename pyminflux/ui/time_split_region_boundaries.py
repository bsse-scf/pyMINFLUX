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

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class TimeSplitRegionBoundariesDialog(QDialog):
    """Dialog to set exact boundaries for a time split region."""

    def __init__(self, start_value: float, end_value: float, parent=None):
        """Constructor.
        
        Parameters
        ----------
        start_value : float
            Current start value of the region (in minutes).
        end_value : float
            Current end value of the region (in minutes).
        parent : QWidget, optional
            Parent widget.
        """
        super().__init__(parent)
        
        self.setWindowTitle("Set Region Boundaries")
        self.setModal(True)
        
        # Store original values
        self.start_value = start_value
        self.end_value = end_value
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add info label
        info_label = QLabel("Set exact boundaries for this time region (in minutes):")
        layout.addWidget(info_label)
        
        # Create form layout for inputs
        form_layout = QFormLayout()
        
        # Start value input
        self.start_input = QLineEdit()
        self.start_input.setValidator(QDoubleValidator(decimals=2))
        self.start_input.setText(f"{start_value:.2f}")
        form_layout.addRow("Start (min):", self.start_input)
        
        # End value input
        self.end_input = QLineEdit()
        self.end_input.setValidator(QDoubleValidator(decimals=2))
        self.end_input.setText(f"{end_value:.2f}")
        form_layout.addRow("End (min):", self.end_input)
        
        layout.addLayout(form_layout)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set minimum width
        self.setMinimumWidth(300)
    
    def get_values(self):
        """Get the entered start and end values.
        
        Returns
        -------
        tuple
            (start, end) values as floats, or None if invalid.
        """
        try:
            start = float(self.start_input.text())
            end = float(self.end_input.text())
            
            # Ensure start < end
            if start >= end:
                return None
            
            return (start, end)
        except ValueError:
            return None
