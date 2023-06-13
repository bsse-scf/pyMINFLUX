#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
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

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QPoint,
    QThread,
    QWaitCondition,
    Signal,
    Slot,
)
from PySide6.QtGui import QAction, QDoubleValidator, QIntValidator, Qt
from PySide6.QtWidgets import QDialog, QMenu

from ..fourier import estimate_resolution_by_frc
from ..processor import MinFluxProcessor
from ..state import State
from .helpers import export_plot_interactive
from .ui_frc_tool import Ui_FRCTool


class LocalWorker(QThread):

    # Signal progress and completion
    processing_started = Signal()
    processing_progress_updated = Signal(int)
    processing_interrupted = Signal()
    processing_finished = Signal()

    def __init__(self, processor, t_start, t_steps, sxy, rx, ry, n_reps):
        """Constructor."""
        super().__init__()

        # Set arguments
        self.processor = processor
        self.t_start = t_start
        self.t_steps = t_steps
        self.sxy = sxy
        self.rx = rx
        self.ry = ry
        self.n_reps = n_reps
        self.all_resolutions = None

        # Set up mutexes and wait conditions
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.is_interrupted = False

    def run(self):
        """Run the computation."""

        # Signal start
        self.processing_started.emit()

        # Allocate space for the results
        self.all_resolutions = np.empty(len(self.t_steps), dtype=np.float32)
        self.all_resolutions.fill(np.nan)

        # Process all time steps
        for i, t in enumerate(self.t_steps):

            with QMutexLocker(self.mutex):
                if self.is_interrupted:
                    self.processing_interrupted.emit()
                    return

            # Extract the data
            df = self.processor.select_by_1d_range("tim", x_range=(self.t_start, t))
            x = df["x"].values
            y = df["y"].values

            # Extimate the resolution by FRC
            resolution, _, _ = estimate_resolution_by_frc(
                x=x,
                y=y,
                sx=self.sxy,
                sy=self.sxy,
                rx=self.rx,
                ry=self.ry,
                num_reps=self.n_reps,
                seed=2023,
                return_all=False,
            )

            # Store the resolution
            self.all_resolutions[i] = 1e9 * resolution

            # Signal progress
            self.processing_progress_updated.emit(
                int(np.round(100 * (i + 1) / len(self.t_steps)))
            )

        # Signal completion
        self.processing_finished.emit()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.is_interrupted = True


