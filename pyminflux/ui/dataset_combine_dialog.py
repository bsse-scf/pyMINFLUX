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

"""Dialog for dataset combining options."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
    QDialogButtonBox,
)


class DatasetCombineDialog(QDialog):
    """
    Dialog to ask user whether to combine a new dataset with the currently loaded one.
    """

    # Constants for dialog result
    RESULT_REPLACE = 0
    RESULT_COMBINE_AUTO = 1
    RESULT_COMBINE_MANUAL = 2

    def __init__(self, current_filename: str, new_filename: str, parent=None):
        """
        Constructor.

        Args:
            current_filename: Name of currently loaded file
            new_filename: Name of new file to be loaded
            parent: Parent widget
        """
        super().__init__(parent)

        self.setWindowTitle("Dataset Already Loaded")
        self.setModal(True)
        self.resize(500, 300)

        self._combine_choice = self.RESULT_REPLACE

        # Create layout
        layout = QVBoxLayout()

        # Information label
        info_label = QLabel(
            f"A dataset is already loaded:\n\n"
            f"Current: {current_filename}\n"
            f"New: {new_filename}\n\n"
            f"Would you like to combine the new dataset with the current one?"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        self.button_group = QButtonGroup(self)

        # Replace option
        self.rb_replace = QRadioButton("Replace current dataset with the new one")
        self.rb_replace.setChecked(True)
        self.button_group.addButton(self.rb_replace, self.RESULT_REPLACE)
        options_layout.addWidget(self.rb_replace)

        # Combine with automatic bead correspondence
        self.rb_combine_auto = QRadioButton(
            "Combine datasets (align using beads with matching names)"
        )
        self.button_group.addButton(self.rb_combine_auto, self.RESULT_COMBINE_AUTO)
        options_layout.addWidget(self.rb_combine_auto)

        # Combine with manual bead correspondence
        self.rb_combine_manual = QRadioButton(
            "Combine datasets (manually assign bead correspondences)"
        )
        self.button_group.addButton(self.rb_combine_manual, self.RESULT_COMBINE_MANUAL)
        options_layout.addWidget(self.rb_combine_manual)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Add note about beads
        note_label = QLabel(
            "Note: Dataset combining requires bead localizations (MBM data) "
            "to be available in Zarr files for both datasets."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        layout.addWidget(note_label)

        # Add stretch
        layout.addStretch()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_combine_choice(self) -> int:
        """
        Get the user's choice.

        Returns:
            One of RESULT_REPLACE, RESULT_COMBINE_AUTO, or RESULT_COMBINE_MANUAL
        """
        return self.button_group.checkedId()
