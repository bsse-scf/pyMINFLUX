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

__ENABLE_PLUGINS__ = False

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from pyqtgraph import ViewBox
from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import pyminflux.resources
from pyminflux import __APP_NAME__, __version__
from pyminflux.plugin import PluginManager
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader, NativeMetadataReader
from pyminflux.settings import Settings, UpdateSettings
from pyminflux.state import State
from pyminflux.threads import AutoUpdateCheckerWorker
from pyminflux.ui.analyzer import Analyzer
from pyminflux.ui.color_unmixer import ColorUnmixer
from pyminflux.ui.colorbar import ColorBarWidget
from pyminflux.ui.colors import ColorCode, reset_all_colors
from pyminflux.ui.dataviewer import DataViewer
from pyminflux.ui.frc_tool import FRCTool
from pyminflux.ui.histogram_plotter import HistogramPlotter
from pyminflux.ui.importer import Importer
from pyminflux.ui.mediator import Mediator
from pyminflux.ui.options import Options
from pyminflux.ui.plotter import Plotter
from pyminflux.ui.plotter_3d import Plotter3D
from pyminflux.ui.plotter_toolbar import PlotterToolbar
from pyminflux.ui.time_inspector import TimeInspector
from pyminflux.ui.trace_stats_viewer import TraceStatsViewer
from pyminflux.ui.ui_main_window import Ui_MainWindow
from pyminflux.ui.wizard import WizardDialog
from pyminflux.utils import check_for_updates
from pyminflux.writer import MinFluxWriter, PyMinFluxNativeWriter


