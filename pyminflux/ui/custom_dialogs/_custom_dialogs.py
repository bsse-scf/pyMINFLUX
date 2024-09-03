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

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)


class ListDialog(QDialog):
    def __init__(
        self, options: list[str], title: str = "Select an option", parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(title)

        # Create a layout
        layout = QVBoxLayout()

        # Create a list widget and populate it with the provided options
        self.list_widget = QListWidget()
        self.list_widget.addItems(options)

        # Add the combo box to the layout
        layout.addWidget(self.list_widget)

        # Add an OK button to confirm selection
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(
            self.accept
        )  # Closes the dialog and accepts the input

        layout.addWidget(ok_button)

        # Set the layout for the dialog
        self.setLayout(layout)

        # Adjust the size of the dialog to fit the list widget content
        self.adjust_list_widget_size()

    def adjust_list_widget_size(self):
        """Adjusts the dialog size based on the contents of the list widget."""
        # Calculate the required height and width to fit all items
        total_height = (
            self.list_widget.sizeHintForRow(0) * self.list_widget.count()
            + 2 * self.list_widget.frameWidth()
        )
        total_width = (
            self.list_widget.sizeHintForColumn(0) + 2 * self.list_widget.frameWidth()
        )

        # Make sure the dialog does not become too large
        max_height = 1280
        max_width = 1024

        # Adjust the list widget and dialog size
        self.list_widget.setMinimumHeight(min(total_height, max_height))
        self.list_widget.setMinimumWidth(min(total_width, max_width))
        self.resize(
            self.list_widget.sizeHint().width(), self.list_widget.sizeHint().height()
        )

    def get_selected_option(self):
        """Returns the selected option from the combo box."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def get_selected_index(self):
        """Returns the selected option index from the combo box."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return self.list_widget.row(selected_items[0])
        return -1


# Example usage:
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # List of options to display in the combo box
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]

    # Create and show the dialog
    dialog = ListDialog(options)

    if dialog.exec_() == QDialog.Accepted:
        selected_option = dialog.get_selected_option()
        print(f"Selected option: {selected_option}")

    sys.exit(app.exec_())
