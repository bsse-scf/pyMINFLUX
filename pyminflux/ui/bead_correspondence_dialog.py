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
    QCheckBox,
)

# Import the Kabsch alignment function
from pyminflux.correct._bead_alignment import _kabsch, RigidTransform, TranslationTransform
from pyminflux.ui.colors import Colors
from pyminflux.ui.fluorophore_naming_widget import FluorophoreNamingWidget


class BeadCorrespondenceDialog(QDialog):
    """
    Dialog for manually assigning bead correspondences between two datasets.
    """
    
    def __init__(
        self, 
        reference_beads: Dict[str, np.ndarray],
        moving_beads: Dict[str, np.ndarray],
        auto_match: bool = False,
        existing_fluo_ids: list = None,
        next_fluo_id: int = 2,
        existing_names: dict = None,
        parent=None
    ):
        """
        Constructor.
        
        Args:
            reference_beads: Dict mapping bead names to their positions [z, y, x] in current (reference) dataset
            moving_beads: Dict mapping bead names to their positions [z, y, x] in new (moving) dataset
            auto_match: If True, automatically match beads by name on initialization
            existing_fluo_ids: List of existing fluorophore IDs in current dataset
            next_fluo_id: The fluorophore ID that will be assigned to the new dataset
            existing_names: Dictionary of existing fluorophore names (fluo_id -> name)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Bead-Based Dataset Alignment")
        self.setModal(True)
        self.resize(1400, 800)
        
        self.current_beads = reference_beads  # Current dataset (reference for alignment)
        self.new_beads = moving_beads  # New dataset (will be transformed)
        self.correspondence = {}  # Will store new_name -> current_name mapping
        
        # Fluorophore naming
        self.existing_fluo_ids = existing_fluo_ids or [1]
        self.next_fluo_id = next_fluo_id
        self.existing_names = existing_names or {}
        
        # Store plot items for interactive highlighting
        self.current_scatter_items = {}  # bead_name -> scatter plot item
        self.new_scatter_items = {}  # bead_name -> scatter plot item
        self.correspondence_lines = {}  # new_name -> line item
        
        # Store alignment results
        self.current_transform = None  # RigidTransform object
        self.residuals = {}  # new_name -> residual (in nm)
        
        # Axis selection for plotting
        self.x_axis_idx = 2  # Default to X (index 2 in [z, y, x])
        self.y_axis_idx = 1  # Default to Y (index 1 in [z, y, x])
        self.show_transformed = False  # Whether to show transformed beads
        
        self._setup_ui()
        self._populate_tables()
        self._plot_beads()
        
        # Auto-match by name if requested
        if auto_match:
            self._auto_match_by_name()
            # Automatically calculate alignment if we have correspondences
            if len(self.correspondence) >= 1:
                self._calculate_alignment()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "<b>Dataset Alignment Using Fiducial Beads</b><br>"
            "The bead positions shown below were extracted from beam monitoring (MBM) data. "
            "Match corresponding beads between the current (red circles) and new (blue squares) datasets. "
            "When you click OK, all localizations in the new dataset will be transformed using the "
            "rigid transformation computed from the matched bead positions. The added localizations "
            "will be assigned a new \"fluo\" value.<br>"
            "<b>Note:</b> Reference beads are always from the <u>first dataset originally loaded</u>"
            "<b>Tip:</b> Hold <b>Shift</b> and click a new bead (blue) to assign it to the currently selected current bead (red)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #333; padding: 8px; background-color: #f8f8f8; border-radius: 4px; }")
        main_layout.addWidget(instructions)
        
        # Warning label (initially hidden)
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet(
            "QLabel { color: #856404; padding: 8px; background-color: #fff3cd; "
            "border: 1px solid #ffc107; border-radius: 4px; }"
        )
        self.warning_label.setVisible(False)
        main_layout.addWidget(self.warning_label)
        
        # Create main horizontal splitter
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Plot view
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0, 0, 0, 0)
        
        plot_label = QLabel("<b>Bead Positions</b>")
        plot_layout.addWidget(plot_label)
        
        # Axis selection controls and transformation checkbox
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("X-axis:"))
        self.x_axis_combo = QComboBox()
        self.x_axis_combo.addItem("X", 2)
        self.x_axis_combo.addItem("Y", 1)
        self.x_axis_combo.addItem("Z", 0)
        self.x_axis_combo.setCurrentIndex(0)  # Default to X
        self.x_axis_combo.currentIndexChanged.connect(self._on_axis_changed)
        axis_layout.addWidget(self.x_axis_combo)
        
        axis_layout.addSpacing(20)
        
        axis_layout.addWidget(QLabel("Y-axis:"))
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItem("X", 2)
        self.y_axis_combo.addItem("Y", 1)
        self.y_axis_combo.addItem("Z", 0)
        self.y_axis_combo.setCurrentIndex(1)  # Default to Y
        self.y_axis_combo.currentIndexChanged.connect(self._on_axis_changed)
        axis_layout.addWidget(self.y_axis_combo)
        
        axis_layout.addSpacing(20)
        
        # Transformation visualization checkbox (on same line)
        self.show_transformed_checkbox = QCheckBox("Show transformed beads")
        self.show_transformed_checkbox.setToolTip(
            "When checked, displays the new dataset beads after applying the calculated transformation. "
            "This allows you to visualize how well the alignment works. "
            "Requires running 'Calculate Alignment' first."
        )
        self.show_transformed_checkbox.setEnabled(False)  # Disabled until alignment is calculated
        self.show_transformed_checkbox.stateChanged.connect(self._on_show_transformed_changed)
        axis_layout.addWidget(self.show_transformed_checkbox)
        
        axis_layout.addStretch()
        plot_layout.addLayout(axis_layout)
        
        # Create pyqtgraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setLabel('left', 'Y (nm)')
        self.plot_widget.setLabel('bottom', 'X (nm)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()
        
        plot_layout.addWidget(self.plot_widget)
        plot_widget.setLayout(plot_layout)
        h_splitter.addWidget(plot_widget)
        
        # Right side: Single table
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table title
        table_layout.addWidget(QLabel("<b>Bead Correspondence Assignments</b>"))
        
        # Matching controls (first row)
        matching_layout = QHBoxLayout()
        auto_match_btn = QPushButton("Auto-match by name")
        auto_match_btn.setToolTip("Automatically match beads that have identical names in both datasets")
        auto_match_btn.clicked.connect(self._auto_match_by_name)
        matching_layout.addWidget(auto_match_btn)
        
        self.nearest_neighbor_btn = QPushButton("Assign nearest neighbors")
        self.nearest_neighbor_btn.setToolTip(
            "For each current bead without a match, assign the nearest new bead "
            "using the currently calculated transformation. "
            "Requires running 'Calculate Alignment' first."
        )
        self.nearest_neighbor_btn.setEnabled(False)  # Disabled until alignment is calculated
        self.nearest_neighbor_btn.clicked.connect(self._assign_nearest_neighbors)
        matching_layout.addWidget(self.nearest_neighbor_btn)
        
        clear_btn = QPushButton("Clear all matches")
        clear_btn.setToolTip("Remove all current bead correspondences")
        clear_btn.clicked.connect(self._clear_all_matches)
        matching_layout.addWidget(clear_btn)
        matching_layout.addStretch()
        
        table_layout.addLayout(matching_layout)
        
        # Alignment controls (second row)
        alignment_layout = QHBoxLayout()
        alignment_layout.addWidget(QLabel("<b>Alignment Quality Control:</b>"))
        
        self.calc_alignment_btn = QPushButton("Calculate Alignment")
        self.calc_alignment_btn.setToolTip(
            "Calculate the rigid transformation using currently selected bead correspondences "
            "and display residual errors for each bead pair"
        )
        self.calc_alignment_btn.clicked.connect(self._calculate_alignment)
        alignment_layout.addWidget(self.calc_alignment_btn)
        
        # Mean residual label
        self.mean_residual_label = QLabel("Mean residual: N/A")
        self.mean_residual_label.setStyleSheet(
            "QLabel { color: #666; font-weight: bold; padding: 5px; }"
        )
        self.mean_residual_label.setToolTip("Mean residual error across all matched bead pairs")
        alignment_layout.addWidget(self.mean_residual_label)
        alignment_layout.addStretch()
        
        table_layout.addLayout(alignment_layout)
        
        # Add spacing
        table_layout.addSpacing(10)
        
        # Single correspondence table (with scroll support)
        self.correspondence_table = QTableWidget()
        self.correspondence_table.setColumnCount(3)
        self.correspondence_table.setHorizontalHeaderLabels(
            ["Current Dataset", "New Dataset", "Residual (nm)"]
        )
        header = self.correspondence_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.correspondence_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.correspondence_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.correspondence_table.setToolTip(
            "Select matching beads from the dropdown. Click 'Calculate Alignment' to preview alignment quality."
        )
        # Enable vertical scrolling
        self.correspondence_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.correspondence_table.setMinimumHeight(200)  # Ensure minimum visible area
        self.correspondence_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        table_layout.addWidget(self.correspondence_table)
        
        table_widget.setLayout(table_layout)
        h_splitter.addWidget(table_widget)
        
        # Set splitter proportions (plot gets more space)
        h_splitter.setSizes([700, 500])
        
        main_layout.addWidget(h_splitter)
        
        # Add fluorophore naming widget (with no stretch so it stays compact)
        self.fluorophore_naming_widget = FluorophoreNamingWidget(
            title="Channel Names for Combined Dataset"
        )
        # Set up all fluorophore IDs (existing + new)
        all_fluo_ids = self.existing_fluo_ids + [self.next_fluo_id]
        self.fluorophore_naming_widget.set_fluorophores(all_fluo_ids, self.existing_names)
        main_layout.addWidget(self.fluorophore_naming_widget, stretch=0)
        
        # Status label at the bottom
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("QLabel { color: #666; padding: 5px; }")
        main_layout.addWidget(self.status_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        
        # Add helpful tooltip to OK button
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setToolTip(
                "Apply the alignment and combine datasets. All localizations in the new dataset "
                "will be transformed to match the current dataset's coordinate system."
            )
        
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
            
            # Residual column (third column) - initially empty
            residual_item = QTableWidgetItem("")
            residual_item.setFlags(residual_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            residual_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.correspondence_table.setItem(row, 2, residual_item)
        
        self._update_status()
    
    def _plot_beads(self):
        """Plot bead positions using selected axes."""
        # Clear existing plot items
        self.plot_widget.clear()
        
        # Re-add legend
        self.plot_widget.addLegend()
        
        # Update axis labels based on selection
        axis_names = {0: 'Z', 1: 'Y', 2: 'X'}
        self.plot_widget.setLabel('bottom', f'{axis_names[self.x_axis_idx]} (nm)')
        self.plot_widget.setLabel('left', f'{axis_names[self.y_axis_idx]} (nm)')
        
        # Store text items for labels
        self.text_items = []
        
        # Clear previous scatter items
        self.current_scatter_items = {}
        self.new_scatter_items = {}
        
        # Flag to track if legend items have been added
        current_added_to_legend = False
        new_added_to_legend = False
        
        # Get colors for existing and new fluorophore IDs
        # For current dataset, use the lowest fluorophore ID (first dataset loaded has lowest IDs)
        if self.existing_fluo_ids:
            current_color = Colors()._get_fid_color(min(self.existing_fluo_ids), as_float=False).tolist()
        else:
            current_color = [255, 0, 0]  # Default to red
        
        # For new dataset, use the next fluorophore ID color
        new_color = Colors()._get_fid_color(self.next_fluo_id, as_float=False).tolist()
        
        # Plot current dataset beads (using existing fluo ID color)
        for bead_name, pos in self.current_beads.items():
            # pos is [z, y, x]
            x_val = pos[self.x_axis_idx]
            y_val = pos[self.y_axis_idx]
            
            scatter = pg.ScatterPlotItem(
                [x_val],
                [y_val],
                size=10,
                pen=pg.mkPen(color=current_color, width=2),
                brush=pg.mkBrush(*current_color, 150),
                symbol='o',
                name='Current dataset' if not current_added_to_legend else None
            )
            scatter.setData([x_val], [y_val], data=[bead_name])
            scatter.sigClicked.connect(self._on_current_point_clicked)
            self.plot_widget.addItem(scatter)
            self.current_scatter_items[bead_name] = scatter
            current_added_to_legend = True
            
            # Add text label
            text = pg.TextItem(text=bead_name, color=tuple(current_color), anchor=(0.5, 1.5))
            text.setPos(x_val, y_val)
            self.plot_widget.addItem(text)
            self.text_items.append(text)
        
        # Plot new dataset beads (using next fluo ID color)
        for bead_name, pos in self.new_beads.items():
            # pos is [z, y, x]
            # If transformation is available and checkbox is checked, transform the position
            if self.show_transformed and self.current_transform is not None:
                pos_transformed = self.current_transform(pos.reshape(1, -1))[0]
                x_val = pos_transformed[self.x_axis_idx]
                y_val = pos_transformed[self.y_axis_idx]
            else:
                x_val = pos[self.x_axis_idx]
                y_val = pos[self.y_axis_idx]
            
            scatter = pg.ScatterPlotItem(
                [x_val],
                [y_val],
                size=10,
                pen=pg.mkPen(color=new_color, width=2),
                brush=pg.mkBrush(*new_color, 150),
                symbol='s',
                name='New dataset' if not new_added_to_legend else None
            )
            scatter.setData([x_val], [y_val], data=[bead_name])
            scatter.sigClicked.connect(self._on_new_point_clicked)
            self.plot_widget.addItem(scatter)
            self.new_scatter_items[bead_name] = scatter
            new_added_to_legend = True
            
            # Add text label
            text = pg.TextItem(text=bead_name, color=tuple(new_color), anchor=(0.5, -0.5))
            text.setPos(x_val, y_val)
            self.plot_widget.addItem(text)
            self.text_items.append(text)
        
        # Re-draw correspondence lines if any
        self._update_correspondence_lines()
    
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
                
                # If transformation is available and checkbox is checked, transform the new position
                if self.show_transformed and self.current_transform is not None:
                    new_pos_transformed = self.current_transform(new_pos.reshape(1, -1))[0]
                    new_x = new_pos_transformed[self.x_axis_idx]
                    new_y = new_pos_transformed[self.y_axis_idx]
                else:
                    new_x = new_pos[self.x_axis_idx]
                    new_y = new_pos[self.y_axis_idx]
                
                current_x = current_pos[self.x_axis_idx]
                current_y = current_pos[self.y_axis_idx]
                
                # Create line from new to current
                line = pg.PlotCurveItem(
                    [new_x, current_x],
                    [new_y, current_y],
                    pen=pg.mkPen(color='g', width=2, style=Qt.PenStyle.DashLine)
                )
                self.plot_widget.addItem(line)
                self.correspondence_lines[new_name] = line
    
    def _highlight_bead(self, bead_name: str, is_current: bool, highlight: bool = True):
        """Highlight or unhighlight a bead in the plot."""
        # Get colors for existing and new fluorophore IDs
        if self.existing_fluo_ids:
            current_color = Colors()._get_fid_color(min(self.existing_fluo_ids), as_float=False).tolist()
        else:
            current_color = [255, 0, 0]  # Default to red
        
        new_color = Colors()._get_fid_color(self.next_fluo_id, as_float=False).tolist()
        
        if is_current:
            if bead_name in self.current_scatter_items:
                scatter = self.current_scatter_items[bead_name]
                if highlight:
                    scatter.setSize(20)
                    scatter.setPen(pg.mkPen(color=current_color, width=4))
                else:
                    scatter.setSize(10)
                    scatter.setPen(pg.mkPen(color=current_color, width=2))
        else:
            if bead_name in self.new_scatter_items:
                scatter = self.new_scatter_items[bead_name]
                if highlight:
                    scatter.setSize(20)
                    scatter.setPen(pg.mkPen(color=new_color, width=4))
                else:
                    scatter.setSize(10)
                    scatter.setPen(pg.mkPen(color=new_color, width=2))
    
    def _on_new_point_clicked(self, plot, points):
        """Handle click on a new dataset bead in the plot."""
        if len(points) > 0:
            new_bead_name = points[0].data()
            
            # Check if Shift key is pressed using QApplication
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt as QtCore_Qt
            modifiers = QApplication.keyboardModifiers()
            shift_pressed = modifiers & QtCore_Qt.KeyboardModifier.ShiftModifier
            
            # If Shift is pressed and a current bead is selected, assign correspondence
            if shift_pressed:
                selected_row = self.correspondence_table.currentRow()
                if selected_row >= 0:
                    current_bead_name = self.correspondence_table.item(selected_row, 0).text()
                    combo = self.correspondence_combos[current_bead_name]
                    
                    # Check if this new bead is already assigned to another current bead
                    old_current_bead = None
                    for other_current_name, other_combo in self.correspondence_combos.items():
                        if other_current_name != current_bead_name and other_combo.currentData() == new_bead_name:
                            old_current_bead = other_current_name
                            # Unset the old correspondence
                            other_combo.setCurrentIndex(0)  # Set to "-- None --"
                            break
                    
                    # Find and set the new bead in the combo box
                    index = combo.findData(new_bead_name)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                        
                        # Show visual feedback
                        if old_current_bead:
                            self.status_label.setText(
                                f"✓ Moved '{new_bead_name}' from '{old_current_bead}' to '{current_bead_name}'"
                            )
                        else:
                            self.status_label.setText(
                                f"✓ Assigned '{new_bead_name}' to '{current_bead_name}'"
                            )
                        self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
                        
                        # Keep the row selected so user can continue assigning
                        return
                    else:
                        self.status_label.setText(
                            f"Error: '{new_bead_name}' not found in dropdown"
                        )
                        self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
                        return
                else:
                    # No current bead selected, show hint
                    self.status_label.setText(
                        "To assign: First select a current bead (red), then Shift+click a new bead (blue)"
                    )
                    self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
                    # Continue with normal behavior below
            
            # Normal behavior: find which current bead is matched to this new bead
            # and select that row in the table
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
    
    def _on_axis_changed(self):
        """Handle axis selection change."""
        # Get new axis indices
        new_x_axis = self.x_axis_combo.currentData()
        new_y_axis = self.y_axis_combo.currentData()
        
        # Check if the same axis is selected for both
        if new_x_axis == new_y_axis:
            # Revert to previous selection
            self.x_axis_combo.blockSignals(True)
            self.y_axis_combo.blockSignals(True)
            
            # Find the index for the previous values
            for i in range(self.x_axis_combo.count()):
                if self.x_axis_combo.itemData(i) == self.x_axis_idx:
                    self.x_axis_combo.setCurrentIndex(i)
                if self.y_axis_combo.itemData(i) == self.y_axis_idx:
                    self.y_axis_combo.setCurrentIndex(i)
            
            self.x_axis_combo.blockSignals(False)
            self.y_axis_combo.blockSignals(False)
            
            # Show error message in status
            self.status_label.setText("Error: X and Y axes must be different.")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            return
        
        # Update axis indices
        self.x_axis_idx = new_x_axis
        self.y_axis_idx = new_y_axis
        
        # Redraw the plot
        self._plot_beads()
        
        # Restore status message
        self._update_status()
    
    def _on_show_transformed_changed(self, state):
        """Handle show transformed checkbox state change."""
        self.show_transformed = (state == Qt.CheckState.Checked.value)
        # Redraw the plot with or without transformation
        self._plot_beads()
    
    def _clear_all_matches(self):
        """Clear all bead correspondences."""
        for combo in self.correspondence_combos.values():
            combo.setCurrentIndex(0)  # Set to "-- None --"
        
        # Clear residuals
        self.residuals = {}
        self.current_transform = None
        self.show_transformed_checkbox.setEnabled(False)
        self.show_transformed_checkbox.setChecked(False)
        self.nearest_neighbor_btn.setEnabled(False)
        self._update_residual_display()
    
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
    
    def _assign_nearest_neighbors(self):
        """Assign nearest neighbors based on current transformation."""
        if self.current_transform is None:
            self.status_label.setText("Error: No transformation calculated. Run 'Calculate Alignment' first.")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            return
        
        # Get already matched new beads
        already_matched_new_beads = set(self.correspondence.keys())
        
        # Transform all new bead positions
        new_bead_names = list(self.new_beads.keys())
        new_bead_positions = np.array([self.new_beads[name] for name in new_bead_names])
        transformed_new_positions = self.current_transform(new_bead_positions)
        
        # Find unmatched current beads
        matched = 0
        for current_bead_name, combo in self.correspondence_combos.items():
            # Skip if already matched
            if combo.currentData() is not None:
                continue
            
            current_pos = self.current_beads[current_bead_name]
            
            # Find nearest new bead (that isn't already matched)
            min_dist = float('inf')
            nearest_new_bead = None
            
            for i, new_bead_name in enumerate(new_bead_names):
                # Skip if this new bead is already matched
                if new_bead_name in already_matched_new_beads:
                    continue
                
                # Calculate distance to transformed new bead position
                dist = np.linalg.norm(transformed_new_positions[i] - current_pos)
                
                if dist < min_dist:
                    min_dist = dist
                    nearest_new_bead = new_bead_name
            
            # Assign the nearest neighbor
            if nearest_new_bead is not None:
                index = combo.findData(nearest_new_bead)
                if index >= 0:
                    combo.setCurrentIndex(index)
                    already_matched_new_beads.add(nearest_new_bead)
                    matched += 1
        
        self.status_label.setText(f"Assigned {matched} nearest neighbor(s).")
        self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
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
        
        # Clear residuals when correspondence changes
        self.residuals = {}
        self.current_transform = None
        self.show_transformed_checkbox.setEnabled(False)
        self.show_transformed_checkbox.setChecked(False)
        self.nearest_neighbor_btn.setEnabled(False)
        self._update_residual_display()
    
    def _calculate_alignment(self):
        """Calculate alignment using current correspondences and display residuals."""
        num_correspondences = len(self.correspondence)
        
        if num_correspondences < 1:
            self.status_label.setText(
                "Error: At least 1 bead correspondence required for alignment calculation."
            )
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            return
        
        # Build point arrays from correspondences
        pts_ref = []  # Reference (current) bead positions
        pts_mov = []  # Moving (new) bead positions
        bead_pairs = []  # Track which beads for later residual assignment
        
        for new_bead_name, current_bead_name in self.correspondence.items():
            if new_bead_name in self.new_beads and current_bead_name in self.current_beads:
                pts_ref.append(self.current_beads[current_bead_name])
                pts_mov.append(self.new_beads[new_bead_name])
                bead_pairs.append((new_bead_name, current_bead_name))
        
        if len(pts_ref) < 1:
            self.status_label.setText("Error: Not enough valid bead pairs for alignment.")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            return
        
        pts_ref = np.array(pts_ref)
        pts_mov = np.array(pts_mov)
        
        try:
            # Check if we have enough correspondences for full rigid transformation
            if len(pts_ref) < 3:
                # Use translation-only transformation for 1-2 correspondences
                t = pts_ref.mean(axis=0) - pts_mov.mean(axis=0)
                self.current_transform = TranslationTransform(t)
                
                # Show warning in the instructions area
                warning_msg = (
                    f"⚠️ <b>Warning: Using translation-only alignment</b><br>"
                    f"Only {len(pts_ref)} bead correspondence(s) available. "
                    f"At least 3 correspondences are required for full rigid alignment (rotation + translation). "
                    f"Currently using translation-only mode, which may result in less accurate alignment.<br>"
                    f"<b>Consider adding more bead correspondences for better results.</b>"
                )
            else:
                # Calculate full Kabsch alignment (rotation + translation)
                R, t = _kabsch(pts_mov, pts_ref, allow_reflection=False)
                self.current_transform = RigidTransform(R, t)
                
                # Clear any previous warning
                warning_msg = None
            
            # Calculate residuals for each bead pair
            self.residuals = {}
            for (new_name, current_name), pt_mov, pt_ref in zip(bead_pairs, pts_mov, pts_ref):
                # Transform the moving point
                pt_transformed = self.current_transform(pt_mov.reshape(1, -1))[0]
                # Calculate residual (Euclidean distance in nm)
                residual = np.linalg.norm(pt_transformed - pt_ref)
                self.residuals[new_name] = residual
            
            # Print transformation to console
            self._print_transformation_info()
            
            # Update display
            self._update_residual_display()
            
            # Enable the "show transformed" checkbox and nearest neighbor button
            self.show_transformed_checkbox.setEnabled(True)
            self.nearest_neighbor_btn.setEnabled(True)
            
            # Update status with success message
            mean_residual = np.mean(list(self.residuals.values()))
            if len(pts_ref) < 3:
                self.status_label.setText(
                    f"⚠️ Translation-only alignment calculated with {len(self.residuals)} bead pair(s). "
                    f"Add more correspondences for full rigid alignment."
                )
                self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
            else:
                self.status_label.setText(
                    f"Alignment calculated successfully with {len(self.residuals)} bead pairs."
                )
                self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            
            # Show/hide warning in instructions area
            if warning_msg:
                self._show_alignment_warning(warning_msg)
            else:
                self._hide_alignment_warning()
            
        except Exception as e:
            self.status_label.setText(f"Error calculating alignment: {e}")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            self.residuals = {}
            self.current_transform = None
            self.show_transformed_checkbox.setEnabled(False)
            self.show_transformed_checkbox.setChecked(False)
            self.nearest_neighbor_btn.setEnabled(False)
            self._update_residual_display()
            self._hide_alignment_warning()
    
    def _update_residual_display(self):
        """Update the residual column in the table and mean residual label."""
        # Update table residual column
        for row in range(self.correspondence_table.rowCount()):
            current_bead_name = self.correspondence_table.item(row, 0).text()
            combo = self.correspondence_combos[current_bead_name]
            new_bead_name = combo.currentData()
            
            residual_item = self.correspondence_table.item(row, 2)
            
            if new_bead_name and new_bead_name in self.residuals:
                residual = self.residuals[new_bead_name]
                residual_item.setText(f"{residual:.2f}")
                
                # Color code based on residual magnitude (darker colors for better readability)
                if residual < 10:  # < 10 nm - good
                    residual_item.setForeground(pg.mkColor(0, 128, 0))  # Dark green
                elif residual < 50:  # 10-50 nm - okay
                    residual_item.setForeground(pg.mkColor(204, 102, 0))  # Dark orange
                else:  # > 50 nm - potentially problematic
                    residual_item.setForeground(pg.mkColor(178, 34, 34))  # Dark red
            else:
                residual_item.setText("")
                residual_item.setForeground(pg.mkColor('k'))
        
        # Update mean residual label
        if self.residuals:
            mean_residual = np.mean(list(self.residuals.values()))
            self.mean_residual_label.setText(f"Mean residual: {mean_residual:.2f} nm")
            
            # Color code the mean residual (darker colors)
            if mean_residual < 10:
                color = "#008000"  # Dark green
            elif mean_residual < 50:
                color = "#CC6600"  # Dark orange
            else:
                color = "#B22222"  # Dark red (firebrick)
            
            self.mean_residual_label.setStyleSheet(
                f"QLabel {{ color: {color}; font-weight: bold; padding: 5px; }}"
            )
        else:
            self.mean_residual_label.setText("Mean residual: N/A")
            self.mean_residual_label.setStyleSheet(
                "QLabel { color: #333; font-weight: bold; padding: 5px; }"
            )
    
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
        if len(self.correspondence) < 1:
            self.status_label.setText(
                "Error: At least 1 bead correspondence is required for alignment."
            )
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            return
        
        # Show additional warning if using translation-only mode
        if len(self.correspondence) < 3:
            from PySide6.QtWidgets import QMessageBox
            result = QMessageBox.warning(
                self,
                "Translation-Only Alignment",
                f"You have selected {len(self.correspondence)} bead correspondence(s).\n\n"
                "This will use translation-only alignment, which does not account for rotation. "
                "For more accurate alignment, it is recommended to have at least 3 bead correspondences.\n\n"
                "Do you want to proceed with translation-only alignment?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                return
        
        self.accept()
    
    def _show_alignment_warning(self, message: str):
        """Show alignment warning message."""
        self.warning_label.setText(message)
        self.warning_label.setVisible(True)
    
    def _hide_alignment_warning(self):
        """Hide alignment warning message."""
        self.warning_label.setVisible(False)
    
    def get_correspondence(self) -> Dict[str, str]:
        """
        Get the bead correspondence mapping.
        
        Returns:
            Dictionary mapping new bead names to current bead names
        """
        return self.correspondence
    
    def get_fluorophore_names(self) -> dict:
        """
        Get the fluorophore names from the naming widget.
        
        Returns:
            Dictionary mapping fluo_id (int) to name (str)
        """
        return self.fluorophore_naming_widget.get_names()
    
    def _print_transformation_info(self):
        """Print transformation details to console."""
        if self.current_transform is None:
            return
        
        print("\n" + "="*60)
        print("BEAD ALIGNMENT TRANSFORMATION")
        print("="*60)
        
        if isinstance(self.current_transform, TranslationTransform):
            print("Type: Translation-only (insufficient correspondences for rotation)")
            print(f"Translation vector [z, y, x] (nm): {self.current_transform.translation}")
        elif isinstance(self.current_transform, RigidTransform):
            print("Type: Rigid (rotation + translation)")
            print("\nRotation matrix:")
            print(self.current_transform.rotation)
            print(f"\nTranslation vector [z, y, x] (nm): {self.current_transform.translation}")
        
        if self.residuals:
            residual_values = list(self.residuals.values())
            print(f"\nAlignment quality:")
            print(f"  Mean residual: {np.mean(residual_values):.2f} nm")
            print(f"  Std residual:  {np.std(residual_values):.2f} nm")
            print(f"  Min residual:  {np.min(residual_values):.2f} nm")
            print(f"  Max residual:  {np.max(residual_values):.2f} nm")
            print(f"  Bead pairs used: {len(self.residuals)}")
        
        print("="*60 + "\n")
