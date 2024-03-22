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
#   limitations under the License.
#
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog

from pyminflux.ui.ui_importer import Ui_Importer


class Importer(QDialog, Ui_Importer):
    """
    A QDialog to support custom loading.
    """

    def __init__(self, valid_cfr, relocalizations, dwell_time):
        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_Importer()
        self.ui.setupUi(self)

        # Store the arguments
        self._num_iterations = len(valid_cfr)
        self._last_valid_cfr = self.find_last_valid_cfr(valid_cfr)
        self._iteration = self._num_iterations - 1
        self._cfr_iteration = self._last_valid_cfr
        self._valid_cfr = valid_cfr
        self._relocalizations = relocalizations
        self._dwell_time = dwell_time

        # Keep track of whether the dataset is a tracking dataset
        self._is_tracking = False

        # Set the dwell time
        self.ui.leDwellTime.setText(f"{self._dwell_time}")

        # Set the tracking checkbox
        self.ui.cbTracking.setChecked(self._is_tracking)

        # Characters
        self.valid_char = "✓"
        self.invalid_char = "⨯"

        # Organize the widgets to hide in lists
        self.widgets_list = [
            (self.ui.pbIter_0, self.ui.lbIter_0, self.ui.lbReloc_0),
            (self.ui.pbIter_1, self.ui.lbIter_1, self.ui.lbReloc_1),
            (self.ui.pbIter_2, self.ui.lbIter_2, self.ui.lbReloc_2),
            (self.ui.pbIter_3, self.ui.lbIter_3, self.ui.lbReloc_3),
            (self.ui.pbIter_4, self.ui.lbIter_4, self.ui.lbReloc_4),
            (self.ui.pbIter_5, self.ui.lbIter_5, self.ui.lbReloc_5),
            (self.ui.pbIter_6, self.ui.lbIter_6, self.ui.lbReloc_6),
            (self.ui.pbIter_7, self.ui.lbIter_7, self.ui.lbReloc_7),
            (self.ui.pbIter_8, self.ui.lbIter_8, self.ui.lbReloc_8),
            (self.ui.pbIter_9, self.ui.lbIter_9, self.ui.lbReloc_9),
            (self.ui.pbIter_10, self.ui.lbIter_10, self.ui.lbReloc_10),
            (self.ui.pbIter_11, self.ui.lbIter_11, self.ui.lbReloc_11),
            (self.ui.pbIter_12, self.ui.lbIter_12, self.ui.lbReloc_12),
            (self.ui.pbIter_13, self.ui.lbIter_13, self.ui.lbReloc_13),
            (self.ui.pbIter_14, self.ui.lbIter_14, self.ui.lbReloc_14),
            (self.ui.pbIter_15, self.ui.lbIter_15, self.ui.lbReloc_15),
        ]

        # Initially hide all buttons and labels
        self.hide_to(self._num_iterations)

        # Set validity flag
        self.set_cfr_validity(self._valid_cfr)

        # Set relocalization flag
        self.set_relocalizations(self._relocalizations)

        # Highlight global _iteration
        self.highlight_iteration(self._num_iterations - 1)

        # Highlight cfr index
        self.highlight_cfr(self._cfr_iteration)

        # Highlight relocalize index
        self.highlight_relocalization(self._cfr_iteration)

        # Adjust the size of the dialog
        self.adjustSize()

        # Set the connections
        self.set_connections()

    def find_last_valid_cfr(self, valid_cfr):
        """Return the index of the last valid CFR measurements."""
        for i in range(len(valid_cfr) - 1, -1, -1):
            if valid_cfr[i]:
                return i
        return None

    def set_connections(self):
        self.ui.leDwellTime.textChanged.connect(self.persist_dwell_time)
        self.ui.cbTracking.stateChanged.connect(self.persist_is_tracking)
        self.ui.pb_last_valid.clicked.connect(self.set_last_valid)
        for i in range(len(self.widgets_list)):
            self.widgets_list[i][0].setProperty("index", i)
            self.widgets_list[i][0].clicked.connect(self.set_all_iterations)

    @Slot(str, name="persist_dwell_time")
    def persist_dwell_time(self, text):
        try:
            dwell_time = float(text)
        except ValueError as _:
            return
        self._dwell_time = dwell_time

    @Slot(int, name="persist_is_tracking")
    def persist_is_tracking(self, state):
        self._is_tracking = state != 0

    @Slot(name="set_last_valid")
    def set_last_valid(self):
        """Set the indices to correspond to the last valid index
        for the general iteration and the cfr iteration."""

        # Reset indices
        self._iteration = self._num_iterations - 1
        self._cfr_iteration = self._last_valid_cfr

        # Reset highlights
        self.reset_colors()

        # Highlight global _iteration
        self.highlight_iteration(self._iteration)

        # Highlight cfr index
        self.highlight_cfr(self._cfr_iteration)

        # Highlight relocalized field
        self.highlight_relocalization(self._cfr_iteration)

    @Slot(int, name="set_all_iterations")
    def set_all_iterations(self, checked):

        # Get the index of the button
        index = self.sender().property("index")

        # Update selections
        self._iteration = index
        self._cfr_iteration = index

        # Reset highlights
        self.reset_colors()

        # Highlight global _iteration
        self.highlight_iteration(index)

        # Highlight cfr index
        self.highlight_cfr(index)

        # Highlight relocalization row
        self.highlight_relocalization(index)

    def get_selection(self) -> dict:
        """Return the selected options."""
        return {
            "iteration": self._iteration,
            "cfr_iteration": self._cfr_iteration,
            "is_tracking": self._is_tracking,
            "dwell_time": self._dwell_time,
        }

    def hide_to(self, to_value: int):
        """Hide all buttons and labels."""
        for i in range(len(self.widgets_list) - 1, to_value - 1, -1):
            self.widgets_list[i][0].setVisible(False)
            self.widgets_list[i][1].setVisible(False)
            self.widgets_list[i][2].setVisible(False)

    def set_cfr_validity(self, cfr_status):
        """Display the validity of the CFR _iteration with the selected characters."""
        for i, status in enumerate(cfr_status):
            self.widgets_list[i][1].setText(
                self.valid_char if status else self.invalid_char
            )

    def set_relocalizations(self, relocalizations):
        """Display the iterations that have relocalizations."""
        for i, status in enumerate(relocalizations):
            self.widgets_list[i][2].setText(
                self.valid_char if status else self.invalid_char
            )

    def reset_colors(self):
        for i in range(len(self.widgets_list) - 1, -1, -1):
            self.widgets_list[i][0].setStyleSheet("")
            self.widgets_list[i][1].setStyleSheet("")
            self.widgets_list[i][2].setStyleSheet("")

    def highlight_iteration(self, iteration):
        """Highlight the button for the global _iteration."""
        self.widgets_list[iteration][0].setStyleSheet(
            "color: black; background-color: lightblue; border-style: flat;"
        )

    def highlight_cfr(self, cfr_index):
        """Highlight the label for the cfr index."""
        self.widgets_list[cfr_index][1].setStyleSheet(
            "color: black; background-color: lightblue;"
        )

    def highlight_relocalization(self, cfr_index):
        """Highlight the relocalized label matching the cfr index."""
        self.widgets_list[cfr_index][2].setStyleSheet(
            "color: black; background-color: lightblue;"
        )
