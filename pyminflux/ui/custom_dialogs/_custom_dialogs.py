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
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QVBoxLayout,
    QWidget,
)


class ListDialog(QDialog):
    """Custom dialog that allows selecting an item from a list."""

    def __init__(
        self,
        options: list[str],
        title: str = "Select an option",
        parent: Optional[QWidget] = None,
    ):
        """Constructor.

        Parameters
        ----------

        options: list[str]
            List of options as strings.

        title: str
            Optional title for the dialog.

        parent: QWidget
            Optional parent widget.
        """
        super().__init__(parent)

        self.setWindowTitle(title)

        # Create a layout
        layout = QVBoxLayout()

        # Create a list widget and populate it with the provided options
        self.list_widget = QListWidget()
        self.list_widget.addItems(options)
        # Ensure single selection mode
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        # Add the list widget to the layout
        layout.addWidget(self.list_widget)

        # Create OK and Cancel buttons using QDialogButtonBox
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)

        # Get references to the OK and Cancel buttons
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.cancel_button = button_box.button(QDialogButtonBox.Cancel)

        # Preselect the first option
        self.ok_button.setEnabled(False)
        if options:
            self.list_widget.setCurrentRow(0)
            self.ok_button.setEnabled(True)

        # Connect the dialog buttons to accept and reject methods
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Set the layout for the dialog
        self.setLayout(layout)

        # Adjust the size of the dialog to fit the list widget content
        self.adjust_list_widget_size()

        # Connect the selection changed signal to update the OK button state
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

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
        max_width = 1280
        max_height = 1024

        # Adjust the list widget and dialog size
        self.list_widget.setMinimumHeight(min(total_height, max_height))
        self.list_widget.setMinimumWidth(min(total_width, max_width))
        self.resize(
            self.list_widget.sizeHint().width(), self.list_widget.sizeHint().height()
        )

    def on_selection_changed(self):
        """Enables or disables the OK button based on selection."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def get_selected_option(self):
        """Returns the selected option from the list widget."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def get_selected_index(self):
        """Returns the selected option index from the list widget."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return self.list_widget.row(selected_items[0])
        return -1


class TreeDialog(QDialog):
    def __init__(
        self,
        options: dict,
        title: str = "Select an option",
        parent: Optional[QWidget] = None,
    ):
        """Constructor.

        Parameters
        ----------

        options: dict
            Hierarchical dictionary of options as strings. Any number of levels is possible,
            but only the leaf values will be selectable.
            Example:

                options = {
                    "Child 0": ["Grandchild 0-0", "Grandchild 0-1"],
                    "Child 1": ["Grandchild 1-0"],
                    "Child 2": ["Grandchild 2-0", "Grandchild 2-1", "Grandchild 2-2"],
                    "Child 3": ["Grandchild 3-0", "Grandchild 3-1"],
                    "Child 4": ["Grandchild 4-0"],
                    "Child 5": ["Grandchild 5-0", "Grandchild 5-1"],
                }

        title: str
            Optional title for the dialog.

        parent: QWidget
            Optional parent widget.
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        layout = QVBoxLayout(self)

        # Create the tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)

        # Set the size policy to allow the tree widget to resize appropriately
        self.tree_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize index counter
        self.index_counter = 0

        # Build the tree from the options
        self.build_tree(options, keep_root=False)

        # Expand all items for visibility
        self.tree_widget.expandAll()

        # Add the tree widget to the layout
        layout.addWidget(self.tree_widget)

        # Add OK and Cancel buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        layout.addWidget(self.button_box)

        # Get a reference to the OK button
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        # Initially disable the OK button
        self.ok_button.setEnabled(False)

        # Connect signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Connect the tree widget's selection change signal
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)

        self.selected_item = None  # Initialize selected_item
        self.selected_index = None  # Initialize selected_index

        # Add scrollbars as needed
        self.tree_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Allow the dialog to be resized
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowMinimizeButtonHint
        )

    def build_tree(self, data, keep_root=True):
        """
        Builds the tree from the data dictionary.
        """
        # Initialize index counter
        self.index_counter = 0

        if keep_root:
            root_item = QTreeWidgetItem(["Please select an item"])
            root_item.setFlags(root_item.flags() & ~Qt.ItemIsSelectable)
            self.tree_widget.addTopLevelItem(root_item)

            # Build the items with the root item
            self.build_tree_items(root_item, data)
        else:
            # Add children directly to the top level
            self.build_tree_items(None, data)

    def build_tree_items(self, parent_item, data):
        """Add items to the widget maintaining the whole hierarchy.
        Importantly, only the leaf children will be selectable."""
        for key, value in data.items():
            # Create the child item
            child_item = QTreeWidgetItem([key])

            # Make non-selectable if it has children
            if isinstance(value, (dict, list)):
                child_item.setFlags(child_item.flags() & ~Qt.ItemIsSelectable)
            else:
                child_item.setFlags(child_item.flags() | Qt.ItemIsSelectable)
                child_item.setData(0, Qt.UserRole, self.index_counter)
                self.index_counter += 1

            # Add the item to the parent or as a top-level item
            if parent_item:
                parent_item.addChild(child_item)
            else:
                self.tree_widget.addTopLevelItem(child_item)

            if isinstance(value, dict):
                # Recursively build the tree for nested dictionaries
                self.build_tree_items(child_item, value)
            elif isinstance(value, list):
                # Add child items
                for grandchild in value:
                    grandchild_item = QTreeWidgetItem([grandchild])

                    # Assign index to grandchild_item
                    grandchild_item.setData(0, Qt.UserRole, self.index_counter)
                    self.index_counter += 1

                    # Make grandchild selectable
                    grandchild_item.setFlags(
                        grandchild_item.flags() | Qt.ItemIsSelectable
                    )
                    child_item.addChild(grandchild_item)
            else:
                # Leaf node, already handled
                pass

    def on_selection_changed(self):
        """
        Enables or disables the OK button based on whether a selectable item is selected.
        """
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            # Check if the selected item is selectable
            item = selected_items[0]
            if item.flags() & Qt.ItemIsSelectable:
                self.ok_button.setEnabled(True)
            else:
                self.ok_button.setEnabled(False)
        else:
            self.ok_button.setEnabled(False)

    def accept(self):
        # Get the selected item
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            # Get the selected item
            self.selected_item = selected_items[0]
            # Get the index from the item's data
            self.selected_index = self.selected_item.data(0, Qt.UserRole)
            super().accept()  # Close the dialog
        else:
            # Should not reach here as OK button is disabled when no item is selected
            # Do not call super().accept() to keep the dialog open
            pass

    def adjust_dialog_size(self):
        """Adjusts the dialog size based on the contents of the tree widget."""
        self.tree_widget.expandAll()
        self.tree_widget.resizeColumnToContents(0)

        # Calculate the total width needed
        total_width = self.tree_widget.columnWidth(0) + 20  # Add some padding

        # Calculate the total height needed
        total_height = 0
        iterator = QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            total_height += self.tree_widget.visualItemRect(item).height()
            iterator += 1

        # Add height for horizontal scrollbar if needed
        if total_width > self.tree_widget.viewport().width():
            total_height += self.tree_widget.horizontalScrollBar().height()

        # Add some padding to the height
        total_height += 20

        # Make sure the dialog does not become too large
        max_width = 1280
        max_height = 1024

        # Get the available screen size
        screen_rect = self.screen().availableGeometry()
        max_width = int(min(screen_rect.width() * 0.8, max_width))
        max_height = int(min(screen_rect.height() * 0.8, max_height))

        # Set the tree widget size
        self.tree_widget.setMinimumWidth(min(total_width, max_width))
        self.tree_widget.setMinimumHeight(min(total_height, max_height))

        # Resize the dialog
        self.resize(
            min(total_width, max_width)
            + self.layout().contentsMargins().left()
            + self.layout().contentsMargins().right(),
            min(total_height, max_height)
            + self.button_box.height()
            + self.layout().contentsMargins().top()
            + self.layout().contentsMargins().bottom(),
        )

    def showEvent(self, event):
        """Show the dialog with a minimal delay to allow resizing."""
        super().showEvent(event)
        QTimer.singleShot(0, self.adjust_dialog_size)


