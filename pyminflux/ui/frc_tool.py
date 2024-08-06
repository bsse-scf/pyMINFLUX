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

import warnings

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPoint, Slot
from PySide6.QtGui import QAction, QDoubleValidator, QIntValidator, Qt
from PySide6.QtWidgets import QDialog, QMenu

from ..processor import MinFluxProcessor
from ..state import State
from ..threads.frc import FRCProcessorThread
from .helpers import export_plot_interactive
from .ui_frc_tool import Ui_FRCTool


class FRCTool(QDialog, Ui_FRCTool):
    def __init__(self, processor: MinFluxProcessor):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_FRCTool()
        self.ui.setupUi(self)

        # Store the reference to the reader
        self.processor = processor

        # Keep reference to the plot
        self.frc_plot = None

        # Keep a reference to the singleton State class
        self.state = State()

        # Create widgets
        self.create_widgets()

        # Keep a reference to the processor thread
        self.processor_thread = None

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
        self.ui.leNumRepeats.setValidator(
            QDoubleValidator(bottom=0.0, top=np.inf, decimals=2)
        )

        # Temporal (s) resolution
        self.ui.leTemporalResolution.setText(str(self.state.frc_temporal_resolution))
        self.ui.leTemporalResolution.setValidator(
            QDoubleValidator(bottom=0.0, top=np.inf, decimals=1)
        )

        # Endpoint estimation
        self.ui.cbEndpoint.setChecked(self.state.frc_endpoint_only)
        self.ui.lbTemporalResolution.setEnabled(True)
        self.ui.leTemporalResolution.setEnabled(True)
        if self.state.frc_endpoint_only:
            self.ui.lbTemporalResolution.setEnabled(False)
            self.ui.leTemporalResolution.setEnabled(False)

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
        self.ui.cbEndpoint.stateChanged.connect(self.persist_frc_endpoint_only)

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

    def set_processor(self, processor: MinFluxProcessor):
        """Reset the internal state."""
        self.processor = processor

    @Slot(int)
    def persist_frc_endpoint_only(self, value):
        """Persist the selection for plotting average positions."""
        if value == Qt.CheckState.Checked.value:
            self.state.frc_endpoint_only = True
            self.ui.lbTemporalResolution.setEnabled(False)
            self.ui.leTemporalResolution.setEnabled(False)
        else:
            self.state.frc_endpoint_only = False
            self.ui.lbTemporalResolution.setEnabled(True)
            self.ui.leTemporalResolution.setEnabled(True)

    @Slot()
    def run_frc_analysis(self):
        """Run FRC analysis to estimate signal resolution."""

        if self.frc_plot is None:
            raise Exception("The PlotWidget object is not ready!")

        if self.processor is None or self.processor.filtered_dataframe is None:
            return

        # Mark that there is no plot ready to export
        self.plot_ready_to_export = False

        # Is there data to process?
        if len(self.processor.filtered_dataframe.index) == 0:
            self.frc_plot.setTitle("No data.")
            return

        # Get the common parameters
        sxy = self.state.frc_lateral_resolution
        n_reps = self.state.frc_num_repeats

        # Set the spatial ranges
        rx = (
            self.processor.filtered_dataframe["x"].min(),
            self.processor.filtered_dataframe["x"].max(),
        )
        ry = (
            self.processor.filtered_dataframe["y"].min(),
            self.processor.filtered_dataframe["y"].max(),
        )

        # Prepare the arguments for the AutoUpdateCheckerWorker
        t_start = self.processor.filtered_dataframe["tim"].min()
        t_end = self.processor.filtered_dataframe["tim"].max()

        # Run temporal analysis or endpoint estimation?
        if self.state.frc_endpoint_only:
            # We only consider one step with the whole data
            t_steps = [t_end + 1.0]

        else:
            # Create the list of time steps to consider
            t_step = self.state.frc_temporal_resolution
            n_steps = int(np.round((t_end - t_start) / t_step))
            t_steps = np.linspace(t_start, t_end, n_steps)
            t_steps = t_steps[1:]

        # Create the new processor_thread
        if self.processor_thread is not None:
            del self.processor_thread
        self.processor_thread = FRCProcessorThread(
            self.processor, t_start, t_steps, sxy, rx, ry, n_reps
        )
        self.processor_thread.processing_started.connect(
            self.update_ui_on_process_start
        )
        self.processor_thread.processing_progress_updated.connect(
            self.update_progress_bar
        )
        self.processor_thread.processing_interrupted.connect(
            self.update_ui_on_process_end
        )
        self.processor_thread.processing_interrupted.connect(
            self.collect_results_and_plot
        )
        self.processor_thread.processing_finished.connect(self.update_ui_on_process_end)
        self.processor_thread.processing_finished.connect(self.collect_results_and_plot)

        # Now process in the local processor_thread
        self.processor_thread.start()

    @Slot()
    def stop_frc_analysis(self):
        if self.processor_thread is None:
            return
        self.processor_thread.stop()

    @Slot(str)
    def persist_frc_lateral_resolution(self, text):
        try:
            frc_lateral_resolution = float(text)
        except ValueError as _:
            return
        self.state.frc_lateral_resolution = frc_lateral_resolution

    @Slot(str)
    def persist_frc_temporal_resolution(self, text):
        try:
            frc_temporal_resolution = float(text)
        except ValueError as _:
            return
        self.state.frc_temporal_resolution = frc_temporal_resolution

    @Slot(str)
    def persist_frc_num_repeats(self, text):
        try:
            frc_num_repeats = int(text)
        except ValueError as _:
            return
        self.state.frc_num_repeats = frc_num_repeats

    @Slot(int)
    def update_progress_bar(self, value):
        self.ui.progress_bar.setValue(value)

    def plot(self, time_steps, resolutions):
        """Plot histograms."""

        if self.frc_plot is None:
            raise Exception("The PlotWidget object is not ready!")

        # Clear the plot
        self.clear_plot()

        # Show x and y grids
        self.frc_plot.showGrid(x=True, y=True)

        # Set properties of the label for y-axis
        self.frc_plot.setLabel("left", "Resolution [nm]")

        # Set properties of the label for x-axis
        self.frc_plot.setLabel("bottom", "Acquisition time", units="s")

        if self.state.frc_endpoint_only:
            # Time steps to use
            time_steps = [time_steps[0] - 1.0]

        # Calculate the mean and standard error of the replicates
        with warnings.catch_warnings():
            # Silence the warning on np.nanmean() for the case that all
            # columns in one or more rows are NaN because the user
            # interrupted the processing.
            warnings.simplefilter("ignore")
            mean_res = np.nanmean(resolutions, axis=1)
            std_res = np.nanstd(resolutions, axis=1, ddof=1)
            se_res = std_res / np.sqrt(resolutions.shape[1])

        # Plot resolution vs. time step
        if len(time_steps) > 1:
            self.frc_plot.plot(time_steps, mean_res, pen=pg.mkPen("r", width=5))
            # Create custom error bars
            for ti, ri, ei in zip(time_steps, mean_res, se_res):
                if np.isnan(ri):
                    continue
                v_line = pg.PlotCurveItem(
                    [ti, ti], [ri - ei, ri + ei], pen=pg.mkPen(color="k", width=3)
                )
                self.frc_plot.addItem(v_line)

            # Set plot x range
            x_range = [time_steps[0], time_steps[-1]]

            # Extract the endpoint resolution (or the last
            # valid if the processing was interrupted)
            res = mean_res[np.isfinite(mean_res)][-1]
            se = se_res[np.isfinite(mean_res)][-1]
        else:
            r = np.nanmean(resolutions, axis=1)[0]
            self.frc_plot.plot(
                [time_steps[0] - 0.1, time_steps[0] + 0.1],
                [r, r],
                pen=pg.mkPen("r", width=5),
            )
            # Create custom error bar
            line = pg.PlotCurveItem(
                [time_steps[0], time_steps[0]],
                [mean_res[0] - se_res[0], mean_res[0] + se_res[0]],
                pen=pg.mkPen(color="k", width=3),
            )
            self.frc_plot.addItem(line)

            # Set plot x range
            x_range = [time_steps[0] - 0.5, time_steps[0] + 0.5]

            # Endpoint resolution
            res = mean_res[0]
            se = se_res[0]

        # Calculate an appropriate y-axis range
        mx = np.nanmax(mean_res + se_res)
        mn = np.nanmin(mean_res - se_res)
        margin = 0.1 * (mx - mn)

        # Set axis ranges
        self.frc_plot.setXRange(x_range[0], x_range[1])
        self.frc_plot.setYRange(mn - margin, mx + margin)

        # Display the endpoint resolution in the plot title
        if np.any(np.isnan(mean_res)):
            self.frc_plot.setTitle(
                f"Endpoint resolution (interrupted) = {res:.1f} ± {se:.1f}nm",
                size="16px",
            )
        else:
            self.frc_plot.setTitle(
                f"Endpoint resolution = {res:.1f} ± {se:.1f}nm", size="16px"
            )

    def clear_plot(self):
        """Clear the plot."""

        if self.frc_plot is None:
            raise Exception("The PlotWidget object ois not ready!")

        for item in self.frc_plot.allChildItems():
            self.frc_plot.removeItem(item)

    def update_ui_on_process_start(self):
        """Disable elements and inform that a processing is ongoing."""

        # Disable all parameter widgets
        self.ui.lbLateralResolution.setEnabled(False)
        self.ui.leLateralResolution.setEnabled(False)
        self.ui.cbEndpoint.setEnabled(False)
        self.ui.lbTemporalResolution.setEnabled(False)
        self.ui.leTemporalResolution.setEnabled(False)
        self.ui.lbNumRepeats.setEnabled(False)
        self.ui.leNumRepeats.setEnabled(False)
        self.ui.pbRunFRCAnalysis.setEnabled(False)

        # If needed, we make the progress bar visible
        if not self.state.frc_endpoint_only:
            self.ui.progress_bar.setValue(0)
            self.ui.progress_bar.setVisible(True)
            self.ui.pbInterrupt.setVisible(True)

    def update_ui_on_process_end(self):
        """Disable elements and inform that a processing is ongoing."""

        # Enable all parameter widgets
        self.ui.lbLateralResolution.setEnabled(True)
        self.ui.leLateralResolution.setEnabled(True)
        self.ui.cbEndpoint.setEnabled(True)
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

        if self.processor_thread is None:
            return

        # Collect the results
        t_steps = self.processor_thread.t_steps
        all_resolutions = self.processor_thread.all_resolutions

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
