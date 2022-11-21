import os
import sys
from pathlib import Path

import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import QSettings, Signal, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from pyminflux import __version__
from pyminflux.reader import MinFluxReader

__APP_NAME__ = "pyMinFlux"

from pyminflux.state import State
from pyminflux.ui.dataviewer import DataViewer
from pyminflux.ui.emittingstream import EmittingStream
from pyminflux.ui.histogram_viewer import HistogramViewer
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

        # Keep a reference to the state machine
        self.state = State()

        # Dialogs and widgets
        self.data_viewer = None
        self.histogram_viewer = None
        self.plotter = None
        self.plotter3D = None

        # Read the application settings
        app_settings = QSettings("ch.ethz.bsse.scf", "pyminflux")
        self.last_selected_path = app_settings.value("io/last_selected_path", ".")

        # Initialize in-window widgets
        self.setup_data_viewer()
        self.setup_data_plotter()

        # Set up signals and slots
        self.setup_conn()

        # Keep a reference to the MinFluxReader
        self.minfluxreader = None

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.signal_textWritten.connect(self.print_to_console)

        # Print a welcome message to the console
        print(f"Welcome to {__APP_NAME__}.")

    def __del__(self):
        """
        Destructor.
        """
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stdout.flush()

    def setup_conn(self):
        """Set up signals and slots."""

        # Menu actions
        self.ui.actionLoad.triggered.connect(self.select_and_open_numpy_file)
        self.ui.actionQuit.triggered.connect(self.quit_application)
        self.ui.actionConsole.changed.connect(self.toggle_dock_console_visibility)
        self.ui.actionData_viewer.changed.connect(self.toggle_dataviewer_visibility)
        self.ui.action3D_Plotter.changed.connect(self.toggle_3d_plotter_visibility)
        self.ui.actionHistogram_Viewer.triggered.connect(self.open_histogram_viewer)
        self.ui.actionState.triggered.connect(self.print_current_state)

        # Other connections
        self.plotter.locations_selected.connect(self.highlight_selected_locations)

    def enable_ui_components_on_loaded_data(self):
        """Enable UI components."""
        self.ui.actionHistogram_Viewer.setEnabled(True)

    def disable_ui_components_on_closed_data(self):
        """Disable UI components."""
        self.ui.actionHistogram_Viewer.setEnabled(False)

    def full_update_ui(self):
        """
        Updates the UI completely (after a project load, for instance).
        :return:
        """
        self.plotter.clear()
        self.plot_localizations()
        self.show_processed_dataframe()

    def update_plots(self):
        """
        Update the UI after a change.
        :return:
        """
        self.plotter.clear()
        self.plot_localizations()

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

            # Store the application settings
            if self.last_selected_path != "":
                app_settings = QSettings("ch.ethz.bsse.scf", "pyminflux")
                app_settings.setValue(
                    "io/last_selected_path", str(self.last_selected_path)
                )

            # Now exit
            event.accept()

    def setup_data_viewer(self):
        """
        Set up the data viewer.
        """

        # Initialize widget if needed
        if self.data_viewer is None:
            self.data_viewer = DataViewer()

        # Add to the UI
        self.ui.splitter_layout.addWidget(self.data_viewer)

        # Show the widget
        self.data_viewer.show()

    def setup_data_plotter(self):
        """Setup 2D in-window plotter."""

        # 2D plotter
        self.plotter = Plotter()

        # Add to the UI
        self.ui.splitter_layout.addWidget(self.plotter)

        # Show the widget
        self.data_viewer.show()

    @Slot(None, name="quit_application")
    def quit_application(self):
        """Quit the application."""
        self.close()

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
            self.last_selected_path = Path(filename).parent

            # Open the file
            self.minfluxreader = MinFluxReader(filename)

            # Show some info
            print(self.minfluxreader)

            # Show the filename on the main window
            self.setWindowTitle(
                f"{__APP_NAME__} v{__version__} - [{Path(filename).name}]"
            )

            # Update the ui
            self.full_update_ui()

            # Enable selected ui components
            self.enable_ui_components_on_loaded_data()

    @Slot(None, name="print_current_state")
    def print_current_state(self):
        """Print current contents of the state machine (DEBUG)."""
        print(f"{self.state.asdict()}")

    @Slot(None, name="self.open_histogram_viewer")
    def open_histogram_viewer(self):
        """Initialize and open the histogram viewer."""
        if self.histogram_viewer is None:
            self.histogram_viewer = HistogramViewer()
            self.histogram_viewer.plot(self.minfluxreader)
        self.histogram_viewer.show()

    @Slot(list, name="highlight_selected_locations")
    def highlight_selected_locations(self, points):
        """Highlight selected locations in the dataframe viewer and scroll to the first one."""

        # Extract indices of the rows corresponding to the selected points
        indices = []
        for p in points:
            indices.append(p.index())

        # Update the dataviewer
        self.data_viewer.select_and_scroll_to_rows(indices)

    def plot_localizations(self):
        """Plot the localizations."""

        if self.minfluxreader is None:
            self.plotter.remove_points()
            return

        # Remove the previous plots
        self.plotter.remove_points()

        # Always plot the (x, y) coordinates in the 2D plotter
        self.plotter.plot_localizations(
            x=self.minfluxreader.processed_dataframe["x"],
            y=self.minfluxreader.processed_dataframe["y"],
        )

        # If the dataset is 3D, also plot the coordinates in the 3D plotter.
        if self.minfluxreader.is_3d:
            self.plot_localizations_3d()

    def plot_localizations_3d(self):
        """If the acquisition is 3D and the Show Plotter menu is checked, show the 3D plotter."""

        # Only plot if the View 3D Plotter menu is checked
        if not self.ui.action3D_Plotter.isChecked():
            return

        # Create the 3D Plotter if it does not exist yet
        if self.plotter3D is None:
            self.plotter3D = Plotter3D(parent=self)

        self.plotter3D.plot(
            self.minfluxreader.processed_dataframe[["x", "y", "z"]].values
        )

        # Show the plotter
        self.plotter3D.show()

    @Slot(None, name="toggle_3d_plotter_visibility")
    def toggle_3d_plotter_visibility(self):
        """Toggle 3D plotter visibility."""

        # Get state of the visibility from the menu
        visible = self.ui.action3D_Plotter.isChecked()
        if self.plotter3D is None:
            if not visible:
                # Nothing to be done
                return
            else:
                # Create the 3D plotter if needed and make it visible
                self.plot_localizations_3d()
                self.plotter3D.show()
        else:
            if not visible:
                # Hide the plotter
                self.plotter3D.hide()
            else:
                # Show the plotter
                self.plotter3D.show()

    def show_processed_dataframe(self):
        """
        Displays the results for current frame in the data viewer.
        """

        # Is there data to process?
        if self.minfluxreader is None:
            self.data_viewer.clear()
            return

        # @TODO
        # This must be run in a parallel QThread
        df = self.minfluxreader.processed_dataframe

        # Pass the dataframe to the pdDataViewer
        self.data_viewer.set_data(df)

        # Optimize the table view columns
        self.data_viewer.optimize()
