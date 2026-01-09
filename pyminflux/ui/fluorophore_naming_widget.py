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

"""Reusable widget for naming fluorophores."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
)
from pyminflux.ui.colors import Colors


class FluorophoreNamingWidget(QWidget):
    """
    Reusable widget displaying a table for naming fluorophores.
    
    The table has two columns:
    - Fluo ID: Non-editable column showing the fluorophore ID
    - Name: Editable column for entering custom fluorophore names
    """
    
    def __init__(self, title: str = "Fluorophore Names", parent=None):
        """
        Constructor.
        
        Args:
            title: Title label to display above the table
            parent: Parent widget
        """
        super().__init__(parent)
        
        self._fluo_ids = []
        self._setup_ui(title)
    
    def _setup_ui(self, title: str):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Set size policy to prevent widget from expanding unnecessarily
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Fluo ID", "Name (click to edit)"])
        
        # Configure table
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        
        # Set tooltip to clarify editability
        self.table.setToolTip("Click on a Name cell to edit the fluorophore name")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        # Scrollbar policy will be set dynamically based on content size
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def set_fluorophores(self, fluo_ids: list, existing_names: dict = None):
        """
        Set the fluorophore IDs to display and optionally their existing names.
        
        Args:
            fluo_ids: List of fluorophore IDs (integers)
            existing_names: Optional dictionary mapping fluo_id -> name
        """
        self._fluo_ids = sorted(fluo_ids)
        existing_names = existing_names or {}
        
        # Clear and set row count
        self.table.setRowCount(len(self._fluo_ids))
        
        # Populate table
        for row, fluo_id in enumerate(self._fluo_ids):
            # Get the color for this fluorophore ID
            color_rgb = Colors()._get_fid_color(fluo_id, as_float=False)
            bg_color = QColor(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 80)  # Semi-transparent
            
            # Fluo ID column (non-editable)
            id_item = QTableWidgetItem(str(fluo_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setBackground(bg_color)
            self.table.setItem(row, 0, id_item)
            
            # Name column (editable)
            default_name = existing_names.get(fluo_id, str(fluo_id))
            name_item = QTableWidgetItem(default_name)
            name_item.setData(Qt.ItemDataRole.UserRole, fluo_id)  # Store fluo_id for retrieval
            name_item.setBackground(bg_color)
            name_item.setToolTip("Click to edit this fluorophore name")
            self.table.setItem(row, 1, name_item)
        
        # Resize table to fit content
        self._resize_table_to_content()
    
    def _resize_table_to_content(self):
        """Resize the table widget to fit its content without wasting space."""
        if self.table.rowCount() == 0:
            self.table.setFixedHeight(50)  # Minimal height when empty
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            return
        
        # Calculate required height: header + all rows + small margin
        header_height = self.table.horizontalHeader().height()
        row_height = sum(self.table.rowHeight(i) for i in range(self.table.rowCount()))
        margin = 4  # Small margin for borders/spacing
        
        total_height = header_height + row_height + margin
        
        # Set maximum height threshold (about 8 rows worth of content)
        max_height = 250
        
        if total_height > max_height:
            # Content exceeds threshold - use max height and enable scrollbar
            self.table.setFixedHeight(max_height)
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            # Content fits - use exact height and disable scrollbar
            self.table.setFixedHeight(total_height)
            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def get_names(self) -> dict:
        """
        Get the fluorophore names from the table.
        
        Returns:
            Dictionary mapping fluo_id (int) to name (str)
        """
        names = {}
        for row in range(self.table.rowCount()):
            fluo_id_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            
            if fluo_id_item and name_item:
                fluo_id = int(fluo_id_item.text())
                name = name_item.text().strip()
                # Use text if provided, otherwise use string representation of ID
                names[fluo_id] = name if name else str(fluo_id)
        
        return names
    
    def set_title(self, title: str):
        """Update the title label."""
        self.title_label.setText(title)
    
    def clear(self):
        """Clear the table."""
        self.table.setRowCount(0)
        self._fluo_ids = []
