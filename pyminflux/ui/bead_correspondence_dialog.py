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

"""Dialog for manual bead correspondence assignment."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QHeaderView,
    QGroupBox,
    QSplitter,
    QWidget,
)


class BeadCorrespondenceDialog(QDialog):
    """
    Dialog for manually assigning bead correspondences between two datasets.
    """
    
    def __init__(
        self, 
        reference_beads: Dict[str, np.ndarray],
        moving_beads: Dict[str, np.ndarray],
        auto_match: bool = False,
        parent=None
    ):
        """
        Constructor.
        
        Args:
            reference_beads: Dict mapping bead names to their positions [z, y, x] in current (reference) dataset
            moving_beads: Dict mapping bead names to their positions [z, y, x] in new (moving) dataset
            auto_match: If True, automatically match beads by name on initialization
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Assign Bead Correspondences")
        self.setModal(True)
        self.resize(1400, 800)
        
        self.current_beads = reference_beads  # Current dataset (reference for alignment)
        self.new_beads = moving_beads  # New dataset (will be transformed)
        self.correspondence = {}  # Will store new_name -> current_name mapping
        
        # Store plot items for interactive highlighting
        self.current_scatter_items = {}  # bead_name -> scatter plot item
        self.new_scatter_items = {}  # bead_name -> scatter plot item
        self.correspondence_lines = {}  # new_name -> line item
        
        self._setup_ui()
        self._populate_tables()
        self._plot_beads()
        
        # Auto-match by name if requested
        if auto_match:
            self._auto_match_by_name()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Match each bead in the current dataset (red circles) with the corresponding bead "
            "in the new dataset (blue squares). Use the dropdown in each row to select the match. "
            "Lines in the plot show assigned correspondences."
        )
        instructions.setWordWrap(True)
        instructions.setToolTip(
            "Click on beads in the plot or select them in the table to assign matches. "
            "Green dashed lines connect matched beads."
        )
        main_layout.addWidget(instructions)
        
        # Create main horizontal splitter
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Plot view
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0, 0, 0, 0)
        
        plot_label = QLabel("<b>Bead Positions (XY view)</b>")
        plot_layout.addWidget(plot_label)
        
        # Create pyqtgraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setLabel('left', 'Y', units='nm')
        self.plot_widget.setLabel('bottom', 'X', units='nm')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()
        
        plot_layout.addWidget(self.plot_widget)
        plot_widget.setLayout(plot_layout)
        h_splitter.addWidget(plot_widget)
        
        # Right side: Single table
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_layout.addWidget(QLabel("<b>Bead Correspondence Assignments</b>"))
        
        # Single correspondence table
        self.correspondence_table = QTableWidget()
        self.correspondence_table.setColumnCount(2)
        self.correspondence_table.setHorizontalHeaderLabels(
            ["Current Dataset Bead (Red)", "→ Matches New Dataset Bead (Blue)"]
        )
        self.correspondence_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.correspondence_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.correspondence_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.correspondence_table.setToolTip(
            "For each current bead (red), select which new bead (blue) it corresponds to"
        )
        self.correspondence_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        table_layout.addWidget(self.correspondence_table)
        
        table_widget.setLayout(table_layout)
        h_splitter.addWidget(table_widget)
        
        # Set splitter proportions (plot gets more space)
        h_splitter.setSizes([700, 500])
        
        main_layout.addWidget(h_splitter)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        
        auto_match_btn = QPushButton("Auto-match by name")
        auto_match_btn.setToolTip("Automatically match beads that have identical names in both datasets")
        auto_match_btn.clicked.connect(self._auto_match_by_name)
        buttons_layout.addWidget(auto_match_btn)
        
        clear_btn = QPushButton("Clear all matches")
        clear_btn.setToolTip("Remove all current bead correspondences")
        clear_btn.clicked.connect(self._clear_all_matches)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("QLabel { color: #666; }")
        main_layout.addWidget(self.status_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
    def _populate_tables(self):
        """Populate the correspondence table."""
        # Populate with current dataset beads (one row per bead)
        self.correspondence_table.setRowCount(len(self.current_beads))
        self.correspondence_combos = {}
        
        for row, (current_bead_name, pos) in enumerate(sorted(self.current_beads.items())):
            # Current bead name (first column)
            name_item = QTableWidgetItem(current_bead_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.correspondence_table.setItem(row, 0, name_item)
            
            # Correspondence combo box (second column) - maps to new dataset beads
            combo = QComboBox()
            combo.addItem("-- None --", None)
            for new_name in sorted(self.new_beads.keys()):
                combo.addItem(new_name, new_name)
            combo.currentIndexChanged.connect(self._update_correspondence)
            self.correspondence_table.setCellWidget(row, 1, combo)
            self.correspondence_combos[current_bead_name] = combo
        
        self._update_status()
    
    def _plot_beads(self):
        """Plot bead positions in XY space."""
        # Store text items for labels
        self.text_items = []
        
        # Flag to track if legend items have been added
        current_added_to_legend = False
        new_added_to_legend = False
        
        # Plot current dataset beads (red circles)
        for bead_name, pos in self.current_beads.items():
            # pos is [z, y, x]
            scatter = pg.ScatterPlotItem(
                [pos[2]],  # x
                [pos[1]],  # y
                size=10,
                pen=pg.mkPen(color='r', width=2),
                brush=pg.mkBrush(255, 100, 100, 150),
                symbol='o',
                name='Current dataset' if not current_added_to_legend else None
            )
            scatter.setData([pos[2]], [pos[1]], data=[bead_name])
            scatter.sigClicked.connect(self._on_current_point_clicked)
            self.plot_widget.addItem(scatter)
            self.current_scatter_items[bead_name] = scatter
            current_added_to_legend = True
            
            # Add text label
            text = pg.TextItem(text=bead_name, color=(200, 0, 0), anchor=(0.5, 1.5))
            text.setPos(pos[2], pos[1])
            self.plot_widget.addItem(text)
            self.text_items.append(text)
        
        # Plot new dataset beads (blue squares)
        for bead_name, pos in self.new_beads.items():
            # pos is [z, y, x]
            scatter = pg.ScatterPlotItem(
                [pos[2]],  # x
                [pos[1]],  # y
                size=10,
                pen=pg.mkPen(color='b', width=2),
                brush=pg.mkBrush(100, 100, 255, 150),
                symbol='s',
                name='New dataset' if not new_added_to_legend else None
            )
            scatter.setData([pos[2]], [pos[1]], data=[bead_name])
            scatter.sigClicked.connect(self._on_new_point_clicked)
            self.plot_widget.addItem(scatter)
            self.new_scatter_items[bead_name] = scatter
            new_added_to_legend = True
            
            # Add text label
            text = pg.TextItem(text=bead_name, color=(0, 0, 200), anchor=(0.5, -0.5))
            text.setPos(pos[2], pos[1])
            self.plot_widget.addItem(text)
            self.text_items.append(text)
    
    def _update_correspondence_lines(self):
        """Update lines connecting corresponding beads."""
        # Remove old lines
        for line in self.correspondence_lines.values():
            self.plot_widget.removeItem(line)
        self.correspondence_lines.clear()
        
        # Draw new lines
        for new_name, current_name in self.correspondence.items():
            if new_name in self.new_beads and current_name in self.current_beads:
                new_pos = self.new_beads[new_name]
                current_pos = self.current_beads[current_name]
                
                # Create line from new to current
                line = pg.PlotCurveItem(
                    [new_pos[2], current_pos[2]],  # x coordinates
                    [new_pos[1], current_pos[1]],  # y coordinates
                    pen=pg.mkPen(color='g', width=2, style=Qt.PenStyle.DashLine)
                )
                self.plot_widget.addItem(line)
                self.correspondence_lines[new_name] = line
    
    def _highlight_bead(self, bead_name: str, is_current: bool, highlight: bool = True):
        """Highlight or unhighlight a bead in the plot."""
        if is_current:
            if bead_name in self.current_scatter_items:
                scatter = self.current_scatter_items[bead_name]
                if highlight:
                    scatter.setSize(20)
                    scatter.setPen(pg.mkPen(color='r', width=4))
                else:
                    scatter.setSize(10)
                    scatter.setPen(pg.mkPen(color='r', width=2))
        else:
            if bead_name in self.new_scatter_items:
                scatter = self.new_scatter_items[bead_name]
                if highlight:
                    scatter.setSize(20)
                    scatter.setPen(pg.mkPen(color='b', width=4))
                else:
                    scatter.setSize(10)
                    scatter.setPen(pg.mkPen(color='b', width=2))
    
    def _on_new_point_clicked(self, plot, points):
        """Handle click on a new dataset bead in the plot."""
        # When clicking a new bead (blue), find which current bead it's matched to
        # and select that row in the table
        if len(points) > 0:
            new_bead_name = points[0].data()
            
            # Find which current bead is matched to this new bead
            for current_name, combo in self.correspondence_combos.items():
                if combo.currentData() == new_bead_name:
                    # Found the match, select this row
                    for row in range(self.correspondence_table.rowCount()):
                        item = self.correspondence_table.item(row, 0)
                        if item and item.text() == current_name:
                            self.correspondence_table.selectRow(row)
                            return
            
            # If not matched, just highlight the bead
            for bead_name in self.new_scatter_items.keys():
                self._highlight_bead(bead_name, is_current=False, highlight=(bead_name == new_bead_name))
    
    def _on_current_point_clicked(self, plot, points):
        """Handle click on a current dataset bead in the plot."""
        if len(points) > 0:
            bead_name = points[0].data()
            # Find and select this bead in the table
            for row in range(self.correspondence_table.rowCount()):
                item = self.correspondence_table.item(row, 0)
                if item and item.text() == bead_name:
                    self.correspondence_table.selectRow(row)
                    break
    
    def _on_table_selection_changed(self):
        """Handle selection change in the correspondence table."""
        # Unhighlight all beads
        for bead_name in self.current_scatter_items.keys():
            self._highlight_bead(bead_name, is_current=True, highlight=False)
        for bead_name in self.new_scatter_items.keys():
            self._highlight_bead(bead_name, is_current=False, highlight=False)
        
        # Highlight selected current bead and its matched new bead
        selected_rows = self.correspondence_table.selectedItems()
        if selected_rows:
            row = self.correspondence_table.currentRow()
            if row >= 0:
                current_bead_name = self.correspondence_table.item(row, 0).text()
                self._highlight_bead(current_bead_name, is_current=True, highlight=True)
                
                # Also highlight the matched new bead if any
                if current_bead_name in self.correspondence_combos:
                    combo = self.correspondence_combos[current_bead_name]
                    new_bead_name = combo.currentData()
                    if new_bead_name is not None:
                        self._highlight_bead(new_bead_name, is_current=False, highlight=True)
    
    def _clear_all_matches(self):
        """Clear all bead correspondences."""
        for combo in self.correspondence_combos.values():
            combo.setCurrentIndex(0)  # Set to "-- None --"
    
    def _auto_match_by_name(self):
        """Automatically match beads with the same names."""
        matched = 0
        for current_bead_name, combo in self.correspondence_combos.items():
            # Check if there's a new bead with the same name
            if current_bead_name in self.new_beads:
                # Find the index of this bead name in the combo box
                index = combo.findData(current_bead_name)
                if index >= 0:
                    combo.setCurrentIndex(index)
                    matched += 1
        
        self.status_label.setText(f"Auto-matched {matched} bead(s) by name.")
        self._update_status()
    
    def _update_correspondence(self):
        """Update the correspondence mapping when a combo box changes."""
        # Build correspondence mapping: new_name -> current_name
        # (Note: we store it inverted from the UI representation for backward compatibility)
        self.correspondence = {}
        for current_bead_name, combo in self.correspondence_combos.items():
            new_bead_name = combo.currentData()
            if new_bead_name is not None:
                # Store as new_name -> current_name (inverted from UI)
                self.correspondence[new_bead_name] = current_bead_name
        self._update_correspondence_lines()
        self._update_status()
    
    def _update_status(self):
        """Update the status message."""
        num_matched = len(self.correspondence)
        num_total = len(self.current_beads)
        
        if num_matched == 0:
            status_text = "No correspondences assigned."
            status_color = "red"
        elif num_matched < num_total:
            status_text = f"{num_matched} of {num_total} current beads matched."
            status_color = "orange"
        else:
            status_text = f"All {num_matched} current beads matched."
            status_color = "green"
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"QLabel {{ color: {status_color}; font-weight: bold; }}")
    
    def _on_accept(self):
        """Handle accept - validate that we have enough correspondences."""
        if len(self.correspondence) < 2:
            self.status_label.setText(
                "Error: At least 2 bead correspondences are required for alignment."
            )
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            return
        
        self.accept()
    
    def get_correspondence(self) -> Dict[str, str]:
        """
        Get the bead correspondence mapping.
        
        Returns:
            Dictionary mapping new bead names to current bead names
        """
        return self.correspondence
