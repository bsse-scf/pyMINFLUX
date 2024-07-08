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

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget

from ..reader import MinFluxReader
from ..state import State
from .colors import ColorCode
from .ui_plotter_toolbar import Ui_PlotterToolbar


class PlotterToolbar(QWidget, Ui_PlotterToolbar):

    # Signals
    plot_requested_parameters = Signal()
    color_code_locs_changed = Signal(int)
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
        self.ui.cbFirstParam.addItems(self.plotting_parameters)
        self.ui.cbFirstParam.setCurrentIndex(self.plotting_parameters.index("x"))
        self.ui.cbSecondParam.addItems(self.plotting_parameters)
        self.ui.cbSecondParam.setCurrentIndex(self.plotting_parameters.index("y"))

        self.ui.cbFirstParam.currentIndexChanged.connect(self.persist_first_param)
        self.ui.cbFirstParam.currentIndexChanged.connect(self.toggle_average_state)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.persist_second_param)
        self.ui.cbSecondParam.currentIndexChanged.connect(self.toggle_average_state)

        # Plot
        self.ui.pbPlot.clicked.connect(self.emit_plot_requested)

        # Color-code combo box
        self.ui.cbColorCodeSelector.setCurrentIndex(0)
        self.ui.cbColorCodeSelector.currentIndexChanged.connect(
            self.persist_color_code_and_broadcast
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

    @Slot(int)
    def persist_plot_average_localisations_and_broadcast(self, value):
        """Persist the selection for plotting average positions and broadcast the change."""
        if value == Qt.CheckState.Checked.value:
            self.state.plot_average_localisations = True
        else:
            self.state.plot_average_localisations = False
        self.plot_average_positions_state_changed.emit()

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

    @Slot(int)
    def toggle_average_state(self, index):
        """Persist the selection for the second parameter."""

        # Enable the Average checkbox only for x, y plots
        if (
            not self.state.is_tracking
            and self.state.x_param in ["x", "y"]
            and self.state.y_param in ["x", "y"]
        ):
            self.ui.cbPlotAveragePos.setEnabled(True)
        else:
            self.ui.cbPlotAveragePos.setEnabled(False)

    @Slot(int)
    def persist_color_code_and_broadcast(self, index):
        """Persist the selection of the color code and broadcast a change."""
        self.state.color_code = ColorCode(index)

        # Broadcast the change
        self.color_code_locs_changed.emit(self.state.color_code.value)

    @Slot(int)
    def persist_first_param(self, index):
        """Persist the selection for the first parameter."""

        # Persist the selection
        self.state.x_param = self.plotting_parameters[index]

    @Slot(int)
    def persist_second_param(self, index):
        """Persist the selection for the second parameter."""

        # Persist the selection
        self.state.y_param = self.plotting_parameters[index]

    @Slot()
    def emit_plot_requested(self):
        """Plot the requested parameters."""

        # Emit signal
        self.plot_requested_parameters.emit()

    def reset(self):
        """Reset the toolbar."""
        if self.state.is_tracking and self.state.plot_average_localisations:
            print(
                "DEBUG: Inconsistent state! Both `self.state.is_tracking` and `self.state.plot_average_localisations` are true!"
            )
            self.state.plot_average_localisations = False
        self.toggle_average_state(None)
