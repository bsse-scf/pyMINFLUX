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

import sys
from datetime import datetime
from pathlib import Path

from pyqtgraph import ViewBox
from PySide6 import QtGui
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTextEdit,
)

import pyminflux.resources
from pyminflux import __APP_NAME__, __version__
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader
from pyminflux.settings import Settings
from pyminflux.state import State
from pyminflux.ui.analyzer import Analyzer
from pyminflux.ui.color_unmixer import ColorUnmixer
from pyminflux.ui.dataviewer import DataViewer
from pyminflux.ui.emittingstream import EmittingStream
from pyminflux.ui.options import Options
from pyminflux.ui.plotter import Plotter
from pyminflux.ui.plotter_3d import Plotter3D
from pyminflux.ui.plotter_toolbar import PlotterToolbar
from pyminflux.ui.time_inspector import TimeInspector
from pyminflux.ui.ui_main_window import Ui_MainWindow
from pyminflux.ui.wizard import WizardDialog
from pyminflux.writer import MinFluxWriter


class PyMinFluxMainWindow(QMainWindow, Ui_MainWindow):
    """
    Main application window.
    """

    def __init__(self, parent=None):
        """
        Constructor.
        """

        # Call the base constructor
        super().__init__(parent)

        # Initialize the dialog
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Main window title
        self.setWindowTitle(f"{__APP_NAME__} v{__version__}")

        # Set the window icon
        icon = QIcon(":/icons/icon.png")
        self.setWindowIcon(icon)

        # Keep a reference to the state machine
        self.state = State()

        # Keep track of the last selected path
        self.last_selected_path = ""

        # Keep a reference to the MinFluxProcessor
        self.minfluxprocessor = None

        # Read the application settings and update the state
        self.read_settings()

        # Dialogs and widgets
        self.data_viewer = None
        self.analyzer = None
        self.plotter = None
        self.plotter3D = None
        self.color_unmixer = None
        self.inspector = None
        self.options = Options()

        # Initialize widget and its dock
        self.wizard = WizardDialog()
        self.wizard_dock = QDockWidget("", self)
        self.wizard_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.wizard_dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        )
        self.wizard_dock.setWidget(self.wizard)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.wizard_dock)

        # Initialize Plotter and DataViewer
        self.plotter = Plotter()
        self.plotter_toolbar = PlotterToolbar()
        self.data_viewer = DataViewer()

        # Create the output console
        self.txConsole = QTextEdit()
        self.txConsole.setReadOnly(True)
        self.txConsole.setMinimumHeight(100)
        self.txConsole.setMaximumHeight(500)
        self.txConsole.setLineWrapMode(QTextEdit.NoWrap)
        self.txConsole.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Add them to the splitter
        self.ui.splitter_layout.addWidget(self.plotter)
        self.ui.splitter_layout.addWidget(self.plotter_toolbar)
        self.ui.splitter_layout.addWidget(self.data_viewer)
        self.ui.splitter_layout.addWidget(self.txConsole)

        # Make sure to only show the console if requested
        self.toggle_console_visibility()

        # Set initial visibility and enabled states
        self.plotter.show()
        self.plotter_toolbar.hide()
        self.data_viewer.show()
        self.ui.actionExport_data.setEnabled(False)

        # Set up signals and slots
        self.setup_conn()

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.signal_textWritten.connect(self.print_to_console)

        # Print a welcome message to the console
        print(f"Welcome to {__APP_NAME__}.")

    def read_settings(self):
        """Read the application settings and update the State."""

        # Open settings file
        settings = Settings()

        # Read and set 'last_selected_path' option
        self.last_selected_path = Path(
            settings.instance.value("io/last_selected_path", ".")
        )

        # Read and set 'min_num_loc_per_trace' option
        self.state.min_num_loc_per_trace = int(
            settings.instance.value(
                "options/min_num_loc_per_trace", self.state.min_num_loc_per_trace
            )
        )

        # Read and set 'efo_bin_size_hz' option
        self.state.efo_bin_size_hz = float(
            settings.instance.value(
                "options/efo_bin_size_hz", self.state.efo_bin_size_hz
            )
        )

        # Read and set 'efo_expected_frequency' option
        self.state.efo_expected_frequency = float(
            settings.instance.value(
                "options/efo_expected_frequency", self.state.efo_expected_frequency
            )
        )

        # Read and set 'weigh_avg_localization_by_eco' option
        value = settings.instance.value(
            "options/weigh_avg_localization_by_eco",
            self.state.weigh_avg_localization_by_eco,
        )
        weigh_avg_localization_by_eco = (
            value.lower() == "true" if isinstance(value, str) else bool(value)
        )
        self.state.weigh_avg_localization_by_eco = weigh_avg_localization_by_eco

        # Read and set the plot ranges
        value = settings.instance.value("options/efo_range", self.state.efo_range)
        if value == "None" or value is None:
            self.state.efo_range = None
        elif type(value) is list:
            self.state.efo_range = (float(value[0]), float(value[1]))
        else:
            raise ValueError("Unexpected value for 'efo_range' in settings.")

        value = settings.instance.value("options/cfr_range", self.state.cfr_range)
        if value == "None" or value is None:
            self.state.cfr_range = None
        elif type(value) is list:
            self.state.cfr_range = (float(value[0]), float(value[1]))
        else:
            raise ValueError("Unexpected value for 'cfr_range' in settings.")

        value = settings.instance.value(
            "options/loc_precision_range", self.state.loc_precision_range
        )
        if value == "None" or value is None:
            self.state.loc_precision_range = None
        elif type(value) is list:
            self.state.loc_precision_range = (float(value[0]), float(value[1]))
        else:
            raise ValueError("Unexpected value for 'loc_precision_range' in settings.")

    def setup_conn(self):
        """Set up signals and slots."""

        # Menu actions
        self.ui.actionLoad.triggered.connect(self.select_and_open_data_file)
        self.ui.actionExport_data.triggered.connect(self.export_filtered_data)
        self.ui.actionOptions.triggered.connect(self.open_options_dialog)
        self.ui.actionQuit.triggered.connect(self.quit_application)
        self.ui.actionConsole.changed.connect(self.toggle_console_visibility)
        self.ui.actionData_viewer.changed.connect(self.toggle_dataviewer_visibility)
        self.ui.action3D_Plotter.triggered.connect(self.open_3d_plotter)
        self.ui.actionState.triggered.connect(self.print_current_state)
        self.ui.actionManual.triggered.connect(
            lambda _: QDesktopServices.openUrl("https://pyminflux.ethz.ch/manual")
        )
        self.ui.actionWebsite.triggered.connect(
            lambda _: QDesktopServices.openUrl("https://pyminflux.ethz.ch")
        )
        self.ui.actionAbout.triggered.connect(self.about)

        # Plotter toolbar
        self.plotter_toolbar.plot_requested_parameters.connect(
            self.plot_selected_parameters
        )
        self.plotter_toolbar.fluorophore_id_changed.connect(
            self.update_fluorophore_id_in_processor_and_broadcast
        )
        self.plotter_toolbar.plot_average_positions_state_changed.connect(
            self.full_update_ui
        )

        # Other connections
        self.plotter.locations_selected.connect(
            self.show_selected_points_by_indices_in_dataviewer
        )
        self.plotter.locations_selected_by_range.connect(
            self.show_selected_points_by_range_in_dataviewer
        )
        self.plotter.crop_region_selected.connect(self.crop_data_by_range)
        self.plotter_toolbar.color_code_locs_changed.connect(
            self.plot_selected_parameters
        )
        self.options.weigh_avg_localization_by_eco_option_changed.connect(
            self.update_weighted_average_localization_option_and_plot
        )

        # Wizard
        self.wizard.load_data_triggered.connect(self.select_and_open_data_file)
        self.wizard.open_unmixer_triggered.connect(self.open_color_unmixer)
        self.wizard.open_time_inspector_triggered.connect(self.open_inspector)
        self.wizard.open_analyzer_triggered.connect(self.open_analyzer)
        self.wizard.fluorophore_id_changed.connect(
            self.update_fluorophore_id_in_processor_and_broadcast
        )
        self.wizard.request_fluorophore_ids_reset.connect(self.reset_fluorophore_ids)
        self.wizard.wizard_filters_run.connect(self.full_update_ui)
        self.wizard.export_data_triggered.connect(self.export_filtered_data)

    def enable_ui_components_on_loaded_data(self):
        """Enable UI components."""
        self.ui.actionExport_data.setEnabled(True)
        self.plotter_toolbar.show()

    def disable_ui_components_on_closed_data(self):
        """Disable UI components."""
        self.ui.actionExport_data.setEnabled(False)
        self.plotter_toolbar.hide()

    def full_update_ui(self):
        """
        Updates the UI completely (after a project load, for instance).
        :return:
        """
        self.plotter.clear()
        self.plot_selected_parameters()
        self.data_viewer.clear()
        if (
            self.minfluxprocessor is not None
            and self.minfluxprocessor.filtered_dataframe is not None
        ):
            print(
                f"Retrieved {len(self.minfluxprocessor.filtered_dataframe.index)} events."
            )

    def print_to_console(self, text):
        """
        Append text to the QTextEdit.
        """
        cursor = self.txConsole.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.txConsole.setTextCursor(cursor)

    def closeEvent(self, event):
        """Application close event."""

        # Ask the user
        button = QMessageBox.question(
            self,
            f"{__APP_NAME__}",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )

        if button != QMessageBox.StandardButton.Yes:
            event.ignore()
        else:
            # @TODO Shutdown threads if any are running

            # Close the external dialogs
            if self.plotter3D is not None:
                self.plotter3D.hide_on_close = False
                self.plotter3D.close()
                self.plotter3D = None

            if self.analyzer is not None:
                self.analyzer.close()
                self.analyzer = None

            if self.color_unmixer is not None:
                self.color_unmixer.close()
                self.color_unmixer = None

            if self.inspector is not None:
                self.inspector.close()
                self.inspector = None

            if self.options is not None:
                self.options.close()
                self.options = None

            # Store the application settings
            if self.last_selected_path != "":
                settings = Settings()
                settings.instance.setValue(
                    "io/last_selected_path", str(self.last_selected_path)
                )

            # # Restore sys.stdout
            # sys.stdout = sys.__stdout__
            # sys.stdout.flush()

            # Now exit
            event.accept()

    @Slot(None, name="quit_application")
    def quit_application(self):
        """Quit the application."""
        self.close()

    @Slot(bool, name="toggle_console_visibility")
    def toggle_console_visibility(self):
        """Toggle the visibility of the console widget."""
        if self.ui.actionConsole.isChecked():
            self.txConsole.show()
        else:
            self.txConsole.hide()

    @Slot(bool, name="toggle_dataviewer_visibility")
    def toggle_dataviewer_visibility(self):
        """Toggle the visibility of the console dock widget."""
        if self.data_viewer is not None:
            if self.ui.actionData_viewer.isChecked():
                self.data_viewer.show()
            else:
                self.data_viewer.hide()

    @Slot(bool, name="toggle_plot_average_localizations")
    def toggle_plot_average_localizations(self):
        """Toggle the state of plot_average_localizations."""
        if self.ui.actionPlotAverageLocalizations.isChecked():
            self.state.plot_average_localisations = True
        else:
            self.state.plot_average_localisations = False

        # Trigger a re-plot
        self.full_update_ui()

    @Slot(bool, name="toggle_plot_average_localizations")
    def toggle_plot_average_localizations(self):
        """Toggle the state of plot_average_localizations."""
        if self.ui.actionPlotAverageLocalizations.isChecked():
            self.state.plot_average_localisations = True
            self.plotter_toolbar.ui.cbPlotAveragePos.setChecked(True)
        else:
            self.state.plot_average_localisations = False
            self.plotter_toolbar.ui.cbPlotAveragePos.setChecked(False)

        # Trigger a re-plot
        self.full_update_ui()

    @Slot(None, name="select_and_open_data_file")
    def select_and_open_data_file(self):
        """
        Pick a MINFLUX data file to open.
        :return: void
        """

        # Open a file dialog for the user to pick an .npy file
        res = QFileDialog.getOpenFileName(
            self,
            "Open MINFLUX data file",
            str(self.last_selected_path),
            "NumPy binary files (*.npy);;MATLAB mat files(*.mat)",
        )
        filename = res[0]
        if filename != "":
            # Reset the state machine
            self.state.reset()

            # Open the file
            self.last_selected_path = Path(filename).parent
            minfluxreader = MinFluxReader(filename)

            # Show some info
            print(minfluxreader)

            # Add initialize the processor with the reader
            self.minfluxprocessor = MinFluxProcessor(minfluxreader)

            # Make sure to set current value of use_weighted_localizations
            self.minfluxprocessor.use_weighted_localizations = (
                self.state.weigh_avg_localization_by_eco
            )

            # Set state properties from data
            self.set_state_from_data()

            # Show the filename on the main window
            self.setWindowTitle(
                f"{__APP_NAME__} v{__version__} - [{Path(filename).name}]"
            )

            # Close the Color Unmixer
            if self.color_unmixer is not None:
                self.color_unmixer.close()
                self.color_unmixer = None

            # Close the Temporal Inspector
            if self.inspector is not None:
                self.inspector.close()
                self.inspector = None

            # Update the ui
            self.full_update_ui()

            # Make sure to autoupdate the axis on load
            self.plotter.enableAutoRange(enable=True)

            # Reset the fluorophore list in the wizard
            self.wizard.set_fluorophore_list(self.minfluxprocessor.num_fluorophorses)

            # Enable selected ui components
            self.enable_ui_components_on_loaded_data()

            # Update the Analyzer
            if self.analyzer is not None:
                self.analyzer.set_processor(self.minfluxprocessor)
                self.analyzer.plot()

            # Attach the processor reference to the wizard
            self.wizard.set_processor(self.minfluxprocessor)

            # Enable wizard
            self.wizard.enable_controls(True)

        else:
            # If nothing is loaded (even from earlier), disable wizard
            if self.minfluxprocessor is None:
                self.wizard.enable_controls(False)

    @Slot(None, name="export_filtered_data")
    def export_filtered_data(self):
        """Export filtered data as CSV file."""
        if (
            self.minfluxprocessor is None
            or len(self.minfluxprocessor.filtered_dataframe.index) == 0
        ):
            return

        # Ask the user to pick a name (and format)
        filename, ext = QFileDialog.getSaveFileName(
            self,
            "Export filtered data",
            str(self.last_selected_path),
            "NumPy binary files (*.npy);;Comma-separated value files (*.csv)",
        )

        # Did the user cancel?
        if filename == "":
            return

        if ext == "NumPy binary files (*.npy)":
            # Does the file name have the .npy extension?
            if not filename.lower().endswith(".npy"):
                filename = Path(filename)
                filename = filename.parent / f"{filename.stem}.npy"

            # Write to disk
            result = MinFluxWriter.write_npy(self.minfluxprocessor, filename)

        elif ext == "Comma-separated value files (*.csv)":
            # Does the file name have the .csv extension?
            if not filename.lower().endswith(".csv"):
                filename = Path(filename)
                filename = filename.parent / f"{filename.stem}.csv"

            # Write to disk
            result = MinFluxWriter.write_csv(self.minfluxprocessor, filename)

        else:
            return

        # Save
        if result:
            print(
                f"Successfully exported {len(self.minfluxprocessor.filtered_dataframe.index)} localizations."
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not export filtered data to {Path(filename).name}.",
            )

    @Slot(None, name="print_current_state")
    def print_current_state(self):
        """Print current contents of the state machine (DEBUG)."""
        if self.txConsole.isHidden():
            self.txConsole.show()
            self.ui.actionConsole.setChecked(True)
        state_dict = self.state.asdict()
        print("[DEBUG] Internal state:")
        for s in state_dict:
            print(f'  ∟ "{s}": {state_dict[s]}')

    @Slot(None, name="about")
    def about(self):
        """Show simple About dialog."""
        QMessageBox.about(
            self,
            "About",
            f"{__APP_NAME__} v{__version__}\n"
            f'"Heidelberg"\n'
            f"\n"
            f"Copyright 2022 - {datetime.now().year}\n"
            f"Single Cell Facility\n"
            f"D-BSSE\n"
            f"ETH Zurich\n"
            f"Switzerland",
        )

    @Slot(None, name="open_analyzer")
    def open_analyzer(self):
        """Initialize and open the analyzer."""
        if self.analyzer is None:
            self.analyzer = Analyzer(self.minfluxprocessor)
            self.wizard.wizard_filters_run.connect(self.analyzer.plot)
            self.wizard.efo_bounds_modified.connect(self.analyzer.change_efo_bounds)
            self.wizard.cfr_bounds_modified.connect(self.analyzer.change_cfr_bounds)
            self.analyzer.data_filters_changed.connect(self.full_update_ui)
            self.analyzer.cfr_threshold_factor_changed.connect(
                self.wizard.change_cfr_threshold_factor
            )
            self.analyzer.efo_bounds_changed.connect(self.wizard.change_efo_bounds)
            self.analyzer.cfr_bounds_changed.connect(self.wizard.change_cfr_bounds)
            if self.inspector is not None:
                self.analyzer.data_filters_changed.connect(self.inspector.update)
            self.analyzer.plot()
        self.analyzer.show()
        self.analyzer.activateWindow()

    @Slot(None, name="open_inspector")
    def open_inspector(self):
        """Initialize and open the temporal inspector."""
        if self.inspector is None:
            self.inspector = TimeInspector(self.minfluxprocessor, parent=self)
            self.inspector.dataset_time_filtered.connect(self.full_update_ui)
            self.plotter_toolbar.fluorophore_id_changed.connect(self.inspector.update)
            self.wizard.wizard_filters_run.connect(self.inspector.update)
            if self.analyzer is not None:
                self.analyzer.data_filters_changed.connect(self.inspector.update)
        self.inspector.show()
        self.inspector.activateWindow()

    @Slot(None, name="open_color_unmixer")
    def open_color_unmixer(self):
        """Initialize and open the color unmixer."""
        if self.color_unmixer is None:
            self.color_unmixer = ColorUnmixer(self.minfluxprocessor, parent=self)
            self.color_unmixer.fluorophore_ids_assigned.connect(
                self.wizard.set_fluorophore_list
            )
            self.color_unmixer.fluorophore_ids_assigned.connect(
                self.plot_selected_parameters
            )
            self.wizard.wizard_filters_run.connect(self.plot_selected_parameters)
        self.color_unmixer.show()
        self.color_unmixer.activateWindow()

    @Slot(None, name="open_options_dialog")
    def open_options_dialog(self):
        """Open the options dialog."""
        if self.options is None:
            self.options = Options()
        self.options.show()
        self.options.activateWindow()

    @Slot(list, name="show_selected_points_by_indices_in_dataviewer")
    def show_selected_points_by_indices_in_dataviewer(self, points):
        """Show the data for the selected points in the dataframe viewer."""

        # Extract indices of the rows corresponding to the selected points
        indices = []
        for p in points:
            indices.append(p.index())

        # Sort the indices
        indices = sorted(indices)

        # Get the filtered dataframe subset corresponding to selected indices
        df = self.minfluxprocessor.select_by_indices(
            indices=indices, from_weighted_locs=self.state.plot_average_localisations
        )

        # Update the dataviewer
        self.data_viewer.set_data(df)

        # Inform
        point_str = "event" if len(indices) == 1 else "events"
        print(f"Selected {len(indices)} {point_str}.")

    @Slot(tuple, tuple, name="show_selected_points_by_range_in_dataviewer")
    def show_selected_points_by_range_in_dataviewer(
        self, x_param, y_param, x_range, y_range
    ):
        """Select the data by x and y range and show in the dataframe viewer."""

        # Get the filtered dataframe subset contained in the provided x and y ranges
        df = self.minfluxprocessor.select_by_2d_range(
            x_param,
            y_param,
            x_range,
            y_range,
            from_weighted_locs=self.state.plot_average_localisations,
        )

        # Update the dataviewer
        self.data_viewer.set_data(df)

        # Inform
        point_str = "event" if len(df.index) == 1 else "events"
        print(f"Selected {len(df.index)} {point_str}.")

    @Slot(tuple, tuple, name="crop_data_by_range")
    def crop_data_by_range(self, x_param, y_param, x_range, y_range):
        """Filter the data by x and y range and show in the dataframe viewer."""

        # Filter the dataframe by the passed x and y ranges
        self.minfluxprocessor.filter_by_2d_range(x_param, y_param, x_range, y_range)

        # Update the Analyzer
        if self.analyzer is not None:
            self.analyzer.plot()

        # Update the Fluorophore Detector?
        if self.color_unmixer is not None:
            # No need to update
            pass

        # Update the Temporal Inspector?
        if self.inspector is not None:
            # No need to update
            pass

        # Update the 3D plotter
        if self.plotter3D is not None and self.plotter.isVisible():
            self.plotter3D.plot(
                self.minfluxprocessor.filtered_dataframe[["x", "y", "z"]].values
            )

        # Update the ui
        self.full_update_ui()

        # Make sure to autoupdate the axis (on load only)
        self.plotter.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=True)

    def set_state_from_data(self):
        """Set state properties that depend on data."""
        if self.minfluxprocessor.filtered_dataframe is not None:
            self.state.gmm_efo_num_clusters = int(
                self.minfluxprocessor.filtered_dataframe["dwell"].max()
            )

    def update_weighted_average_localization_option_and_plot(self):
        """Update the weighted average localization option in the Processor and re-plot."""
        if self.minfluxprocessor is not None:
            self.minfluxprocessor.use_weighted_localizations = (
                self.state.weigh_avg_localization_by_eco
            )
        self.plot_selected_parameters()

    def plot_selected_parameters(self):
        """Plot the localizations."""

        # Remove the previous plots
        self.plotter.remove_points()

        # If there is nothing to plot, return here
        if self.minfluxprocessor is None:
            return

        # If an only if the requested parameters are "x" and "y" (in any order),
        # we consider the State.plot_average_localisations property.
        if (self.state.x_param == "x" and self.state.y_param == "y") or (
            self.state.x_param == "y" and self.state.y_param == "x"
        ):
            if self.state.plot_average_localisations:
                # Get the (potentially filtered) averaged dataframe
                dataframe = self.minfluxprocessor.weighted_localizations
            else:
                # Get the (potentially filtered) full dataframe
                dataframe = self.minfluxprocessor.filtered_dataframe

            # If the 3D plotter is open, also plot the coordinates in the 3D plotter.
            if self.plotter3D is not None and self.plotter3D.isVisible():
                self.plot_localizations_3d(dataframe[["x", "y", "z"]].values)

        else:
            # Get the (potentially filtered) full dataframe
            dataframe = self.minfluxprocessor.filtered_dataframe

        # Extract values
        x = dataframe[self.state.x_param].values
        y = dataframe[self.state.y_param].values
        tid = dataframe["tid"].values
        fid = dataframe["fluo"].values

        # Always plot the (x, y) coordinates in the 2D plotter
        self.plotter.plot_parameters(
            tid=tid,
            fid=fid,
            x=x,
            y=y,
            x_param=self.state.x_param,
            y_param=self.state.y_param,
        )

    def plot_localizations_3d(self, coords=None):
        """If the acquisition is 3D and the Show Plotter menu is checked, show the 3D plotter.

        If coords is None, filters may be applied.
        """

        # Only plot if the View 3D Plotter is open
        if self.plotter3D is None:
            return

        if coords is None:
            dataframe = self.minfluxprocessor.filtered_dataframe
            if dataframe is None:
                return
            coords = dataframe[["x", "y", "z"]].values

        # Plot new data (old data will be dropped)
        self.plotter3D.plot(coords)

        # Show the plotter
        self.plotter3D.show()

    @Slot(None, name="open_3d_plotter")
    def open_3d_plotter(self):
        """Open 3D plotter."""

        """Initialize and open the analyzer."""
        if self.plotter3D is None:
            self.plotter3D = Plotter3D()
            self.plotter3D.hide_on_close = True
        if self.minfluxprocessor is not None and self.minfluxprocessor.num_values > 0:
            if self.state.plot_average_localisations:
                self.plot_localizations_3d(
                    self.minfluxprocessor.weighted_localizations[["x", "y", "z"]].values
                )
            else:
                self.plot_localizations_3d(
                    self.minfluxprocessor.filtered_dataframe[["x", "y", "z"]].values
                )
        self.plotter3D.show()
        self.plotter3D.activateWindow()

    def show_processed_dataframe(self, dataframe=None):
        """
        Displays the results for current frame in the data viewer.
        """

        # Is there data to process?
        if self.minfluxprocessor is None:
            self.data_viewer.clear()
            return

        if dataframe is None:
            # Get the (potentially filtered) dataframe
            dataframe = self.minfluxprocessor.filtered_dataframe()

        # Pass the dataframe to the pdDataViewer
        self.data_viewer.set_data(dataframe)

    @Slot(int, name="update_fluorophore_id_in_processor_and_broadcast")
    def update_fluorophore_id_in_processor_and_broadcast(self, index):
        """Update the fluorophore ID in the processor and broadcast the change to all parties."""

        # Update the processor
        self.minfluxprocessor.current_fluorophore_id = index

        # Update all views
        self.full_update_ui()

        # Update the analyzer as well
        if self.analyzer is not None:
            self.analyzer.plot()

    def reset_fluorophore_ids(self):
        """Reset the fluorophore IDs."""

        # Reset
        self.minfluxprocessor.reset()

        # Update UI
        self.update_fluorophore_id_in_processor_and_broadcast(0)