class FRCTool(QDialog, Ui_FRCTool):
    def __init__(self, minfluxprocessor: MinFluxProcessor, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_FRCTool()
        self.ui.setupUi(self)

        # Store the reference to the reader
        self.processor = minfluxprocessor

        # Keep reference to the plot
        self.frc_plot = None

        # Keep a reference to the singleton State class
        self.state = State()

        # Create widgets
        self.create_widgets()

        # Keep a reference to the local worker
        self.worker = None

        # Hide the progress bar
        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setVisible(False)
        self.ui.pbInterrupt.setVisible(False)

        # Keep track of whether there is a plot to export
        self.plot_ready_to_export = False

        #
        # Set defaults
        #

        # Lateral (xy) resolution
        self.ui.leLateralResolution.setText(str(self.state.frc_lateral_resolution))
        self.ui.leNumRepeats.setValidator(QDoubleValidator(bottom=0.0, decimals=2))

        # Temporal (s) resolution
        self.ui.leTemporalResolution.setText(str(self.state.frc_temporal_resolution))
        self.ui.leTemporalResolution.setValidator(
            QDoubleValidator(bottom=0.0, decimals=1)
        )

        # Number of repeats
        self.ui.leNumRepeats.setText(str(self.state.frc_num_repeats))
        self.ui.leNumRepeats.setValidator(QIntValidator(bottom=0))

        # Set signal-slot connections
        self.setup_conn()

    def setup_conn(self):
        """Set up signal-slot connections."""

        self.ui.pbRunFRCAnalysis.clicked.connect(self.run_frc_analysis)
        self.ui.pbInterrupt.clicked.connect(self.stop_frc_analysis)
        self.ui.leLateralResolution.textChanged.connect(
            self.persist_frc_lateral_resolution
        )
        self.ui.leTemporalResolution.textChanged.connect(
            self.persist_frc_temporal_resolution
        )

        self.ui.leNumRepeats.textChanged.connect(self.persist_frc_num_repeats)

    def create_widgets(self):
        """Create widgets."""

        # Parameters Layout
        self.frc_plot = pg.PlotWidget(parent=self, background="w", title="")
        self.frc_plot.setMouseEnabled(x=True, y=True)
        self.frc_plot.setMenuEnabled(False)
        self.frc_plot.hideAxis("bottom")
        self.frc_plot.hideAxis("left")
        self.frc_plot.scene().sigMouseClicked.connect(self.raise_context_menu)
        self.ui.hlPlot.addWidget(self.frc_plot)
        self.frc_plot.show()

    def keyPressEvent(self, ev):
        """Key press event."""

        # Do not capture key events for now
        ev.ignore()

    def set_processor(self, minfluxprocessor: MinFluxProcessor):
        """Reset the internal state."""
        self.processor = minfluxprocessor

    @Slot(name="run_frc_analysis")
    def run_frc_analysis(self):
        """Run FRC analysis to estimate signal resolution."""

        # Mark that there is no plot ready to export
        self.plot_ready_to_export = False

        # Get the parameters
        sxy = self.state.frc_lateral_resolution
        t_step = self.state.frc_temporal_resolution
        n_reps = self.state.frc_num_repeats

        # Create the list of time steps to consider
        t_start = self.processor.filtered_dataframe["tim"].min()
        t_end = self.processor.filtered_dataframe["tim"].max()
        n_steps = int(np.round((t_end - t_start) / t_step))
        t_steps = np.linspace(t_start, t_end, n_steps)
        t_steps = t_steps[1:]

        # Set the spatial ranges
        rx = (
            self.processor.filtered_dataframe["x"].min(),
            self.processor.filtered_dataframe["x"].max(),
        )
        ry = (
            self.processor.filtered_dataframe["y"].min(),
            self.processor.filtered_dataframe["y"].max(),
        )

        # Create a new worker
        if self.worker is not None:
            del self.worker
        self.worker = LocalWorker(self.processor, t_start, t_steps, sxy, rx, ry, n_reps)
        self.worker.processing_started.connect(self.update_ui_on_process_start)
        self.worker.processing_progress_updated.connect(self.update_progress_bar)
        self.worker.processing_interrupted.connect(self.update_ui_on_process_end)
        self.worker.processing_interrupted.connect(self.collect_results_and_plot)
        self.worker.processing_finished.connect(self.update_ui_on_process_end)
        self.worker.processing_finished.connect(self.collect_results_and_plot)

        # Now process in the local worker
        self.worker.start()

    @Slot(name="stop_frc_analysis")
    def stop_frc_analysis(self):
        if self.worker is None:
            return
        self.worker.stop()

    @Slot(str, name="persist_frc_lateral_resolution")
    def persist_frc_lateral_resolution(self, text):
        try:
            frc_lateral_resolution = float(text)
        except ValueError as _:
            return
        self.state.frc_lateral_resolution = frc_lateral_resolution

    @Slot(str, name="persist_frc_temporal_resolution")
    def persist_frc_temporal_resolution(self, text):
        try:
            frc_temporal_resolution = float(text)
        except ValueError as _:
            return
        self.state.frc_temporal_resolution = frc_temporal_resolution

    @Slot(str, name="persist_frc_num_repeats")
    def persist_frc_num_repeats(self, text):
        try:
            frc_num_repeats = int(text)
        except ValueError as _:
            return
        self.state.frc_num_repeats = frc_num_repeats

    @Slot(int, name="update_progress_bar")
    def update_progress_bar(self, value):
        self.ui.progress_bar.setValue(value)

    def plot(self, time_steps, resolutions):
        """Plot histograms."""

        # Clear the plot
        self.clear_plot()

        # Show x and y grids
        self.frc_plot.showGrid(x=True, y=True)

        # Set properties of the label for y axis
        self.frc_plot.setLabel("left", "Resolution [nm]")

        # Set properties of the label for x axis
        self.frc_plot.setLabel("bottom", "Acquisition time", units="s")

        # Set axis ranges
        self.frc_plot.setXRange(time_steps[0], time_steps[-1])
        self.frc_plot.setYRange(np.nanmin(resolutions), np.nanmax(resolutions))

        # Plot resolution vs. time step
        self.frc_plot.plot(time_steps, resolutions, pen=pg.mkPen("r", width=3))

    def clear_plot(self):
        """Clear the plot."""

        for item in self.frc_plot.allChildItems():
            print(type(item))
            self.frc_plot.removeItem(item)

    def update_ui_on_process_start(self):
        """Disable elements and inform that a processing is ongoing."""

        # Disable all parameter widgets
        self.ui.lbLateralResolution.setEnabled(False)
        self.ui.leLateralResolution.setEnabled(False)
        self.ui.lbTemporalResolution.setEnabled(False)
        self.ui.leTemporalResolution.setEnabled(False)
        self.ui.lbNumRepeats.setEnabled(False)
        self.ui.leNumRepeats.setEnabled(False)
        self.ui.pbRunFRCAnalysis.setEnabled(False)

        # However, we make the progress bar visible
        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setVisible(True)
        self.ui.pbInterrupt.setVisible(True)

    def update_ui_on_process_end(self):
        """Disable elements and inform that a processing is ongoing."""

        # Enable all parameter widgets
        self.ui.lbLateralResolution.setEnabled(True)
        self.ui.leLateralResolution.setEnabled(True)
        self.ui.lbTemporalResolution.setEnabled(True)
        self.ui.leTemporalResolution.setEnabled(True)
        self.ui.lbNumRepeats.setEnabled(True)
        self.ui.leNumRepeats.setEnabled(True)
        self.ui.pbRunFRCAnalysis.setEnabled(True)

        # However, we make the progress bar invisible
        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setVisible(False)
        self.ui.pbInterrupt.setVisible(False)

    def collect_results_and_plot(self):
        """Collect results from the local worked and plot them."""

        if self.worker is None:
            return

        # Collect the results
        t_steps = self.worker.t_steps
        all_resolutions = self.worker.all_resolutions

        # Update plot
        self.plot(t_steps, all_resolutions)

        # Mark that there is a plot ready  to export
        self.plot_ready_to_export = True

    def raise_context_menu(self, ev):
        """Create a context menu on the plot."""
        if ev.button() == Qt.MouseButton.RightButton:
            if not self.plot_ready_to_export:
                return

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
