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
        parent=None
    ):
        """
        Constructor.
        
        Args:
            reference_beads: Dict mapping bead names to their positions [z, y, x] in reference dataset
            moving_beads: Dict mapping bead names to their positions [z, y, x] in moving dataset
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Assign Bead Correspondences")
        self.setModal(True)
        self.resize(1400, 800)
        
        self.reference_beads = reference_beads
        self.moving_beads = moving_beads
        self.correspondence = {}  # Will store moving_name -> reference_name mapping
        
        # Store plot items for interactive highlighting
        self.ref_scatter_items = {}  # bead_name -> scatter plot item
        self.mov_scatter_items = {}  # bead_name -> scatter plot item
        self.correspondence_lines = {}  # moving_name -> line item
        
        self._setup_ui()
        self._populate_tables()
        self._plot_beads()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Assign correspondences between beads in the moving dataset (blue) "
            "and the reference dataset (red). Select beads in the table or click them in the plot. "
            "Lines show current correspondences."
        )
        instructions.setWordWrap(True)
        instructions.setToolTip(
            "Click on beads in the plot or select them in the tables to assign matches. "
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
        
        # Right side: Tables
        tables_widget = QWidget()
        tables_layout = QVBoxLayout()
        tables_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create vertical splitter for tables
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Moving beads table
        moving_widget = QWidget()
        moving_layout = QVBoxLayout()
        moving_layout.setContentsMargins(0, 0, 0, 0)
        moving_layout.addWidget(QLabel("<b>Moving Dataset Beads (Blue)</b>"))
        
        self.moving_table = QTableWidget()
        self.moving_table.setColumnCount(5)
        self.moving_table.setHorizontalHeaderLabels(
            ["Bead Name", "Z (nm)", "Y (nm)", "X (nm)", "→ Matches"]
        )
        self.moving_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.moving_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.moving_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.moving_table.setToolTip("Select a moving bead (blue squares in plot) to assign it to a reference bead")
        self.moving_table.itemSelectionChanged.connect(self._on_moving_selection_changed)
        moving_layout.addWidget(self.moving_table)
        moving_widget.setLayout(moving_layout)
        v_splitter.addWidget(moving_widget)
        
        # Reference beads table
        reference_widget = QWidget()
        reference_layout = QVBoxLayout()
        reference_layout.setContentsMargins(0, 0, 0, 0)
        reference_layout.addWidget(QLabel("<b>Reference Dataset Beads (Red)</b>"))
        
        self.reference_table = QTableWidget()
        self.reference_table.setColumnCount(4)
        self.reference_table.setHorizontalHeaderLabels(
            ["Bead Name", "Z (nm)", "Y (nm)", "X (nm)"]
        )
        self.reference_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.reference_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.reference_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.reference_table.setToolTip("Select a reference bead (red circles in plot) to match with a moving bead")
        self.reference_table.itemSelectionChanged.connect(self._on_reference_selection_changed)
        reference_layout.addWidget(self.reference_table)
        reference_widget.setLayout(reference_layout)
        v_splitter.addWidget(reference_widget)
        
        tables_layout.addWidget(v_splitter)
        tables_widget.setLayout(tables_layout)
        h_splitter.addWidget(tables_widget)
        
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
        
        assign_btn = QPushButton("Assign Selected Match")
        assign_btn.clicked.connect(self._assign_selected_match)
        assign_btn.setToolTip("Assign the currently selected moving bead to the selected reference bead")
        buttons_layout.addWidget(assign_btn)
        
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
        """Populate the bead tables."""
        # Populate moving table
        self.moving_table.setRowCount(len(self.moving_beads))
        self.correspondence_combos = {}
        
        for row, (bead_name, pos) in enumerate(sorted(self.moving_beads.items())):
            # Bead name
            name_item = QTableWidgetItem(bead_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.moving_table.setItem(row, 0, name_item)
            
            # Position
            for col, val in enumerate(pos):
                pos_item = QTableWidgetItem(f"{val:.2f}")
                pos_item.setFlags(pos_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.moving_table.setItem(row, col + 1, pos_item)
            
            # Correspondence combo box
            combo = QComboBox()
            combo.addItem("-- None --", None)
            for ref_name in sorted(self.reference_beads.keys()):
                combo.addItem(ref_name, ref_name)
            combo.currentIndexChanged.connect(self._update_correspondence)
            self.moving_table.setCellWidget(row, 4, combo)
            self.correspondence_combos[bead_name] = combo
        
        # Populate reference table
        self.reference_table.setRowCount(len(self.reference_beads))
        
        for row, (bead_name, pos) in enumerate(sorted(self.reference_beads.items())):
            # Bead name
            name_item = QTableWidgetItem(bead_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.reference_table.setItem(row, 0, name_item)
            
            # Position
            for col, val in enumerate(pos):
                pos_item = QTableWidgetItem(f"{val:.2f}")
                pos_item.setFlags(pos_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.reference_table.setItem(row, col + 1, pos_item)
        
        self._update_status()
    
    def _plot_beads(self):
        """Plot bead positions in XY space."""
        # Store text items for labels
        self.text_items = []
        
        # Plot reference beads (red)
        for bead_name, pos in self.reference_beads.items():
            # pos is [z, y, x]
            scatter = pg.ScatterPlotItem(
                [pos[2]],  # x
                [pos[1]],  # y
                size=15,
                pen=pg.mkPen(color='r', width=2),
                brush=pg.mkBrush(255, 100, 100, 150),
                symbol='o',
                name=f'Ref: {bead_name}'
            )
            scatter.setData([pos[2]], [pos[1]], data=[bead_name])
            scatter.sigClicked.connect(self._on_reference_point_clicked)
            self.plot_widget.addItem(scatter)
            self.ref_scatter_items[bead_name] = scatter
            
            # Add text label
            text = pg.TextItem(text=bead_name, color=(200, 0, 0), anchor=(0.5, 1.5))
            text.setPos(pos[2], pos[1])
            self.plot_widget.addItem(text)
            self.text_items.append(text)
        
        # Plot moving beads (blue)
        for bead_name, pos in self.moving_beads.items():
            # pos is [z, y, x]
            scatter = pg.ScatterPlotItem(
                [pos[2]],  # x
                [pos[1]],  # y
                size=15,
                pen=pg.mkPen(color='b', width=2),
                brush=pg.mkBrush(100, 100, 255, 150),
                symbol='s',
                name=f'Mov: {bead_name}'
            )
            scatter.setData([pos[2]], [pos[1]], data=[bead_name])
            scatter.sigClicked.connect(self._on_moving_point_clicked)
            self.plot_widget.addItem(scatter)
            self.mov_scatter_items[bead_name] = scatter
            
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
        for mov_name, ref_name in self.correspondence.items():
            if mov_name in self.moving_beads and ref_name in self.reference_beads:
                mov_pos = self.moving_beads[mov_name]
                ref_pos = self.reference_beads[ref_name]
                
                # Create line from moving to reference
                line = pg.PlotCurveItem(
                    [mov_pos[2], ref_pos[2]],  # x coordinates
                    [mov_pos[1], ref_pos[1]],  # y coordinates
                    pen=pg.mkPen(color='g', width=2, style=Qt.PenStyle.DashLine)
                )
                self.plot_widget.addItem(line)
                self.correspondence_lines[mov_name] = line
    
    def _highlight_bead(self, bead_name: str, is_reference: bool, highlight: bool = True):
        """Highlight or unhighlight a bead in the plot."""
        if is_reference:
            if bead_name in self.ref_scatter_items:
                scatter = self.ref_scatter_items[bead_name]
                if highlight:
                    scatter.setSize(25)
                    scatter.setPen(pg.mkPen(color='r', width=4))
                else:
                    scatter.setSize(15)
                    scatter.setPen(pg.mkPen(color='r', width=2))
        else:
            if bead_name in self.mov_scatter_items:
                scatter = self.mov_scatter_items[bead_name]
                if highlight:
                    scatter.setSize(25)
                    scatter.setPen(pg.mkPen(color='b', width=4))
                else:
                    scatter.setSize(15)
                    scatter.setPen(pg.mkPen(color='b', width=2))
    
    def _on_moving_point_clicked(self, plot, points):
        """Handle click on a moving bead in the plot."""
        if len(points) > 0:
            bead_name = points[0].data()
            # Find and select this bead in the table
            for row in range(self.moving_table.rowCount()):
                item = self.moving_table.item(row, 0)
                if item and item.text() == bead_name:
                    self.moving_table.selectRow(row)
                    break
    
    def _on_reference_point_clicked(self, plot, points):
        """Handle click on a reference bead in the plot."""
        if len(points) > 0:
            bead_name = points[0].data()
            # Find and select this bead in the table
            for row in range(self.reference_table.rowCount()):
                item = self.reference_table.item(row, 0)
                if item and item.text() == bead_name:
                    self.reference_table.selectRow(row)
                    break
    
    def _on_moving_selection_changed(self):
        """Handle selection change in moving beads table."""
        # Unhighlight all moving beads
        for bead_name in self.mov_scatter_items.keys():
            self._highlight_bead(bead_name, is_reference=False, highlight=False)
        
        # Highlight selected bead
        selected_rows = self.moving_table.selectedItems()
        if selected_rows:
            row = self.moving_table.currentRow()
            if row >= 0:
                bead_name = self.moving_table.item(row, 0).text()
                self._highlight_bead(bead_name, is_reference=False, highlight=True)
    
    def _on_reference_selection_changed(self):
        """Handle selection change in reference beads table."""
        # Unhighlight all reference beads
        for bead_name in self.ref_scatter_items.keys():
            self._highlight_bead(bead_name, is_reference=True, highlight=False)
        
        # Highlight selected bead
        selected_rows = self.reference_table.selectedItems()
        if selected_rows:
            row = self.reference_table.currentRow()
            if row >= 0:
                bead_name = self.reference_table.item(row, 0).text()
                self._highlight_bead(bead_name, is_reference=True, highlight=True)
    
    def _assign_selected_match(self):
        """Assign the selected moving bead to the selected reference bead."""
        mov_row = self.moving_table.currentRow()
        ref_row = self.reference_table.currentRow()
        
        if mov_row < 0:
            self.status_label.setText("Please select a moving bead first.")
            self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
            return
        
        if ref_row < 0:
            self.status_label.setText("Please select a reference bead to match.")
            self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
            return
        
        mov_name = self.moving_table.item(mov_row, 0).text()
        ref_name = self.reference_table.item(ref_row, 0).text()
        
        # Update the combo box
        if mov_name in self.correspondence_combos:
            combo = self.correspondence_combos[mov_name]
            index = combo.findData(ref_name)
            if index >= 0:
                combo.setCurrentIndex(index)
    
    def _clear_all_matches(self):
        """Clear all bead correspondences."""
        for combo in self.correspondence_combos.values():
            combo.setCurrentIndex(0)  # Set to "-- None --"
    
    def _auto_match_by_name(self):
        """Automatically match beads with the same names."""
        matched = 0
        for bead_name, combo in self.correspondence_combos.items():
            if bead_name in self.reference_beads:
                # Find the index of this bead name in the combo box
                index = combo.findData(bead_name)
                if index >= 0:
                    combo.setCurrentIndex(index)
                    matched += 1
        
        self.status_label.setText(f"Auto-matched {matched} bead(s) by name.")
        self._update_status()
    
    def _update_correspondence(self):
        """Update the correspondence mapping when a combo box changes."""
        self.correspondence = {}
        for bead_name, combo in self.correspondence_combos.items():
            ref_name = combo.currentData()
            if ref_name is not None:
                self.correspondence[bead_name] = ref_name
        self._update_correspondence_lines()
        self._update_status()
    
    def _update_status(self):
        """Update the status message."""
        num_matched = len(self.correspondence)
        num_total = len(self.moving_beads)
        
        if num_matched == 0:
            status_text = "No correspondences assigned."
            status_color = "red"
        elif num_matched < num_total:
            status_text = f"{num_matched} of {num_total} beads matched."
            status_color = "orange"
        else:
            status_text = f"All {num_matched} beads matched."
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
            Dictionary mapping moving bead names to reference bead names
        """
        return self.correspondence
