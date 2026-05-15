#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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

import pandas as pd
from PySide6.QtCore import QSignalBlocker, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget

from pyminflux.ui.state import State

from ..reader import MinFluxReader
from .ui_plotter_toolbar import Ui_PlotterToolbar


class PlotterToolbar(QWidget, Ui_PlotterToolbar):

    # Signals
    plot_requested_parameters = Signal()
    color_column_changed = Signal()
    plot_average_positions_state_changed = Signal()
    plotter_changed = Signal()
    plotter_projection_changed = Signal()

    def __init__(self):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_PlotterToolbar()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # The main plotter does not focus on temporal measurement
        self.plotting_parameters = MinFluxReader.processed_properties()

        # Add the values to the plot properties combo boxes (without time)
        self.set_plotting_columns(self.plotting_parameters)

        self.ui.cbFirstParam.currentIndexChanged.connect(self.persist_first_param)
        self.ui.cbFirstParam.currentIndexChanged.connect(self.toggle_average_state)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.persist_second_param)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.toggle_average_state)

        # Plot
        self.ui.pbPlot.clicked.connect(self.emit_plot_requested)

        # Color column combo box
        self.set_available_color_columns([])
        self.ui.cbColorColumnSelector.currentIndexChanged.connect(
            self.persist_color_column_and_broadcast
        )

        # Set the state of the 3D checkbox
        self.ui.cbPlot3D.setChecked(self.state.plot_3d)
        self.ui.cbProjection.setCurrentIndex(0 if self.state.plot_3d_orthogonal else 1)
        self.update_ui()
        self.ui.cbPlot3D.stateChanged.connect(self.persist_plot_3d_and_broadcast)
        self.ui.cbProjection.currentIndexChanged.connect(
            self.persist_plot_3d_projection_and_broadcast
        )

        # Set the state of the average checkbox
        self.ui.cbPlotAveragePos.setChecked(self.state.plot_average_localisations)
        self.ui.cbPlotAveragePos.stateChanged.connect(
            self.persist_plot_average_localisations_and_broadcast
        )

        # Hide the MINFLUX and Confocal checkboxes
        self.ui.cbShowMinflux.setChecked(self.state.show_localizations)
        self.ui.cbShowConfocal.setChecked(self.state.show_confocal)
        self.ui.cbShowConfocal.stateChanged.connect(
            self.persist_show_confocal_and_broadcast
        )
        self.ui.cbShowMinflux.stateChanged.connect(
            self.persist_show_minflux_and_broadcast
        )
        self.disable_minflux_confocal_controls()

    @Slot(int)
    def persist_plot_average_localisations_and_broadcast(self, value):
        """Persist the selection for plotting average positions and broadcast the change."""
        if value == Qt.CheckState.Checked.value:
            self.state.plot_average_localisations = True
        else:
            self.state.plot_average_localisations = False
        self.plot_average_positions_state_changed.emit()

    @Slot(int)
    def persist_show_confocal_and_broadcast(self, value):
        """Persist the state of the show confocal selection and broadcast the change."""
        if value == Qt.CheckState.Checked.value:
            self.state.show_confocal = True
        else:
            self.state.show_confocal = False
        self.update_ui()
        self.plot_requested_parameters.emit()

    @Slot(int)
    def persist_show_minflux_and_broadcast(self, value):
        """Persist the state of the show confocal selection and broadcast the change."""
        if value == Qt.CheckState.Checked.value:
            self.state.show_localizations = True
        else:
            self.state.show_localizations = False
        self.update_ui()
        self.plot_requested_parameters.emit()

    @Slot(int)
    def persist_plot_3d_and_broadcast(self, value):
        """Persist the selection for 2D vs. 3D plotting and update the UI."""
        if value == Qt.CheckState.Checked.value:
            self.state.plot_3d = True
        else:
            self.state.plot_3d = False
        self.update_ui()
        self.plotter_changed.emit()

    @Slot(int)
    def persist_plot_3d_projection_and_broadcast(self, index):
        """Persist the selection for 2D vs. 3D plotting projection and update the UI."""
        self.state.plot_3d_orthogonal = index == 0
        self.update_ui()
        self.plotter_projection_changed.emit()

    def update_ui(self):
        """Update UI elements as a function of the plotter type."""
        self.ui.cbProjection.setVisible(self.state.plot_3d)
        self.ui.line.setVisible(not self.state.plot_3d)
        self.ui.cbFirstParam.setVisible(not self.state.plot_3d)
        self.ui.cbSecondParam.setVisible(not self.state.plot_3d)
        self.ui.pbPlot.setVisible(not self.state.plot_3d)
        self.ui.cbShowMinflux.setVisible(not self.state.plot_3d)
        self.ui.cbShowConfocal.setVisible(not self.state.plot_3d)

    @Slot(int)
    def toggle_average_state(self, index):
        """Persist the selection for the second parameter."""

        # Enable the Average checkbox only for x, y plots
        if (
            not self.state.is_tracking
            and self.state.x_param in ["x", "y", "z"]
            and self.state.y_param in ["x", "y", "z"]
        ):
            self.ui.cbPlotAveragePos.setEnabled(True)
        else:
            # For clarity, disable and also unckeck
            self.ui.cbPlotAveragePos.setEnabled(False)
            self.ui.cbPlotAveragePos.setChecked(False)

    @Slot(int)
    def persist_color_column_and_broadcast(self, index):
        """Persist the selected color column and broadcast a change."""
        self.state.color_column = self.ui.cbColorColumnSelector.itemData(index)

        # Broadcast the change
        self.color_column_changed.emit()

    @Slot(int)
    def persist_first_param(self, index):
        """Persist the selection for the first parameter."""
        if index < 0 or index >= len(self.plotting_parameters):
            return

        # Persist the selection
        self.state.x_param = self.plotting_parameters[index]

    @Slot(int)
    def persist_second_param(self, index):
        """Persist the selection for the second parameter."""
        if index < 0 or index >= len(self.plotting_parameters):
            return

        # Persist the selection
        self.state.y_param = self.plotting_parameters[index]

    def set_plot_dataframe_schema(
        self,
        dataframe: pd.DataFrame | None,
        color_columns: list[str] | None = None,
    ):
        """Populate plot controls from the active workflow's plot dataframe."""
        if dataframe is None:
            self.set_plotting_columns(MinFluxReader.processed_properties())
            self.set_available_color_columns([])
            return

        numeric_columns = [
            column
            for column in dataframe.columns
            if pd.api.types.is_numeric_dtype(dataframe[column])
        ]
        self.set_plotting_columns(numeric_columns)

        if color_columns is None:
            color_columns = []
        self.set_available_color_columns(color_columns)

    def set_plotting_columns(self, columns, preferred_x="x", preferred_y="y"):
        """Populate X/Y plotting parameter controls."""
        columns = list(columns)
        if not columns:
            columns = ["x", "y"]

        previous_x = self.state.x_param if self.state.x_param in columns else preferred_x
        previous_y = self.state.y_param if self.state.y_param in columns else preferred_y
        if previous_x not in columns:
            previous_x = columns[0]
        if previous_y not in columns:
            previous_y = columns[1] if len(columns) > 1 else columns[0]

        first_blocker = QSignalBlocker(self.ui.cbFirstParam)
        second_blocker = QSignalBlocker(self.ui.cbSecondParam)
        first_blocker.reblock()
        second_blocker.reblock()

        self.plotting_parameters = columns
        self.ui.cbFirstParam.clear()
        self.ui.cbSecondParam.clear()
        self.ui.cbFirstParam.addItems(columns)
        self.ui.cbSecondParam.addItems(columns)
        self.ui.cbFirstParam.setCurrentIndex(columns.index(previous_x))
        self.ui.cbSecondParam.setCurrentIndex(columns.index(previous_y))

        first_blocker.unblock()
        second_blocker.unblock()

        self.state.x_param = previous_x
        self.state.y_param = previous_y
        self.toggle_average_state(None)

    def set_available_color_columns(self, color_columns):
        """Populate color controls from allowed dataframe columns."""
        color_columns = [
            column
            for column in color_columns
            if isinstance(column, str)
        ]
        current = (
            self.state.color_column
            if self.state.color_column in color_columns
            else None
        )

        blocker = QSignalBlocker(self.ui.cbColorColumnSelector)
        blocker.reblock()
        self.ui.cbColorColumnSelector.clear()
        self.ui.cbColorColumnSelector.addItem("nothing", None)
        for column in color_columns:
            self.ui.cbColorColumnSelector.addItem(column, column)
        self.ui.cbColorColumnSelector.setCurrentIndex(
            0 if current is None else color_columns.index(current) + 1
        )
        blocker.unblock()

        self.state.color_column = current

    @Slot()
    def emit_plot_requested(self):
        """Plot the requested parameters."""

        # Emit signal
        self.plot_requested_parameters.emit()

    @Slot()
    def disable_minflux_confocal_controls(self):
        """Hide the controls to toggle the minflux and confocal plots."""
        self.ui.cbShowMinflux.setChecked(self.state.show_localizations)
        self.ui.cbShowConfocal.setChecked(self.state.show_confocal)
        enabled = self.state.show_confocal
        self.ui.cbShowMinflux.setEnabled(enabled)
        self.ui.cbShowConfocal.setEnabled(enabled)
        self.ui.cbShowMinflux.setVisible(False)
        self.ui.cbShowConfocal.setVisible(False)

    @Slot()
    def enable_minflux_confocal_controls(self):
        """Show the controls to toggle the minflux and confocal plots."""
        self.ui.cbShowMinflux.setChecked(self.state.show_localizations)
        self.ui.cbShowConfocal.setChecked(self.state.show_confocal)
        enabled = self.state.show_confocal
        self.ui.cbShowMinflux.setEnabled(enabled)
        self.ui.cbShowConfocal.setEnabled(enabled)
        self.ui.cbShowMinflux.setVisible(True)
        self.ui.cbShowConfocal.setVisible(True)

    def reset(self):
        """Reset the toolbar."""
        if self.state.is_tracking and self.state.plot_average_localisations:
            print(
                "DEBUG: Inconsistent state! Both `self.state.is_tracking` and `self.state.plot_average_localisations` are true!"
            )
            self.state.plot_average_localisations = False
        self.toggle_average_state(None)

        # Disable minflux/confocal plotting controls
        if not self.state.has_confocal:
            self.disable_minflux_confocal_controls()
