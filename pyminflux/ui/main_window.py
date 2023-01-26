import sys
from pathlib import Path

from PySide6 import QtGui
from PySide6.QtCore import QSettings, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from pyminflux import __version__
from pyminflux.processor import MinFluxProcessor
from pyminflux.reader import MinFluxReader

__APP_NAME__ = "pyMinFlux"

import pyminflux.resources
from pyminflux.state import State
from pyminflux.ui.analyzer import Analyzer
from pyminflux.ui.dataviewer import DataViewer
from pyminflux.ui.emittingstream import EmittingStream
from pyminflux.ui.options import Options
from pyminflux.ui.plotter import Plotter
from pyminflux.ui.plotter_3d import Plotter3D
from pyminflux.ui.ui_main_window import Ui_MainWindow


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

        # Read the application settings and update the state
        app_settings = QSettings("ch.ethz.bsse.scf", "pyminflux")
        self.last_selected_path = app_settings.value("io/last_selected_path", ".")
        self.state.min_num_loc_per_trace = int(
            app_settings.value("options/min_num_loc_per_trace", 1)
        )

        # Dialogs and widgets
        self.data_viewer = None
        self.analyzer = None
        self.plotter = None
        self.plotter3D = None
        self.options = Options()

        # Make sure to only show the console if requested
        self.toggle_dock_console_visibility()

        # Initialize menus
        self.initialize_menu_state()

        # Initialize Plotter and DataViewer
        self.plotter = Plotter()
        self.data_viewer = DataViewer()

        # Add them to the splitter
        self.ui.splitter_layout.addWidget(self.plotter)
        self.ui.splitter_layout.addWidget(self.data_viewer)

        # Show them
        self.plotter.show()
        self.data_viewer.show()

        # Set up signals and slots
        self.setup_conn()

        # Keep a reference to the MinFluxProcessor
        self.minfluxprocessor = None

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.signal_textWritten.connect(self.print_to_console)

        # Print a welcome message to the console
        print(f"Welcome to {__APP_NAME__}.")

    def setup_conn(self):
        """Set up signals and slots."""

        # Menu actions
        self.ui.actionLoad.triggered.connect(self.select_and_open_numpy_file)
        self.ui.actionOptions.triggered.connect(self.open_options_dialog)
        self.ui.actionQuit.triggered.connect(self.quit_application)
        self.ui.actionConsole.changed.connect(self.toggle_dock_console_visibility)
        self.ui.actionData_viewer.changed.connect(self.toggle_dataviewer_visibility)
        self.ui.action3D_Plotter.triggered.connect(self.open_3d_plotter)
        self.ui.actionAnalyzer.triggered.connect(self.open_analyzer)
        self.ui.actionPlotAverageLocalizations.changed.connect(
            self.toggle_plot_average_localizations
        )
        self.ui.actionState.triggered.connect(self.print_current_state)

        # Other connections
        self.plotter.locations_selected.connect(
            self.show_selected_points_by_indices_in_dataviewer
        )
        self.plotter.locations_selected_by_range.connect(
            self.show_selected_points_by_range_in_dataviewer
        )

    def enable_ui_components_on_loaded_data(self):
        """Enable UI components."""
        self.ui.actionAnalyzer.setEnabled(True)

    def disable_ui_components_on_closed_data(self):
        """Disable UI components."""
        self.ui.actionAnalyzer.setEnabled(False)

    def full_update_ui(self):
        """
        Updates the UI completely (after a project load, for instance).
        :return:
        """
        self.plotter.clear()
        self.plot_localizations()
        self.data_viewer.clear()
        print(
            f"Retrieved {len(self.minfluxprocessor.filtered_dataframe.index)} events."
        )

    def print_to_console(self, text):
        """
        Append text to the QTextEdit.
        """
        cursor = self.ui.txConsole.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.ui.txConsole.setTextCursor(cursor)

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
                self.plotter3D.close()
                self.plotter3D = None

            if self.analyzer is not None:
                self.analyzer.close()
                self.analyzer = None

            if self.options is not None:
                self.options.close()
                self.options = None

            # Store the application settings
            if self.last_selected_path != "":
                app_settings = QSettings("ch.ethz.bsse.scf", "pyminflux")
                app_settings.setValue(
                    "io/last_selected_path", str(self.last_selected_path)
                )

            # Restore sys.stdout
            sys.stdout = sys.__stdout__
            sys.stdout.flush()

            # Now exit
            event.accept()

    @Slot(None, name="quit_application")
    def quit_application(self):
        """Quit the application."""
        self.close()

    @Slot(name="initialize_menu_state")
    def initialize_menu_state(self):
        """Initialize state of menu based on state properties."""
        self.ui.actionPlotAverageLocalizations.setChecked(
            self.state.plot_average_localisations
        )

    @Slot(bool, name="toggle_dock_console_visibility")
    def toggle_dock_console_visibility(self):
        """Toggle the visibility of the console dock widget."""
        if self.ui.actionConsole.isChecked():
            self.ui.dwBottom.show()
        else:
            self.ui.dwBottom.hide()

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

    @Slot(None, name="select_and_open_numpy_file")
    def select_and_open_numpy_file(self):
        """
        Pick NumPy MINFLUX data file to open.
        :return: void
        """

        # Open a file dialog for the user to pick an .npy file
        res = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            str(self.last_selected_path),
            "NumPy binary file (*.npy);;All files (*.*)",
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

            # Show the filename on the main window
            self.setWindowTitle(
                f"{__APP_NAME__} v{__version__} - [{Path(filename).name}]"
            )

            # Close the Analyzer
            if self.analyzer is not None:
                self.analyzer.close()
                self.analyzer = None

            # Close the 3D plotter
            if self.plotter3D is not None:
                self.plotter3D.close()
                self.plotter3D = None

            # Update the ui
            self.full_update_ui()

            # Enable selected ui components
            self.enable_ui_components_on_loaded_data()

    @Slot(None, name="print_current_state")
    def print_current_state(self):
        """Print current contents of the state machine (DEBUG)."""
        state_dict = self.state.asdict()
        for s in state_dict:
            print(f"{s}: {state_dict[s]}")

    @Slot(None, name="self.open_analyzer")
    def open_analyzer(self):
        """Initialize and open the analyzer."""
        if self.analyzer is None:
            self.analyzer = Analyzer(self.minfluxprocessor)
            self.analyzer.data_filters_changed.connect(self.full_update_ui)
            self.analyzer.plot()
        self.analyzer.show()
        self.analyzer.activateWindow()

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
        df = self.minfluxprocessor.select_dataframe_by_indices(
            indices=indices, from_weighed_locs=self.state.plot_average_localisations
        )

        # Update the dataviewer
        self.data_viewer.set_data(df)

        # Inform
        point_str = "event" if len(indices) == 1 else "events"
        print(f"Selected {len(indices)} {point_str}.")

    @Slot(tuple, tuple, name="show_selected_points_by_range_in_dataviewer")
    def show_selected_points_by_range_in_dataviewer(self, x_range, y_range):
        """Filter the data by x and y range and show in the dataframe viewer."""

        # Get the filtered dataframe subset contained in the provided x and y ranges
        df = self.minfluxprocessor.select_dataframe_by_xy_range(
            x_range, y_range, from_weighed_locs=self.state.plot_average_localisations
        )

        # Update the dataviewer
        self.data_viewer.set_data(df)

        # Inform
        point_str = "event" if len(df.index) == 1 else "events"
        print(f"Selected {len(df.index)} {point_str}.")

    def plot_localizations(self):
        """Plot the localizations."""

        # Remove the previous plots
        self.plotter.remove_points()

        # If there is nothing to plot, return here
        if self.minfluxprocessor is None:
            return

        if self.state.plot_average_localisations:
            # Get the (potentially filtered) averaged dataframe
            dataframe = self.minfluxprocessor.weighed_localizations
        else:
            # Get the (potentially filtered) full dataframe
            dataframe = self.minfluxprocessor.filtered_dataframe

        # Always plot the (x, y) coordinates in the 2D plotter
        self.plotter.plot_localizations(
            tid=dataframe["tid"],
            x=dataframe["x"],
            y=dataframe["y"],
        )

        # If the 3D plotter is open, also plot the coordinates in the 3D plotter.
        if self.plotter3D is not None:
            self.plot_localizations_3d(dataframe[["x", "y", "z"]].values)

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
            if (
                self.minfluxprocessor is not None
                and self.minfluxprocessor.num_values > 0
            ):
                if self.state.plot_average_localisations:
                    self.plot_localizations_3d(
                        self.minfluxprocessor.weighed_localizations[
                            ["x", "y", "z"]
                        ].values
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