class PyMinFluxMainWindow(QMainWindow, Ui_MainWindow):
    """
    Main application window.
    """

    main_window_ready = Signal()
    request_sync_external_tools = Signal()

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

        # Keep a reference to the AutoUpdateCheckWorker
        self.update_worker = None

        # Interval in seconds since last check for updates
        self._check_interval_in_seconds = 60 * 60 * 24 * 7

        # Keep a reference to the MinFluxProcessor
        self.processor = None

        # Read the application settings and update the state
        self.load_and_apply_settings()

        # Set the menu state based on the settings
        self.ui.actionConsole.setChecked(self.state.open_console_at_start)

        # Initialize Mediator
        self.mediator = Mediator()
        self.mediator.register_dialog("main_window", self)

        # Dialogs and widgets
        self.data_viewer = None
        self.analyzer = None
        self.plotter = None
        self.plotter3d = None
        self.histogram_plotter = None
        self.color_unmixer = None
        self.time_inspector = None
        self.trace_stats_viewer = None
        self.frc_tool = None
        self.options = Options()
        self.mediator.register_dialog("options", self.options)

        # Initialize widget and its dock
        self.wizard = WizardDialog()
        self.wizard_dock = QDockWidget("", self)
        self.wizard_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.wizard_dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable
        )
        self.wizard_dock.setWidget(self.wizard)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.wizard_dock)
        self.mediator.register_dialog("wizard", self.wizard)

        # Initialize Plotter and DataViewer
        self.plotter = Plotter()
        self.mediator.register_dialog("plotter", self.plotter)
        self.plotter_toolbar = PlotterToolbar()
        self.mediator.register_dialog("plotter_toolbar", self.plotter_toolbar)
        self.data_viewer = DataViewer()
        self.mediator.register_dialog("data_viewer", self.data_viewer)

        # Initialize Plotter3D
        self.plotter3d = Plotter3D()
        self.mediator.register_dialog("plotter3d", self.plotter3d)

        # Initialize the ColorBarWidget
        self.colorbar = ColorBarWidget()

        # Initialize a Plotters QWidget with a layout for Plotter, Plotter3D and PlotterColorBar
        self.plotters_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.plotter)
        left_layout.addWidget(self.plotter3d)
        self.plotters_layout.addLayout(left_layout)
        self.plotters_layout.addWidget(QLabel(""))

        # Create the output console
        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setMinimumHeight(100)
        self.txt_console.setMaximumHeight(500)
        self.txt_console.setLineWrapMode(QTextEdit.NoWrap)
        self.txt_console.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.mediator.register_dialog("txt_console", self.txt_console)

        # Add them to the splitter
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.plotter)
        self.stacked_widget.addWidget(self.plotter3d)
        self.plotters_layout = QHBoxLayout()
        self.plotters_layout.addWidget(self.stacked_widget)
        self.plotters_layout.addWidget(self.colorbar, alignment=Qt.AlignRight)
        self.plotters_widget = QWidget()
        self.plotters_widget.setLayout(self.plotters_layout)
        self.ui.splitter_layout.addWidget(self.plotters_widget)
        self.ui.splitter_layout.addWidget(self.plotter_toolbar)
        self.ui.splitter_layout.addWidget(self.data_viewer)
        self.ui.splitter_layout.addWidget(self.txt_console)
        self.ui.splitter_layout.setStretchFactor(0, 1)
        self.ui.splitter_layout.setStretchFactor(1, 0)
        self.ui.splitter_layout.setStretchFactor(2, 0)
        self.ui.splitter_layout.setStretchFactor(3, 0)

        # Make sure to only show the console and the dataviewer if requested
        self.toggle_dataviewer_visibility()
        self.toggle_console_visibility()

        # Set initial visibility and enabled states
        self.enable_ui_components(False)

        # Set up signals and slots
        self.setup_actions_conn()

        # Print a welcome message to the console
        print(f"Welcome to {__APP_NAME__} v{__version__}.")

        # Check for updates
        self.auto_check_remote_for_updates()

        # Initialize Plotter3D scene and view only when the main window
        # has finished initializing
        self.main_window_ready.connect(self.plotter3d.on_show)

        # Initialize and add plug-ins
        self.plugin_manager = None
        if __ENABLE_PLUGINS__:
            self.init_plugins()

    def init_plugins(self):
        """Scans the plugins folder and adds the plug-ins to the Plugins menu."""
        self.plugin_manager = PluginManager(
            Path(__file__).parent.parent.parent / "plugins"
        )
        self.plugin_manager.load_plugins()
        self.ui.menuPlugins.clear()
        for index, info in enumerate(self.plugin_manager.get_plugin_info()):
            action = QAction(f"{info['name']} ({info['version']})", self)
            action.setStatusTip(info["description"])
            action.triggered.connect(lambda checked, i=index: self.execute_plugin(i))
            self.ui.menuPlugins.addAction(action)

    def execute_plugin(self, index):
        result = self.plugin_manager.execute_plugin(index, self.processor)
        print(f"Plugin result: {result}")

    def showEvent(self, event):
        super().showEvent(event)
        self.main_window_ready.emit()

    def load_and_apply_settings(self):
        """Read the application settings and update the State."""

        # Open settings file
        settings = Settings()

        # Read and set "last_selected_path" option
        self.state.last_selected_path = Path(
            settings.instance.value("io/last_selected_path", ".")
        )

        # Read and set 'min_trace_length' option
        self.state.min_trace_length = int(
            settings.instance.value(
                "options/min_trace_length", self.state.min_trace_length
            )
        )

        # Current option name: "options/min_trace_length"
        if settings.instance.contains("options/min_trace_length"):
            self.state.min_trace_length = int(
                settings.instance.value(
                    "options/min_trace_length", self.state.min_trace_length
                )
            )

        # Read and set 'z_scaling_factor' option
        self.state.z_scaling_factor = float(
            settings.instance.value(
                "options/z_scaling_factor", self.state.z_scaling_factor
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

        # Read and set 'plot_export_dpi' option
        self.state.plot_export_dpi = int(
            settings.instance.value(
                "options/plot_export_dpi", self.state.plot_export_dpi
            )
        )

        # Read and set 'open_console_at_start' option
        value = settings.instance.value(
            "options/open_console_at_start",
            self.state.open_console_at_start,
        )
        open_console_at_start = (
            value.lower() == "true" if isinstance(value, str) else bool(value)
        )
        self.state.open_console_at_start = open_console_at_start

    def setup_actions_conn(self):
        """Set up signals and slots."""

        # Menu actions
        self.ui.actionLoad.triggered.connect(self.select_and_load_or_import_data_file)
        self.ui.actionSave.triggered.connect(self.save_native_file)
        self.ui.actionExport_data.triggered.connect(self.export_filtered_data)
        self.ui.actionExport_stats.triggered.connect(self.export_filtered_stats)
        self.ui.actionOptions.triggered.connect(self.open_options_dialog)
        self.ui.actionQuit.triggered.connect(self.quit_application)
        self.ui.actionConsole.changed.connect(self.toggle_console_visibility)
        self.ui.actionData_viewer.changed.connect(self.toggle_dataviewer_visibility)
        self.ui.actionState.triggered.connect(self.print_current_state)
        self.ui.actionHistogram_Plotter.triggered.connect(self.open_histogram_plotter)
        self.ui.actionUnmixer.triggered.connect(self.open_color_unmixer)
        self.ui.actionTime_Inspector.triggered.connect(self.open_time_inspector)
        self.ui.actionAnalyzer.triggered.connect(self.open_analyzer)
        self.ui.actionTrace_Stats_Viewer.triggered.connect(self.open_trace_stats_viewer)
        self.ui.actionFRC_analyzer.triggered.connect(self.open_frc_tool)
        self.ui.actionManual.triggered.connect(
            lambda _: QDesktopServices.openUrl(
                "https://github.com/bsse-scf/pyMINFLUX/wiki/pyMINFLUX-user-manual"
            )
        )
        self.ui.actionWebsite.triggered.connect(
            lambda _: QDesktopServices.openUrl("https://pyminflux.ethz.ch")
        )
        self.ui.actionCode_repository.triggered.connect(
            lambda _: QDesktopServices.openUrl("https://github.com/bsse-scf/pyMINFLUX")
        )
        self.ui.actionIssues.triggered.connect(
            lambda _: QDesktopServices.openUrl(
                "https://github.com/bsse-scf/pyMINFLUX/issues"
            )
        )
        self.ui.actionMailing_list.triggered.connect(
            lambda _: QDesktopServices.openUrl(
                "https://sympa.ethz.ch/sympa/subscribe/pyminflux"
            )
        )
        self.ui.actionWhat_s_new.triggered.connect(
            lambda _: QDesktopServices.openUrl(
                "https://github.com/bsse-scf/pyMINFLUX/blob/master/CHANGELOG.md"
            )
        )
        self.ui.actionCheck_for_updates.triggered.connect(self.check_remote_for_updates)
        self.ui.actionAbout.triggered.connect(self.about)

    def enable_ui_components(self, enabled: bool):
        """Enable/disable UI components."""

        if self.plotter is None:
            raise Exception("Plotter object not ready!")

        if self.plotter3d is None:
            raise Exception("Plotter3D object not ready!")

        if self.data_viewer is None:
            raise Exception("DataViewer object not ready!")

        # Always show one of the plotters
        self.toggle_plotter()

        if enabled:
            self.plotter_toolbar.show()
        else:
            self.plotter_toolbar.hide()
        self.ui.actionSave.setEnabled(enabled)
        self.ui.actionExport_data.setEnabled(enabled)
        self.ui.actionExport_stats.setEnabled(enabled)
        self.ui.actionHistogram_Plotter.setEnabled(enabled)
        self.ui.actionUnmixer.setEnabled(enabled)
        self.ui.actionTime_Inspector.setEnabled(enabled)
        self.ui.actionAnalyzer.setEnabled(enabled)
        self.ui.actionTrace_Stats_Viewer.setEnabled(enabled)
        self.ui.actionFRC_analyzer.setEnabled(enabled)

    def full_update_ui(self):
        """
        Updates the UI completely (after a project load, for instance).
        :return:
        """

        if self.plotter is None:
            raise Exception("Plotter object not ready!")

        if self.plotter3d is None:
            raise Exception("Plotter3D object not ready!")

        if self.data_viewer is None:
            raise Exception("DataViewer object not ready!")

        self.plotter.clear()
        self.plotter3d.clear()
        self.plot_selected_parameters()
        self.data_viewer.clear()
        if self.processor is not None and self.processor.filtered_dataframe is not None:
            print(f"Retrieved {len(self.processor.filtered_dataframe.index)} events.")

    def print_to_console(self, text):
        """
        Append text to the QTextEdit.
        """
        cursor = self.txt_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.txt_console.setTextCursor(cursor)

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

            if self.options is not None:
                self.mediator.unregister_dialog("options")
                self.options.close()
                self.options = None

            if self.histogram_plotter is not None:
                self.mediator.unregister_dialog("histogram_plotter")
                self.histogram_plotter.close()
                self.histogram_plotter = None

            if self.analyzer is not None:
                self.mediator.unregister_dialog("analyzer")
                self.analyzer.close()
                self.analyzer = None

            if self.color_unmixer is not None:
                self.mediator.unregister_dialog("color_unmixer")
                self.color_unmixer.close()
                self.color_unmixer = None

            if self.time_inspector is not None:
                self.mediator.unregister_dialog("time_inspector")
                self.time_inspector.close()
                self.time_inspector = None

            if self.options is not None:
                self.mediator.unregister_dialog("options")
                self.options.close()
                self.options = None

            if self.trace_stats_viewer is not None:
                self.mediator.unregister_dialog("trace_stats_viewer")
                self.trace_stats_viewer.close()
                self.trace_stats_viewer = None

            if self.frc_tool is not None:
                self.mediator.unregister_dialog("frc_tool")
                self.frc_tool.close()
                self.frc_tool = None

            # Store the application settings
            if self.state.last_selected_path is not None:
                settings = Settings()
                settings.instance.setValue(
                    "io/last_selected_path", str(self.state.last_selected_path)
                )

            # Unregister the text console and the Main Window
            self.mediator.unregister_dialog("txt_console")
            self.mediator.unregister_dialog("main_window")

            # Now exit
            event.accept()

    @Slot()
    def toggle_plotter(self):
        """Enable the requested plotter."""
        if self.state.plot_3d:
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.stacked_widget.setCurrentIndex(0)

    @Slot()
    def reset_filters_and_broadcast(self):
        """Reset all filters and broadcast changes."""

        if self.processor is None:
            return

        # Reset filters and data
        self.processor.reset()
        self.state.efo_thresholds = None
        self.state.cfr_thresholds = None

        # Update main window
        self.full_update_ui()

        # Signal that the external viewers and tools should be updated
        self.request_sync_external_tools.emit()

    @Slot()
    def quit_application(self):
        """Quit the application."""
        self.close()

    @Slot(bool)
    def toggle_console_visibility(self):
        """Toggle the visibility of the console widget."""
        if self.ui.actionConsole.isChecked():
            self.txt_console.show()
        else:
            self.txt_console.hide()

    @Slot(bool)
    def toggle_dataviewer_visibility(self):
        """Toggle the visibility of the console dock widget."""
        if self.data_viewer is not None:
            if self.ui.actionData_viewer.isChecked():
                self.data_viewer.show()
            else:
                self.data_viewer.hide()

    @Slot()
    def save_native_file(self):
        """Save data to native pyMINFLUX `.pmx` file."""
        if (
            self.processor is None
            or self.processor.filtered_dataframe is None
            or len(self.processor.filtered_dataframe.index) == 0
        ):
            return

        # Get current filename to build the suggestion output
        if self.processor.filename is None:
            # Just use the path
            out_filename = str(self.state.last_selected_path)
        else:
            out_filename = str(
                self.processor.filename.parent / f"{self.processor.filename.stem}.pmx"
            )

        # Ask the user to pick a name (and format)
        filename, ext = QFileDialog.getSaveFileName(
            self,
            "Save pyMINFLUX dataset",
            out_filename,
            "pyMINFLUX files (*.pmx)",
        )

        # Did the user cancel?
        if filename == "":
            return

        # Does the file name have the .pmx extension?
        if not filename.lower().endswith(".pmx"):
            filename = Path(filename)
            filename = filename.parent / f"{filename.stem}.pmx"

        # Write to disk
        writer = PyMinFluxNativeWriter(self.processor)
        result = writer.write(filename)

        # Save
        if result:
            print(f"Successfully saved {filename}.")
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not save file {Path(filename).name}!\n\nThe error was:\n{writer.message}",
            )

    @Slot()
    def select_and_load_or_import_data_file(self, filename: Optional[str] = None):
        """
        Pick a MINFLUX `.pmx` file to load, or an Imspector `.npy' or '.mat' file to import.
        :return: void
        """

        # Do we have a filename?
        if filename is None or not filename:
            # Open a file dialog for the user to pick a .pmx, .npy or .mat file
            if self.state.last_selected_path is not None:
                save_path = str(self.state.last_selected_path)
            else:
                save_path = str(Path(".").absolute())

            res = QFileDialog.getOpenFileName(
                self,
                "Load file",
                save_path,
                "All Supported Files (*.pmx *.npy *.mat);;"
                "pyMINFLUX file (*.pmx);;"
                "Imspector NumPy files (*.npy);;"
                "Imspector MATLAB mat files (*.mat)",
            )
            filename = res[0]

        # Make sure that we are working with a string
        filename = str(filename)

        if filename != "" and Path(filename).is_file():

            # Pick the right reader
            if len(filename) < 5:
                print(f"Invalid file {filename}: skipping.")
                return
            ext = filename.lower()[-4:]

            # Make sure we have a supported file
            if ext not in [".pmx", ".npy", ".mat"]:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Unsupported file {filename}.",
                )
                return

            # Reload the default settings
            self.load_and_apply_settings()

            # Inform
            print("Reloaded default settings.")

            # If we have a `.pmx` file, we first scan the metadata and update
            # the State
            if ext == ".pmx":
                metadata = NativeMetadataReader.scan(filename)
                if metadata is None:
                    # Could not read the metadata. Abort loading.
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Could not load {filename}.",
                    )
                    return

                # Update the State from the read metadata
                self.state.update_from_metadata(metadata)

                # Inform
                print(f"Loaded settings from {Path(filename).name}.")

            # Now pass the filename to the MinFluxReader
            try:
                reader = MinFluxReader(
                    filename, z_scaling_factor=self.state.z_scaling_factor
                )
            except IOError as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"{e}",
                )
                return

            # Open the Importer
            importer = Importer(
                valid_cfr=reader.valid_cfr,
                relocalizations=reader.relocalizations,
                dwell_time=self.state.dwell_time,
                is_tracking=self.state.is_tracking,
                pool_dcr=self.state.pool_dcr,
            )
            if importer.exec_() != QDialog.Accepted:
                # The user cancelled the dialog
                print("Loading cancelled.")
                return

            # Retrieve the selected options from the Importer
            selection = importer.get_selection()

            # Update the reader object (we let the MinFluxProcessor
            # trigger the creation of the dataframe, hence the
            # process=False argument everywhere).
            reader.set_tracking(selection["is_tracking"], process=False)
            reader.set_indices(
                selection["iteration"], selection["cfr_iteration"], process=False
            )
            reader.set_dwell_time(selection["dwell_time"], process=False)
            reader.set_pool_dcr(selection["pool_dcr"], process=False)

            # Update the state as well
            self.state.is_tracking = selection["is_tracking"]
            self.state.dwell_time = selection["dwell_time"]
            if self.state.is_tracking:
                self.state.plot_average_localisations = False
            self.state.pool_dcr = selection["pool_dcr"]

            # Show some info
            print(reader)

            # Process the file
            self.state.last_selected_path = Path(filename).parent

            # Add initialize the processor with the reader
            self.processor = MinFluxProcessor(reader, self.state.min_trace_length)

            # Make sure to set current value of use_weighted_localizations
            self.processor.use_weighted_localizations = (
                self.state.weigh_avg_localization_by_eco
            )

            # Show the filename on the main window
            self.setWindowTitle(
                f"{__APP_NAME__} v{__version__} - [{Path(filename).name}]"
            )

            # Reset the color caches
            reset_all_colors()

            # Reset the plotter
            if self.plotter is None:
                raise Exception("Plotter object not ready!")
            self.plotter.reset()

            # Reset the plotter3D
            if self.plotter3d is None:
                raise Exception("Plotter3D object not ready!")
            self.plotter3d.reset()

            # Inject the Processor
            self.plotter3d.set_processor(processor=self.processor)

            # Reset the plotter toolbar
            if self.plotter_toolbar is None:
                raise Exception("Plotter Toolbar object not ready!")
            self.plotter_toolbar.reset()

            # Close the Options
            if self.options is not None:
                self.mediator.unregister_dialog("options")
                self.options.close()
                self.options = None

            # Close the Histogram Plotter
            if self.histogram_plotter is not None:
                self.mediator.unregister_dialog("histogram_plotter")
                self.histogram_plotter.close()
                self.histogram_plotter = None

            # Close the Color Unmixer
            if self.color_unmixer is not None:
                self.mediator.unregister_dialog("color_unmixer")
                self.color_unmixer.close()
                self.color_unmixer = None

            # Close the Temporal Inspector
            if self.time_inspector is not None:
                self.mediator.unregister_dialog("time_inspector")
                self.time_inspector.close()
                self.time_inspector = None

            # Close the Trace Stats Viewer
            if self.trace_stats_viewer is not None:
                self.mediator.unregister_dialog("trace_stats_viewer")
                self.trace_stats_viewer.close()
                self.trace_stats_viewer = None

            # Close the FRC Tool
            if self.frc_tool is not None:
                self.mediator.unregister_dialog("frc_tool")
                self.frc_tool.close()
                self.frc_tool = None

            # Update the ui
            self.full_update_ui()

            # Make sure to autoupdate the axis on load
            self.plotter.enableAutoRange(enable=True)

            # Reset the fluorophore list in the wizard
            self.wizard.set_fluorophore_list(self.processor.num_fluorophores)

            # Enable selected ui components
            self.enable_ui_components(True)

            # If the read sequence is not valid, disable the save button
            if reader.is_last_valid:
                self.ui.actionSave.setEnabled(True)
                self.wizard.enable_save_button(True)
            else:
                self.ui.actionSave.setEnabled(False)
                self.wizard.enable_save_button(False)

            # If the acquisition is a tracking one, disable the FRC tool
            if reader.is_tracking:
                self.ui.actionFRC_analyzer.setEnabled(False)
            else:
                self.ui.actionFRC_analyzer.setEnabled(True)

            # Update the Analyzer
            if self.analyzer is not None:
                self.analyzer.set_processor(self.processor)
                self.analyzer.plot()

            # Attach the processor reference to the wizard
            self.wizard.set_processor(self.processor)

            # Enable wizard
            self.wizard.enable_controls(True)

        else:
            # If nothing is loaded (even from earlier), disable wizard
            if self.processor is None:
                self.wizard.enable_controls(False)

    @Slot()
    def export_filtered_data(self):
        """Export filtered data as CSV file."""
        if (
            self.processor is None
            or self.processor.filtered_dataframe is None
            or len(self.processor.filtered_dataframe.index) == 0
        ):
            return

        # Get current filename to build the suggestion output
        if self.processor.filename is None:
            out_filename = str(f"{Path('.') / self.processor.filename.stem}.csv")
        else:
            out_filename = str(
                self.processor.filename.parent / f"{self.processor.filename.stem}.csv"
            )

        # Ask the user to pick a name (and format)
        filename, ext = QFileDialog.getSaveFileName(
            self,
            "Export filtered data",
            out_filename,
            "Comma-separated value files (*.csv)",
        )

        # Did the user cancel?
        if filename == "":
            return

        if ext == "Comma-separated value files (*.csv)":
            # Does the file name have the .csv extension?
            if not filename.lower().endswith(".csv"):
                filename = Path(filename)
                filename = filename.parent / f"{filename.stem}.csv"

            # Write to disk
            result = MinFluxWriter.write_csv(self.processor, filename)

        else:
            return

        # Save
        if result:
            print(
                f"Successfully exported {len(self.processor.filtered_dataframe.index)} localizations."
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not export filtered data to {Path(filename).name}.",
            )

    @Slot()
    def export_filtered_stats(self):
        """Export filtered, per-trace statistics as CSV file."""
        if (
            self.processor is None
            or self.processor.filtered_dataframe is None
            or len(self.processor.filtered_dataframe.index) == 0
        ):
            # Inform and return
            QMessageBox.information(
                self,
                "Info",
                f"Sorry, nothing to export.",
            )
            return

        # Get current filename to build the suggestion output
        if self.processor.filename is None:
            out_filename = str(f"{Path('.') / self.processor.filename.stem}.csv")
        else:
            out_filename = str(
                self.processor.filename.parent
                / f"{self.processor.filename.stem}_stats.csv"
            )

        # Ask the user to pick a name
        filename, ext = QFileDialog.getSaveFileName(
            self,
            "Export trace statistics",
            out_filename,
            "Comma-separated value files (*.csv)",
        )

        # Did the user cancel?
        if filename == "":
            return

        # Does the file name have the .csv extension?
        if ext != "Comma-separated value files (*.csv)":
            return

        if not filename.lower().endswith(".csv"):
            filename = Path(filename)
            filename = filename.parent / f"{filename.stem}.csv"

        # Collect stats
        stats = self.processor.filtered_dataframe_stats
        if stats is None:
            return

        # Write stats to disk
        try:
            stats.to_csv(filename, index=False)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not export trace statistics to {Path(filename).name}.\n\n{str(e)}.",
            )
            return

        print(f"Successfully exported statistics for {len(stats.index)} traces.")

    @Slot()
    def print_current_state(self):
        """Print current contents of the state machine (DEBUG)."""
        if self.txt_console.isHidden():
            self.txt_console.show()
            self.ui.actionConsole.setChecked(True)
        state_dict = self.state.asdict()
        print("[DEBUG] Internal state:")
        for s in state_dict:
            print(f'  ∟ "{s}": {state_dict[s]}')

    @Slot()
    def about(self):
        """Show simple About dialog."""
        from h5py import __version__ as h5py_version
        from numpy import __version__ as numpy_version
        from pandas import __version__ as pandas_version
        from pyarrow import __version__ as pyarrow_version
        from pyqtgraph import __version__ as pg_version
        from PySide6 import __version__ as pyside6_version
        from scipy import __version__ as scipy_version
        from vispy import __version__ as vispy_version

        QMessageBox.about(
            self,
            "About",
            f"{__APP_NAME__} v{__version__}\n"
            f"\n"
            f"Copyright 2022 - {datetime.now().year}\n"
            f"Single Cell Facility\n"
            f"D-BSSE\n"
            f"ETH Zurich\n"
            f"Switzerland"
            f"\n\n---\n"
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n"
            f"PySide6 {pyside6_version}\n"
            f"PyQtGraph {pg_version}\n"
            f"NumPy {numpy_version}\n"
            f"SciPy {scipy_version}\n"
            f"Pandas {pandas_version}\n"
            f"PyArrow {pyarrow_version}\n"
            f"h5py {h5py_version}\n"
            f"VisPy {vispy_version}\n",
        )

    @Slot()
    def check_remote_for_updates(self):
        """Check for application updates."""

        # Check for updates
        code, version, error = check_for_updates()

        # Process the output
        if code == -1:
            # Something went wrong: report
            html = (
                f"<b>Error! {error}</b><br /><br /><br />Please make sure you are connected to the internet.<br />"
                f"If this error persists, please <a href='https://github.com/bsse-scf/pyMINFLUX/issues/'>report it</a>."
            )

        elif code == 0:
            # No new version
            html = (
                f"<b>Congratulations!</b><br /><br />You are running the latest version ({pyminflux.__version__}) "
                f"of {pyminflux.__APP_NAME__}."
            )

        elif code == 1:
            # Show a dialog with a link to the download page
            html = (
                f"<b>There is a new version ({version}) of {pyminflux.__APP_NAME__}!</b><br /><br />"
                f"You can download it from the <a href='https://github.com/bsse-scf/pyMINFLUX/releases/latest'>release page</a>."
            )

        else:
            raise ValueError("Unexpected code!")

        # Update last check time
        update_settings = UpdateSettings(self._check_interval_in_seconds)
        update_settings.update_last_check_time()

        # Show the dialog
        self.show_update_result_dialog(html)

    def auto_check_remote_for_updates(self):
        """Automatic check for application updates."""

        # Check if it is time to check
        update_settings = UpdateSettings(self._check_interval_in_seconds)
        if not update_settings.is_elapsed():
            return

        # For simplicity, we already update the last check timestamp
        update_settings.update_last_check_time()

        # Create the worker
        self.update_worker = AutoUpdateCheckerWorker()

        # Connect the signals
        self.update_worker.result.connect(self.complete_check_remote_for_updates)

        # Start the worker
        self.update_worker.start()

    def complete_check_remote_for_updates(self, is_update, version):
        """Automatic check for application updates."""

        # Only display the dialog if there is an update
        if not is_update:
            return

        # Show a dialog with a link to the download page
        html = (
            f"<b>There is a new version ({version}) of {pyminflux.__APP_NAME__}!</b><br /><br />"
            f"You can download it from the <a href='https://github.com/bsse-scf/pyMINFLUX/releases/latest'>release page</a>."
        )

        # Show the dialog
        self.show_update_result_dialog(html)

    @Slot()
    def open_analyzer(self):
        """Initialize and open the analyzer."""
        if self.processor is None:
            return
        if self.analyzer is None:
            self.analyzer = Analyzer(self.processor)
            self.mediator.register_dialog("analyzer", self.analyzer)
        self.analyzer.plot()
        self.analyzer.show()
        self.analyzer.activateWindow()

    def show_update_result_dialog(self, html):
        """Display the outcome of the update check in a dialog."""
        # Show the dialog
        dialog = QDialog()
        dialog.setWindowTitle("Check for updates")
        dialog.setMinimumSize(400, 180)
        dialog.setFixedHeight(180)
        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("background-color: transparent;")
        text_browser.setOpenExternalLinks(True)
        text_browser.insertHtml(html)
        layout.addWidget(text_browser)
        button = QPushButton("OK")
        button.clicked.connect(dialog.close)
        layout.addWidget(button)
        dialog.exec_()

    @Slot()
    def open_time_inspector(self):
        """Initialize and open the Time Inspector."""
        if self.time_inspector is None:
            self.time_inspector = TimeInspector(self.processor)
            self.mediator.register_dialog("time_inspector", self.time_inspector)
        self.time_inspector.show()
        self.time_inspector.activateWindow()

    @Slot()
    def open_histogram_plotter(self):
        """Initialize and open the histogram plotter."""
        if self.processor is None:
            return
        if self.histogram_plotter is None:
            self.histogram_plotter = HistogramPlotter(self.processor)
            self.mediator.register_dialog("histogram_plotter", self.histogram_plotter)
        self.histogram_plotter.show()
        self.histogram_plotter.activateWindow()

    @Slot()
    def open_color_unmixer(self):
        """Initialize and open the color unmixer."""
        if self.processor is None:
            return
        if self.color_unmixer is None:
            self.color_unmixer = ColorUnmixer(self.processor)
            self.mediator.register_dialog("color_unmixer", self.color_unmixer)
        self.color_unmixer.show()
        self.color_unmixer.activateWindow()

    @Slot()
    def open_options_dialog(self):
        """Open the options dialog."""
        if self.options is None:
            self.options = Options()
            self.mediator.register_dialog("options", self.options)
        self.options.show()
        self.options.activateWindow()

    @Slot()
    def update_min_trace_length(self):
        if self.processor is not None:
            self.processor.min_trace_length = self.state.min_trace_length

    @Slot()
    def open_trace_stats_viewer(self):
        """Open the trace stats viewer."""
        if self.processor is None:
            return
        if self.trace_stats_viewer is None:
            self.trace_stats_viewer = TraceStatsViewer(self.processor)
            self.mediator.register_dialog("trace_stats_viewer", self.trace_stats_viewer)
        self.trace_stats_viewer.show()
        self.trace_stats_viewer.activateWindow()

    @Slot()
    def open_frc_tool(self):
        """Open the FRC tool."""
        if self.processor is None:
            return
        if self.frc_tool is None:
            self.frc_tool = FRCTool(self.processor)
            self.mediator.register_dialog("frc_tool", self.frc_tool)
        self.frc_tool.show()
        self.frc_tool.activateWindow()

    @Slot(list)
    def show_selected_points_by_indices_in_dataviewer(self, points):
        """Show the data for the selected points in the dataframe viewer."""

        if self.data_viewer is None:
            raise Exception("DataViewer object not ready!")

        if self.processor is None:
            return

        # Extract the Pandas Series index loc of the rows corresponding to the selected points
        indices = []
        for p in points:
            indices.append(p.data())

        # Sort the indices
        indices = sorted(indices)

        # Get the filtered dataframe subset corresponding to selected series ilocs
        df = self.processor.select_by_series_iloc(
            iloc=indices, from_weighted_locs=self.state.plot_average_localisations
        )

        # Update the dataviewer
        self.data_viewer.set_data(df)

        # Inform
        point_str = "event" if len(indices) == 1 else "events"
        print(f"Selected {len(indices)} {point_str}.")

    @Slot(tuple, tuple)
    def show_selected_points_by_range_in_dataviewer(
        self, x_param, y_param, x_range, y_range
    ):
        """Select the data by x and y range and show in the dataframe viewer."""

        if self.data_viewer is None:
            raise Exception("DataViewer object not ready!")

        if self.processor is None:
            return

        # Get the filtered dataframe subset contained in the provided x and y ranges
        df = self.processor.select_by_2d_range(
            x_param,
            y_param,
            x_range,
            y_range,
            from_weighted_locs=self.state.plot_average_localisations,
        )

        # Update the dataviewer
        self.data_viewer.set_data(df)

        # Inform
        if df is not None:
            point_str = "event" if len(df.index) == 1 else "events"
            print(f"Selected {len(df.index)} {point_str}.")
        else:
            print(f"Selected 0 events.")

    @Slot(tuple, tuple)
    def crop_data_by_range(self, x_param, y_param, x_range, y_range):
        """Filter the data by x and y range and show in the dataframe viewer."""

        if self.plotter is None:
            raise Exception("Plotter object not ready!")

        if self.processor is None:
            return

        # Filter the dataframe by the passed x and y ranges
        self.processor.filter_by_2d_range(x_param, y_param, x_range, y_range)

        # Update the Analyzer
        if self.analyzer is not None:
            self.analyzer.plot()

        # Update the Fluorophore Detector?
        if self.color_unmixer is not None:
            # No need to update
            pass

        # Update the Temporal Inspector?
        if self.time_inspector is not None:
            # No need to update
            pass

        # Update the ui
        self.full_update_ui()

        # Make sure to autoupdate the axis (on load only)
        self.plotter.getViewBox().enableAutoRange(axis=ViewBox.XYAxes, enable=True)

        # Signal that the external viewers and tools should be updated
        self.request_sync_external_tools.emit()

    def update_weighted_average_localization_option_and_plot(self):
        """Update the weighted average localization option in the Processor and re-plot."""
        if self.processor is not None:
            self.processor.use_weighted_localizations = (
                self.state.weigh_avg_localization_by_eco
            )
        self.plot_selected_parameters()

    def update_and_show_colorbar_widget_if_needed(
        self,
        colormap: str,
        data_range: Optional[tuple[float, float]] = None,
    ):
        """Update the colorbar widget for the color-coding modes that require it."""

        # Make sure we have a valid colormap
        if colormap not in [None, "jet", "plasma"]:
            raise ValueError(f"Unsupported colormap `{colormap}`.")

        # Make sure we have a valid data range
        if data_range is None:
            data_range = (0.0, 1.0)

        # Only show and update the colorbar for supported parameters and color coding option
        if not (
            self.state.color_code == ColorCode.BY_DEPTH
            or self.state.color_code == ColorCode.BY_TIME
        ):
            self.colorbar.hide()
            return

        # Update the colorbar widget
        label = (
            "Depth [nm]"
            if self.state.color_code == ColorCode.BY_DEPTH
            else "Time [min]"
        )
        self.colorbar.reset(colormap=colormap, data_range=data_range, label=label)
        self.colorbar.show()

    def plot_selected_parameters(self):
        """Plot the localizations."""

        colormap = None

        if self.plotter is None:
            raise Exception("Plotter object not ready!")

        if self.plotter3d is None:
            raise Exception("Plotter3D object not ready!")

        # If there is nothing to plot, return here
        if (
            self.processor is None
            or self.processor.filtered_dataframe is None
            or len(self.processor.filtered_dataframe.index) == 0
        ):
            print("No data to process.")
            return

        if self.state.plot_3d:

            # Extract filtered (and optionally averaged) localizations
            if self.state.plot_average_localisations:
                # Get the (potentially filtered) averaged dataframe
                dataframe = self.processor.weighted_localizations
            else:
                # Get the (potentially filtered) full dataframe
                dataframe = self.processor.filtered_dataframe

            # Do we have data to plot
            if dataframe is None:
                return

            # Extract identifiers
            tid = dataframe["tid"]
            fid = None
            depth = dataframe["z"]
            time = None

            # Extract necessary values for color-coding
            if (
                self.state.color_code == ColorCode.NONE
                or self.state.color_code == ColorCode.BY_TID
            ):
                pass
            elif self.state.color_code == ColorCode.BY_FLUO:
                fid = dataframe["fluo"]
            elif self.state.color_code == ColorCode.BY_DEPTH:
                pass
            elif self.state.color_code == ColorCode.BY_TIME:
                time = dataframe["tim"] / 60.0  # Color-code by time in minutes
            else:
                raise ValueError("Unknown color code")

            # Plot localizations in 3D
            self.plotter3d.plot(dataframe[["x", "y", "z"]], tid, fid, depth, time)

            # Range for colorbar
            if self.state.color_code == ColorCode.BY_DEPTH:

                # Set colormap
                colormap = "jet"

                # Set data range
                data_range_for_colorbar = (dataframe["z"].min(), dataframe["z"].max())

            elif self.state.color_code == ColorCode.BY_TIME:

                # Set colormap
                colormap = "plasma"

                # Set data range
                data_range_for_colorbar = (
                    dataframe["tim"].min()
                    / 60.0,  # Data range for color-coding in minutes
                    dataframe["tim"].max() / 60.0,
                )
            else:
                data_range_for_colorbar = None
        else:

            # Remove the previous plots
            self.plotter.remove_points()

            # If an only if the requested parameters are "x" and "y" (in any order),
            # we consider the State.plot_average_localisations property.
            if (self.state.x_param == "x" and self.state.y_param == "y") or (
                self.state.x_param == "y" and self.state.y_param == "x"
            ):
                if self.state.plot_average_localisations:
                    # Get the (potentially filtered) averaged dataframe
                    dataframe = self.processor.weighted_localizations
                else:
                    # Get the (potentially filtered) full dataframe
                    dataframe = self.processor.filtered_dataframe

            else:
                # Get the (potentially filtered) full dataframe
                dataframe = self.processor.filtered_dataframe

            # Do we have data to plot
            if dataframe is None:
                return

            # Pre-define values
            tid = dataframe["tid"]
            fid = None
            depth = None
            time = None

            # Extract values
            x = dataframe[self.state.x_param]
            y = dataframe[self.state.y_param]
            if (
                self.state.color_code == ColorCode.NONE
                or self.state.color_code == ColorCode.BY_TID
            ):
                pass
            elif self.state.color_code == ColorCode.BY_FLUO:
                fid = dataframe["fluo"]
            elif self.state.color_code == ColorCode.BY_DEPTH:
                depth = dataframe["z"]
            elif self.state.color_code == ColorCode.BY_TIME:
                time = dataframe["tim"] / 60.0  # Color-code by time in minutes
            else:
                raise ValueError("Unknown color code")

            # Always plot the (x, y) coordinates in the 2D plotter
            self.plotter.plot_parameters(
                x=x,
                y=y,
                color_code=self.state.color_code,
                x_param=self.state.x_param,
                y_param=self.state.y_param,
                tid=tid,
                fid=fid,
                depth=depth,
                time=time,
            )

            # Range for colorbar
            if self.state.color_code == ColorCode.BY_DEPTH:

                # Set colormap
                colormap = "jet"

                # Set data range
                data_range_for_colorbar = (dataframe["z"].min(), dataframe["z"].max())

            elif self.state.color_code == ColorCode.BY_TIME:

                # Set colormap
                colormap = "plasma"

                # Set data range for colorbar (in minutes)
                data_range_for_colorbar = (
                    dataframe["tim"].min()
                    / 60.0,  # Data range for color-coding in minutes
                    dataframe["tim"].max() / 60.0,
                )
            else:
                colormap = None
                data_range_for_colorbar = None

        # Bring the active plot forward
        self.toggle_plotter()

        # Update and show the colorbar for the color-coding mode that need it
        self.update_and_show_colorbar_widget_if_needed(
            colormap=colormap, data_range=data_range_for_colorbar
        )

    def show_processed_dataframe(self, dataframe=None):
        """
        Displays the results for current frame in the data viewer.
        """

        if self.data_viewer is None:
            raise Exception("DataViewer object not ready!")

        # Is there data to process?
        if self.processor is None:
            self.data_viewer.clear()
            return

        if dataframe is None:
            # Get the (potentially filtered) dataframe
            dataframe = self.processor.filtered_dataframe

        # Pass the dataframe to the pdDataViewer
        self.data_viewer.set_data(dataframe)

    @Slot(int)
    def update_fluorophore_id_in_processor_and_broadcast(self, index):
        """Update the fluorophore ID in the processor and broadcast the change to all parties."""

        if self.processor is None:
            return

        # Update the processor
        self.processor.current_fluorophore_id = index

        # Update all views
        self.full_update_ui()

        # Update the analyzer as well
        if self.analyzer is not None:
            self.analyzer.plot()

    def reset_fluorophore_ids(self):
        """Reset the fluorophore IDs."""

        if self.processor is None:
            return

        # Reset
        self.processor.reset()

        # Update UI
        self.update_fluorophore_id_in_processor_and_broadcast(0)
