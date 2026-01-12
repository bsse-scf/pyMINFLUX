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

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Signal, Slot
from PySide6.QtGui import QAction, QDoubleValidator, Qt
from PySide6.QtWidgets import QDialog, QMenu

from pyminflux.analysis import (
    assign_data_to_clusters,
    prepare_histogram,
    reassign_fluo_ids_by_majority_vote,
)
from pyminflux.processor import MinFluxProcessor
from pyminflux.ui.colors import Colors
from pyminflux.ui.fluorophore_naming_widget import FluorophoreNamingWidget
from pyminflux.ui.helpers import export_plot_interactive
from pyminflux.ui.state import State
from pyminflux.ui.time_plotter import TimePlotter
from pyminflux.ui.ui_color_unmixer import Ui_ColorUnmixer


class ColorUnmixer(QDialog, Ui_ColorUnmixer):
    """
    A QDialog to display the dcr histogram and to assigning the fluorophore ids.
    """

    # Signal that the fluorophore IDs have been assigned
    fluorophore_ids_assigned = Signal(int)

    def __init__(self, processor: MinFluxProcessor):
        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_ColorUnmixer()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Set up ui elements
        self.ui.pbAssign.setEnabled(False)
        self.ui.leBinSize.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leBinSize.setText(str(self.state.dcr_bin_size))
        self.ui.pbManualAssign.setEnabled(False)
        self.ui.leManualThreshold.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leManualThreshold.setText(str(self.state.dcr_manual_threshold))
        
        # Time splitting plot caches (like TimeInspector)
        self.time_resolution_sec = 60  # 1 minute bins
        self.time_x_axis = None
        self.localizations_per_unit_time_cache = None
        self.localization_precision_per_unit_time_cache_x = None
        self.localization_precision_per_unit_time_cache_y = None
        self.localization_precision_per_unit_time_cache_z = None
        self.localization_precision_stderr_per_unit_time_cache_x = None
        self.localization_precision_stderr_per_unit_time_cache_y = None
        self.localization_precision_stderr_per_unit_time_cache_z = None

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.processor = processor

        # Keep track of the global data range and step
        self.n_dcr_max = None
        self.dcr_bin_edges = None
        self.dcr_bin_centers = None
        self.dcr_bin_width = None

        # Keep track of the fluorophore ID assignments
        self.assigned_fluorophore_ids = None

        # Create the plot elements for DCR unmixing
        self.plot_widget = PlotWidget(parent=self, background="w", title="dcr")

        # Plot the dcr histogram
        self.plot_dcr_histogram()

        # Create the plot elements for time splitting
        self.time_plot_widget = PlotWidget(parent=self, background="w", title="tid")
        
        # Time splitting state
        self.time_split_regions = []  # List of LinearRegionItem objects
        self.time_assigned_fluorophore_ids = None  # Assignments based on time ranges

        # Add them to the UI (they will be shown/hidden based on active tab)
        self.ui.main_layout.addWidget(self.plot_widget, stretch=1)
        self.ui.main_layout.addWidget(self.time_plot_widget, stretch=1)
        self.time_plot_widget.hide()  # Initially hidden
        
        # Add fluorophore naming widget
        self.fluorophore_naming_widget = FluorophoreNamingWidget(
            title="Fluorophore Names"
        )
        # Initially hidden until fluorophores are detected
        self.fluorophore_naming_widget.setVisible(False)
        self.ui.main_layout.addWidget(self.fluorophore_naming_widget, stretch=0)

        # Add connections for DCR unmixing
        self.ui.cbNumFluorophores.currentIndexChanged.connect(
            self.persist_num_fluorophores
        )
        self.ui.leBinSize.textChanged.connect(self.persist_dcr_bin_size)
        self.ui.leBinSize.editingFinished.connect(self.plot_dcr_histogram)
        self.ui.leManualThreshold.textChanged.connect(self.persist_dcr_manual_threshold)
        self.ui.pbDetect.clicked.connect(self.detect_fluorophores)
        self.ui.pbAssign.clicked.connect(self.assign_fluorophores_ids)
        self.ui.pbPreview.clicked.connect(self.preview_manual_assignment)
        self.ui.pbManualAssign.clicked.connect(self.assign_fluorophores_ids)
        
        # Add connections for time splitting
        self.ui.pbSplit.clicked.connect(self.split_by_time)
        self.ui.pbTimeSplitAssign.clicked.connect(self.assign_time_split_fluorophores)
        self.ui.pbTimeSplitAssign.setEnabled(False)
        self.ui.pbTimePlot.clicked.connect(self.plot_time_selected)
        
        # Connect tab change to update plots
        self.ui.twMainTabs.currentChanged.connect(self.main_tab_changed)

    def showEvent(self, event):
        """Override showEvent to update plots when dialog is shown."""
        super().showEvent(event)
        # Check which tab is active and update its plot
        current_tab = self.ui.twMainTabs.currentIndex()
        if current_tab == 1:  # Time splitting tab
            self.plot_time_selected()

    @Slot(str)
    def persist_dcr_bin_size(self, text):
        try:
            dcr_bin_size = float(text)
        except ValueError as _:
            return
        self.state.dcr_bin_size = dcr_bin_size

    @Slot(str)
    def persist_num_fluorophores(self, text):
        num_fluorophores = self.ui.cbNumFluorophores.currentIndex() + 1
        self.state.num_fluorophores = num_fluorophores
        self.ui.pbAssign.setEnabled(False)
        # Hide naming widget when number changes
        self.fluorophore_naming_widget.setVisible(False)

    @Slot(str)
    def persist_dcr_manual_threshold(self, text):
        try:
            dcr_manual_threshold = float(text)
        except ValueError as _:
            return
        self.state.dcr_manual_threshold = float(dcr_manual_threshold)

    @Slot(str)
    def invalidate_time_cache(self):
        """Invalidate the time plot cache."""
        self.localizations_per_unit_time_cache = None
        self.localization_precision_per_unit_time_cache_x = None
        self.localization_precision_per_unit_time_cache_y = None
        self.localization_precision_per_unit_time_cache_z = None
        self.localization_precision_stderr_per_unit_time_cache_x = None
        self.localization_precision_stderr_per_unit_time_cache_y = None
        self.localization_precision_stderr_per_unit_time_cache_z = None
        self.time_x_axis = None

    @Slot()
    def plot_dcr_histogram(self):
        """Plot the dcr histogram for the currently selected fluorophore."""

        # Do we have something to plot?
        if self.processor is None or self.processor.filtered_dataframe is None:
            return

        # Retrieve the filtered data for current fluorophore
        if self.state.dcr_bin_size == 0:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.processor.filtered_dataframe["dcr"].to_numpy(),
                auto_bins=True,
            )
        else:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.processor.filtered_dataframe["dcr"].to_numpy(),
                auto_bins=False,
                bin_size=self.state.dcr_bin_size,
            )

        # Remember the global histogram range and step
        self.n_dcr_max = n_dcr.max()
        self.dcr_bin_edges = dcr_bin_edges
        self.dcr_bin_centers = dcr_bin_centers
        self.dcr_bin_width = dcr_bin_width

        # Update the state and the ui element
        self.state.dcr_bin_size = self.dcr_bin_width
        self.ui.leBinSize.setText(f"{self.dcr_bin_width:.5f}")

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Create the bar chart
        chart = pg.BarGraphItem(
            x=self.dcr_bin_centers,
            height=n_dcr,
            width=0.9 * self.dcr_bin_width,
            brush=self.brush,
        )
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setXRange(0.0, 1.0)
        self.plot_widget.setYRange(0.0, self.n_dcr_max)
        self.plot_widget.setLabel("bottom", "Filtered dataset")
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.addItem(chart)
        self.plot_widget.scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu
        )

    @Slot()
    def preview_manual_assignment(self):
        """Preview the manual assignment."""

        if self.processor is None or self.processor.filtered_dataframe is None:
            return

        # Get the data for current fluorophore
        dcr = self.processor.filtered_dataframe["dcr"].to_numpy()
        if len(dcr) == 0:
            return

        # Get the threshold
        threshold = float(self.ui.leManualThreshold.text())

        # Keep track of the total number of elements for normalisation
        n_total = len(dcr)

        # Partition the data
        y_pred = dcr > threshold

        # Turn the prediction into a fluo_id
        fluo_ids = y_pred + 1

        # Reassign fluorophore IDs majority vote if necessary
        if self.state.num_fluorophores > 1:
            fluo_ids = reassign_fluo_ids_by_majority_vote(
                fluo_ids, self.processor.filtered_dataframe["tid"]
            )

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Calculate the final fluorophore IDs that will be assigned
        unique_cluster_ids = sorted(np.unique(fluo_ids).tolist())
        final_id_mapping = self._calculate_final_fluo_id_mapping(unique_cluster_ids)

        # Calculate the bar width as a function of the number of fluorophores
        bar_width = 0.9 / self.state.num_fluorophores
        offset = self.dcr_bin_width / self.state.num_fluorophores

        # Create new histograms (always 2 for manual assignment)
        for cluster_id in unique_cluster_ids:
            data = dcr[fluo_ids == cluster_id]
            if len(data) == 0:
                continue

            # Calculate the dcr histogram using the global bins
            n_dcr, _ = np.histogram(data, bins=self.dcr_bin_edges, density=False)

            # Normalize by the total count
            n_dcr = n_dcr / n_total

            # Get the final fluorophore ID that will be assigned to this cluster
            final_fluo_id = final_id_mapping[cluster_id]
            
            # Get the color for this fluorophore ID
            color_rgb = Colors()._get_fid_color(final_fluo_id, as_float=False)
            brush = pg.mkBrush(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 127)

            # Create the bar chart
            chart = pg.BarGraphItem(
                x=self.dcr_bin_centers + cluster_id * offset,
                height=n_dcr,
                width=bar_width * self.dcr_bin_width,
                brush=brush,
            )
            self.plot_widget.addItem(chart)

        # Store the predictions (1-shifted)
        self.assigned_fluorophore_ids = fluo_ids

        # Check if only one cluster was detected
        unique_fluo_ids = sorted(np.unique(fluo_ids).tolist())
        if len(unique_fluo_ids) == 1:
            # Only one cluster detected - no unmixing will occur
            self.fluorophore_naming_widget.setVisible(False)
            self.ui.pbManualAssign.setEnabled(False)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Split Detected",
                f"Only one cluster was detected with the current threshold."
            )
            return
        
        # Calculate the final fluorophore IDs that will be assigned
        final_id_mapping = self._calculate_final_fluo_id_mapping(unique_fluo_ids)
        
        # Show the FINAL fluorophore IDs (not cluster IDs) in the naming widget
        final_fluo_ids = sorted(final_id_mapping.values())
        self.fluorophore_naming_widget.set_fluorophores(
            final_fluo_ids,
            self.processor.fluorophore_names
        )
        self.fluorophore_naming_widget.setVisible(True)

        # Make sure to enable the assign button
        self.ui.pbManualAssign.setEnabled(True)

    def _calculate_final_fluo_id_mapping(self, cluster_ids):
        """Calculate the final fluorophore ID mapping for the given cluster IDs.
        
        Parameters
        ----------
        cluster_ids : list
            List of cluster IDs (e.g., [1, 2] for 2 clusters)
        
        Returns
        -------
        dict
            Mapping from cluster IDs to final fluorophore IDs
        """
        # Get the current fluorophore ID being unmixed
        current_fluo_id = self.processor.current_fluorophore_id
        
        # When there's only one fluorophore, the GUI shows only "All" (current_fluorophore_id = 0)
        # In this case, extract the actual fluorophore ID from the data
        if current_fluo_id == 0:
            filtered_df = self.processor.filtered_dataframe
            if filtered_df is not None and len(filtered_df) > 0:
                current_fluo_id = int(filtered_df['fluo'].iloc[0])
            else:
                current_fluo_id = 1
        
        # Get all existing fluorophore IDs from the full dataset
        all_existing_fluo_ids = set(np.unique(self.processor.processed_dataframe["fluo"].to_numpy()).astype(int))
        all_existing_fluo_ids.discard(0)  # Remove 0 if present
        
        # Build the mapping: first cluster keeps existing ID, others get new unused IDs
        final_id_mapping = {cluster_ids[0]: current_fluo_id}
        next_id = 1
        for i in range(1, len(cluster_ids)):
            while next_id in all_existing_fluo_ids or next_id in final_id_mapping.values():
                next_id += 1
            final_id_mapping[cluster_ids[i]] = next_id
            next_id += 1
        
        return final_id_mapping

    @Slot()
    def detect_fluorophores(self):
        """Detect fluorophores."""

        # Get the data for current fluorophore
        dcr = self.processor.filtered_dataframe["dcr"].to_numpy()
        if len(dcr) == 0:
            return

        # Fit the data to the requested number of clusters
        fluo_ids = assign_data_to_clusters(dcr, self.state.num_fluorophores, seed=42)

        # Reassign fluorophore IDs majority vote if necessary
        if self.state.num_fluorophores > 1:
            fluo_ids = reassign_fluo_ids_by_majority_vote(
                fluo_ids, self.processor.filtered_dataframe["tid"]
            )

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Calculate the final fluorophore IDs that will be assigned
        unique_cluster_ids = sorted(np.unique(fluo_ids).tolist())
        final_id_mapping = self._calculate_final_fluo_id_mapping(unique_cluster_ids)

        # Calculate the bar width as a function of the number of fluorophores
        bar_width = 0.9 / self.state.num_fluorophores
        offset = self.dcr_bin_width / self.state.num_fluorophores

        # Keep track of the total number of values for histogram normalization
        n_values = len(dcr)

        # Create new histograms
        for cluster_id in unique_cluster_ids:
            data = dcr[fluo_ids == cluster_id]
            if len(data) == 0:
                continue

            # Calculate the dcr histogram using the global bins
            n_dcr, _ = np.histogram(data, bins=self.dcr_bin_edges, density=False)

            # Normalize by the total count
            n_dcr = n_dcr / n_values

            # Get the final fluorophore ID that will be assigned to this cluster
            final_fluo_id = final_id_mapping[cluster_id]
            
            # Get the color for this fluorophore ID
            color_rgb = Colors()._get_fid_color(final_fluo_id, as_float=False)
            brush = pg.mkBrush(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 127)

            # Create the bar chart
            chart = pg.BarGraphItem(
                x=self.dcr_bin_centers + cluster_id * offset,
                height=n_dcr,
                width=bar_width * self.dcr_bin_width,
                brush=brush,
            )
            self.plot_widget.addItem(chart)

        # Store the predictions (1-shifted)
        self.assigned_fluorophore_ids = fluo_ids

        # Check if only one cluster was detected
        unique_fluo_ids = sorted(np.unique(fluo_ids).tolist())
        if len(unique_fluo_ids) == 1:
            # Only one cluster detected - no unmixing will occur
            self.fluorophore_naming_widget.setVisible(False)
            self.ui.pbAssign.setEnabled(False)
            # Show info message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Split Detected",
                f"Only one cluster was detected. The data cannot be split further."
            )
            return
        
        # Calculate the final fluorophore IDs that will be assigned
        final_id_mapping = self._calculate_final_fluo_id_mapping(unique_fluo_ids)
        
        # Show the FINAL fluorophore IDs (not cluster IDs) in the naming widget
        final_fluo_ids = sorted(final_id_mapping.values())
        self.fluorophore_naming_widget.set_fluorophores(
            final_fluo_ids,
            self.processor.fluorophore_names
        )
        self.fluorophore_naming_widget.setVisible(True)

        # Make sure to enable the assign button
        self.ui.pbAssign.setEnabled(True)

    @Slot()
    def assign_fluorophores_ids(self):
        """Assign the fluorophores ids with smart ID allocation."""

        if self.assigned_fluorophore_ids is None:
            return

        # Get unique new cluster IDs from unmixing (e.g., [1, 2] for 2 clusters)
        unique_unmixed_ids = sorted(np.unique(self.assigned_fluorophore_ids).astype(int).tolist())
        
        # Calculate the final fluorophore ID mapping
        new_fluo_id_mapping = self._calculate_final_fluo_id_mapping(unique_unmixed_ids)
        
        # Remap the assigned fluorophore IDs
        remapped_fluo_ids = np.array([new_fluo_id_mapping[fid] for fid in self.assigned_fluorophore_ids], dtype=np.uint8)
        
        # Get fluorophore names from the embedded widget
        # Note: The widget was populated with final fluorophore IDs, so the returned
        # dictionary already uses the correct final IDs as keys (no remapping needed)
        fluorophore_names = self.fluorophore_naming_widget.get_names()
        
        # Assign the IDs via the processor
        self.processor.set_fluorophore_ids(remapped_fluo_ids)
        
        # Set the fluorophore names (will update existing names, preserving others)
        if fluorophore_names:
            self.processor.set_fluorophore_names(fluorophore_names)
        
        # Reset to "All" fluorophores so the user can see all the newly created fluorophores
        # Otherwise, if we unmixed fluorophore 1 into [1, 2], and current_fluorophore_id is still 1,
        # only fluorophore 1 will be visible, making it seem like fluorophore 2 disappeared
        self.processor.current_fluorophore_id = 0

        # Inform that the fluorophore IDs have been assigned
        unique_final_fluo_ids = sorted(np.unique(remapped_fluo_ids).tolist())
        self.fluorophore_ids_assigned.emit(len(unique_final_fluo_ids))

        # Disable the button until the new detection is run
        self.ui.pbAssign.setEnabled(False)
        self.ui.pbManualAssign.setEnabled(False)

    def histogram_raise_context_menu(self, ev):
        """Create a context menu on the plot."""
        if ev.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            export_action = QAction("Export plot")
            export_action.triggered.connect(
                lambda checked: export_plot_interactive(ev.currentItem)
            )
            menu.addAction(export_action)
            pos = ev.screenPos()
            menu.exec(QPoint(int(pos.x()), int(pos.y())))
            ev.accept()
        else:
            ev.ignore()

    @Slot(int)
    def main_tab_changed(self, index):
        """Handle main tab changes to show/hide appropriate plots."""
        if index == 0:  # DCR unmixing tab
            self.plot_widget.show()
            self.time_plot_widget.hide()
        elif index == 1:  # Time splitting tab
            self.plot_widget.hide()
            self.time_plot_widget.show()
            self.plot_time_selected()

    @Slot()
    def plot_time_selected(self):
        """Plot the selected time analysis."""
        
        # Do we have something to plot?
        if (
            self.processor is None
            or self.processor.filtered_dataframe is None
            or len(self.processor.filtered_dataframe.index) == 0
        ):
            return
        
        # Always invalidate cache to ensure we're using current fluorophore selection
        self.invalidate_time_cache()
        
        # Clear existing plot items
        for item in self.time_plot_widget.allChildItems():
            self.time_plot_widget.removeItem(item)
        
        # Get the requested plot
        if self.ui.cbTimePlotType.currentIndex() == 0:
            self.plot_localizations_per_unit_time()
        elif self.ui.cbTimePlotType.currentIndex() == 1:
            self.plot_localization_precision_per_unit_time(std_err=False)
        elif self.ui.cbTimePlotType.currentIndex() == 2:
            self.plot_localization_precision_per_unit_time(std_err=True)
        else:
            raise ValueError("Unexpected plotting request.")
        
        self.time_plot_widget.setLabel("bottom", text="time (min)")
        self.time_plot_widget.showAxis("bottom")
        self.time_plot_widget.showAxis("left")
        self.time_plot_widget.setMouseEnabled(x=True, y=False)
        self.time_plot_widget.setMenuEnabled(False)
    
    def plot_localizations_per_unit_time(self):
        """Plot number of localizations per unit time."""
        cache_dict = {
            'data': self.localizations_per_unit_time_cache,
            'x_axis': self.time_x_axis
        }
        
        TimePlotter.plot_localizations_per_unit_time(
            self.time_plot_widget,
            self.processor,
            self.time_resolution_sec,
            cache_dict,
            self.brush
        )
        
        # Update cache references
        self.localizations_per_unit_time_cache = cache_dict['data']
        self.time_x_axis = cache_dict['x_axis']
    
    def plot_localization_precision_per_unit_time(self, std_err: bool = False):
        """Plot localization precision as a function of time.
        
        Parameters
        ----------
        std_err: bool
            Set to True to plot the standard error instead of the standard deviation.
        """
        cache_dict = {
            'x': self.localization_precision_per_unit_time_cache_x,
            'y': self.localization_precision_per_unit_time_cache_y,
            'z': self.localization_precision_per_unit_time_cache_z,
            'x_stderr': self.localization_precision_stderr_per_unit_time_cache_x,
            'y_stderr': self.localization_precision_stderr_per_unit_time_cache_y,
            'z_stderr': self.localization_precision_stderr_per_unit_time_cache_z,
            'x_axis': self.time_x_axis
        }
        
        TimePlotter.plot_localization_precision_per_unit_time(
            self.time_plot_widget,
            self.processor,
            self.time_resolution_sec,
            cache_dict,
            std_err
        )
        
        # Update cache references
        self.localization_precision_per_unit_time_cache_x = cache_dict['x']
        self.localization_precision_per_unit_time_cache_y = cache_dict['y']
        self.localization_precision_per_unit_time_cache_z = cache_dict['z']
        self.localization_precision_stderr_per_unit_time_cache_x = cache_dict['x_stderr']
        self.localization_precision_stderr_per_unit_time_cache_y = cache_dict['y_stderr']
        self.localization_precision_stderr_per_unit_time_cache_z = cache_dict['z_stderr']
        self.time_x_axis = cache_dict['x_axis']

    def _constrain_region_to_non_overlapping(self, changed_region):
        """Constrain a region to not overlap with other regions."""
        start, end = changed_region.getRegion()
        
        # Find the index of the changed region
        try:
            region_idx = self.time_split_regions.index(changed_region)
        except ValueError:
            return
        
        # Check against previous region (if exists)
        if region_idx > 0:
            prev_region = self.time_split_regions[region_idx - 1]
            prev_start, prev_end = prev_region.getRegion()
            
            # If start overlaps with previous region, push it to the right
            if start < prev_end:
                start = prev_end
                # Ensure minimum size
                if end <= start:
                    end = start + 1
                changed_region.setRegion([start, end])
                return
        
        # Check against next region (if exists)
        if region_idx < len(self.time_split_regions) - 1:
            next_region = self.time_split_regions[region_idx + 1]
            next_start, next_end = next_region.getRegion()
            
            # If end overlaps with next region, push it to the left
            if end > next_start:
                end = next_start
                # Ensure minimum size
                if start >= end:
                    start = end - 1
                changed_region.setRegion([start, end])
    
    @Slot()
    def split_by_time(self):
        """Split the data into equal time ranges."""
        
        if self.processor is None or self.processor.filtered_dataframe is None:
            return

        # Get time data in seconds and convert to minutes
        tim_data_sec = self.processor.filtered_dataframe["tim"].to_numpy()
        if len(tim_data_sec) == 0:
            return
        
        tim_data = tim_data_sec / 60.0  # Convert to minutes

        # Get number of splits
        num_splits = self.ui.sbNumSplits.value()
        
        # Calculate the time range in minutes
        tim_min = tim_data.min()
        tim_max = tim_data.max()
        tim_range = tim_max - tim_min
        
        # Calculate split size with small gaps (2% of range per gap)
        gap_fraction = 0.02
        total_gap = gap_fraction * tim_range * (num_splits - 1)
        usable_range = tim_range - total_gap
        split_size = usable_range / num_splits
        gap_size = gap_fraction * tim_range
        
        # Remove existing regions and disconnect signals
        for region in self.time_split_regions:
            try:
                region.sigRegionChanged.disconnect()
            except:
                pass
            self.time_plot_widget.removeItem(region)
        self.time_split_regions.clear()
        
        # Create new regions
        unique_cluster_ids = list(range(1, num_splits + 1))
        final_id_mapping = self._calculate_final_fluo_id_mapping(unique_cluster_ids)
        
        for i in range(num_splits):
            # Calculate start and end for this split (in minutes)
            start = tim_min + i * (split_size + gap_size)
            end = start + split_size
            
            # Get the final fluorophore ID for coloring
            final_fluo_id = final_id_mapping[i + 1]
            color_rgb = Colors()._get_fid_color(final_fluo_id, as_float=False)
            
            # Create the linear region
            region = pg.LinearRegionItem(
                values=[start, end],
                pen={'color': (int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2])), 'width': 3},
                brush=pg.mkBrush(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 50),
                movable=True,
            )
            
            # Store cluster ID as attribute for later retrieval
            region.cluster_id = i + 1
            
            # Connect signal to prevent overlaps
            region.sigRegionChanged.connect(lambda r=region: self._constrain_region_to_non_overlapping(r))
            
            self.time_plot_widget.addItem(region)
            self.time_split_regions.append(region)
        
        # Calculate initial assignments and show naming widget
        self._update_time_split_assignments()
        
    def _update_time_split_assignments(self):
        """Update fluorophore ID assignments based on current time region positions."""
        
        if self.processor is None or self.processor.filtered_dataframe is None:
            return
        
        if len(self.time_split_regions) == 0:
            return
        
        # Get time data in minutes
        tim_data_sec = self.processor.filtered_dataframe["tim"].to_numpy()
        tim_data = tim_data_sec / 60.0  # Convert to minutes
        
        # Initialize all as unassigned (0)
        fluo_ids = np.zeros(len(tim_data), dtype=np.uint8)
        
        # Assign based on regions (which are in minutes)
        for region in self.time_split_regions:
            start, end = region.getRegion()
            mask = (tim_data >= start) & (tim_data <= end)
            fluo_ids[mask] = region.cluster_id
        
        # Store assignments
        self.time_assigned_fluorophore_ids = fluo_ids
        
        # Calculate final fluorophore IDs
        unique_cluster_ids = sorted([r.cluster_id for r in self.time_split_regions])
        final_id_mapping = self._calculate_final_fluo_id_mapping(unique_cluster_ids)
        
        # Show the FINAL fluorophore IDs in the naming widget
        final_fluo_ids = sorted(final_id_mapping.values())
        self.fluorophore_naming_widget.set_fluorophores(
            final_fluo_ids,
            self.processor.fluorophore_names
        )
        self.fluorophore_naming_widget.setVisible(True)
        
        # Enable assign button
        self.ui.pbTimeSplitAssign.setEnabled(True)

    @Slot()
    def assign_time_split_fluorophores(self):
        """Assign fluorophore IDs based on time splitting."""
        
        if len(self.time_split_regions) == 0:
            return
        
        # Get time data in minutes
        tim_data_sec = self.processor.filtered_dataframe["tim"].to_numpy()
        tim_data = tim_data_sec / 60.0  # Convert to minutes
        
        # Get unique cluster IDs
        unique_cluster_ids = sorted([r.cluster_id for r in self.time_split_regions])
        
        # Calculate the final fluorophore ID mapping
        new_fluo_id_mapping = self._calculate_final_fluo_id_mapping(unique_cluster_ids)
        
        # Get fluorophore names from the widget
        fluorophore_names = self.fluorophore_naming_widget.get_names()
        
        # Build time ranges and apply filtering BEFORE assigning IDs
        # This ensures we only assign IDs to data within regions (no fluo_id=0)
        sorted_regions = sorted(self.time_split_regions, key=lambda r: r.getRegion()[0])
        
        time_ranges_to_keep = []
        for region in sorted_regions:
            start_min, end_min = region.getRegion()
            start_sec = start_min * 60.0
            end_sec = end_min * 60.0
            time_ranges_to_keep.append((start_sec, end_sec))
        
        first_start = time_ranges_to_keep[0][0]
        last_end = time_ranges_to_keep[-1][1]
        
        # Apply filters BEFORE assigning IDs (first pass)
        self.processor.filter_by_1d_range("tim", (first_start, last_end))
        
        for i in range(len(time_ranges_to_keep) - 1):
            gap_start = time_ranges_to_keep[i][1]
            gap_end = time_ranges_to_keep[i + 1][0]
            if gap_end > gap_start:
                self.processor.filter_by_1d_range_complement("tim", (gap_start, gap_end))
        
        # Now get filtered time data - only contains data within regions
        tim_data_sec = self.processor.filtered_dataframe["tim"].to_numpy()
        tim_data = tim_data_sec / 60.0  # Convert to minutes
        
        # Build fluorophore ID assignments (all will be non-zero)
        fluo_ids = np.zeros(len(tim_data), dtype=np.uint8)
        
        for region in self.time_split_regions:
            start, end = region.getRegion()  # These are in minutes
            mask = (tim_data >= start) & (tim_data <= end)
            fluo_ids[mask] = new_fluo_id_mapping[region.cluster_id]
        
        # Assign the fluorophore IDs (this will reset filters via _init_selected_rows_dict)
        self.processor.set_fluorophore_ids(fluo_ids)
        
        # Set the fluorophore names
        if fluorophore_names:
            self.processor.set_fluorophore_names(fluorophore_names)
        
        # Re-apply filters AFTER set_fluorophore_ids() (second pass - necessary!)
        # set_fluorophore_ids() calls _init_selected_rows_dict() which clears filters
        self.processor.filter_by_1d_range("tim", (first_start, last_end))
        
        for i in range(len(time_ranges_to_keep) - 1):
            gap_start = time_ranges_to_keep[i][1]
            gap_end = time_ranges_to_keep[i + 1][0]
            if gap_end > gap_start:
                self.processor.filter_by_1d_range_complement("tim", (gap_start, gap_end))
        
        # Reset to "All" fluorophores
        self.processor.current_fluorophore_id = 0
        
        # Inform that the fluorophore IDs have been assigned
        unique_final_fluo_ids = sorted(new_fluo_id_mapping.values())
        self.fluorophore_ids_assigned.emit(len(unique_final_fluo_ids))
        
        # Disable the button until new split is performed
        self.ui.pbTimeSplitAssign.setEnabled(False)
        
        # Close the dialog
        self.close()