EXAMPLE = 2

# Example usage:
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    if EXAMPLE == 1:

        # List of options to display in the combo box
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]

        # Create and show the dialog
        dialog = ListDialog(options)

        if dialog.exec() == QDialog.Accepted:
            selected_option = dialog.get_selected_option()
            print(f"Selected option: {selected_option}")
        else:
            # The dialog was rejected
            print("Dialog canceled.")

    else:

        # Define your options here
        options = {
            "Child 0": ["Grandchild 0-0", "Grandchild 0-1"],
            "Child 1": ["Grandchild 1-0"],
            "Child 2": ["Grandchild 2-0", "Grandchild 2-1", "Grandchild 2-2"],
            "Child 3": ["Grandchild 3-0", "Grandchild 3-1"],
            "Child 4": ["Grandchild 4-0"],
            "Child 5": ["Grandchild 5-0", "Grandchild 5-1"],
        }

        # Create and show the dialog
        dialog = TreeDialog(options=options)

        if dialog.exec() == QDialog.Accepted:
            # The dialog was accepted
            if dialog.selected_item:
                selected_text = dialog.selected_item.text(0)
                selected_index = dialog.selected_index
                print("User selected:", selected_text)
                print("Linear index:", selected_index)
                # Use selected_index as needed
            else:
                print("No item was selected.")
        else:
            # The dialog was rejected
            print("Dialog canceled.")

    sys.exit(app.exec())
