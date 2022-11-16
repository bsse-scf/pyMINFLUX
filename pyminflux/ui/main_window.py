import os
import sys
from pathlib import Path

import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox

from threads import TrackerThread
from ui.Point import Point
from ui.dataviewer import DataViewer
from ui.emittingstream import EmittingStream
from ui.plotter import Plotter

from ui.ui_main_window_new import Ui_MainWindow

from pyminflux import __version__
from pyminflux.reader import MinFluxReader


class pyMinFluxMainWindow(QMainWindow, Ui_MainWindow):
    """
    Main application window.
    """

    # Add a signal for changing current image index
    signal_image_index_changed = Signal(int, name='signal_image_index_changed')

    # Add a signal for marking dataframe of given index as modified
    signal_mark_dataframe_as_modified = Signal(int, bool, name='signal_mark_dataframe_as_modified')

    def __init__(self, parent=None):
        """
        Constructor.
        """

        # Call the base constructor
        super().__init__(parent)

        # Initialize the dialog
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.plotter = None
        self.current_image_index = 0
        self.tracker_thread = None
        self.tracker_is_running = False
        self.last_selected_path = ''
        self.data_viewer = None
        self.line_handle_positions = []
        self.line_handle_translations = []
        self.line_handle_filtered_positions = []
        self.line_handle_filtered_translations = []
        self.text_handle_cell_indices = []
        self.text_handle_track_indices = []
        self.pickEvent = False

        # super(TracerMainWindow, self).__init__()
        # self.setupUi(self)
        self.setWindowTitle(f"pyMinFlux v{__version__}")
        self.setup_data_viewer()
        self.setup_data_plotter()
        self.setup_conn()

        # Keep a reference to the MinFluxReader
        self.minfluxreader = None

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.signal_textWritten.connect(self.print_to_console)

        # Read the application settings
        app_settings = QSettings('ch.ethz.bsse.scf', 'pyminflux')
        self.last_selected_path = app_settings.value("io/last_selected_path", ".")

        # Initialize tracker
        self.tracker = None

        # Initialize the tracker thread
        self.tracker_thread = TrackerThread(self.tracker)
        self.tracker_thread.started.connect(self.tracker_started)
        self.tracker_thread.finished.connect(self.tracker_finished)

    def __del__(self):
        """
        Destructor.
        """
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stdout.flush()

    def full_update_ui(self):
        """
        Updates the UI completely (after a project load, for instance).
        :return: 
        """
        #self.plotter.clear()
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
        """
        Application close event
        :param event: a QCloseEvent
        :return:
        """

        button = QMessageBox.question(self, "Lineage Tracer",
                                      "Are you sure you want to quit?",
                                      QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)

        if button != QMessageBox.StandardButton.Yes:
            event.ignore()
        else:
            # @todo Do this in a safer way!
            if self.tracker_is_running:
                self.tracker_thread.terminate()
                self.tracker_thread.wait()

            # Store the application settings
            if self.last_selected_path != '':
                app_settings = QSettings('ch.ethz.bsse.scf', 'pyminflux')
                app_settings.setValue("io/last_selected_path", str(self.last_selected_path))

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
        self.ui.dataframe_layout.addWidget(self.data_viewer)

        # Show the widget
        self.data_viewer.show()

    def setup_data_plotter(self):
        """
        Setup canvases with respective figures.
        :return: void
        """
        self.plotter = Plotter()

        # Add to the UI
        self.ui.plotting_layout.addWidget(self.plotter)

        # Show the widget
        self.data_viewer.show()

    def setup_conn(self):
        """
        Set up signals and slots
        :return: void
        """
        self.ui.pbLoadNumpyDataFile.clicked.connect(self.select_and_open_numpy_file)

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
            "NumPy binary file (*.npy);;All files (*.*)"
        )
        filename = res[0]
        if filename != "":
            self.last_selected_path = Path(filename).parent

            # Open the file
            self.minfluxreader = MinFluxReader(filename)

            # Show some info
            print(self.minfluxreader)

            # Show the filename on the button
            self.ui.pbLoadNumpyDataFile.setText(filename)

            # Update the ui
            self.full_update_ui()

    def run_tracker(self):
        """
        Run the tracker.
        :return: void
        """
        if len(self.tracker.file_list) == 0:
            print("Select files to be processed.")
            return

        if self.tracker.result_folder == '':
            print("Select project folder.")
            return

        # Launch the actual process in a separate thread
        if self.tracker_is_running:
            print("Cannot currently run the tracker because another"
                  " process is running.")
        else:
            self.tracker_thread.start()

    def tracker_started(self):
        """
        Callback for starting the tracker thread.
        :return: void
        """
        self.tracker_is_running = True
        self.disable_buttons()

    def tracker_finished(self):
        """
        Callback for starting the tracker thread.
        :return: void
        """
        self.tracker_is_running = False
        self.tracker.results_up_to_date = True
        self.enable_buttons()
        self.full_update_ui()

    def disable_buttons(self):
        """
        Disable all buttons
        :return: void
        """
        self.ui.pbLoadNumpyDataFile.setEnabled(False)

    def enable_buttons(self):
        """
        Enable all buttons.
        :return: void
        """
        self.ui.pbLoadNumpyDataFile.setEnabled(True)

    def plot_localizations(self):
        """Plot the localizations."""

        if self.minfluxreader is None:
            self.plotter.redraw()
            return

        # Remove the previous plots
        # TODO: Make this a bit cleverer
        self.plotter.remove_points()

        # Plot the positions
        if self.minfluxreader.is_3d:
            self.plotter.plot_localizations(
                x=self.minfluxreader.processed_dataframe["x"],
                y=self.minfluxreader.processed_dataframe["y"],
                z=self.minfluxreader.processed_dataframe["z"]
            )
        else:
            self.plotter.plot_localizations(
                x=self.minfluxreader.processed_dataframe["x"],
                y=self.minfluxreader.processed_dataframe["y"]
            )


    def save_plots(self):
        """
        Save all plots to disk.

        :return: void
        """
        if self.tracker.result_folder == '':
            return

        if len(self.tracker.image_file_list) == 0:
            return

        # Load the results if needed
        if self.tracker.num_data_frames() == 0:
            return

        # Is there a result folder already?
        if self.tracker.result_folder == '':
            return

        plot_folder = os.path.join(self.tracker.result_folder, "plots")
        if not os.path.isdir(plot_folder):
            os.mkdir(plot_folder)

        # Disable buttons
        self.disable_buttons()

        # Create all plots
        for i in range(len(self.tracker.image_file_list)):
            # Plot image and results for current index
            self.current_image_index = i
            self.plot_localizations()

            # Save to disk
            plot_file_name = os.path.join(plot_folder, "plot%05d.tif" % (i + 1))
            self.ui.canvas.figure.savefig(plot_file_name,
                                       dpi=150,
                                       bbox_inches='tight')

            # Inform
            print("Saved plot %s." % plot_file_name)

            # Force redraw
            QApplication.processEvents()

        # Enable buttons
        self.enable_buttons()

        print("Done.")

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

    @Slot(name="delete_selection")
    def delete_selection(self):
        # DataViewer and Scene are in sync. So we collect the objects to be
        # deleted from the Scene.
        selected_items = self.plotter.selectedItems()
        if len(selected_items) == 0:
            # Nothing selected
            return

        if self.tracker_is_running:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Sorry, you cannot modify the data"
                        " while the tracker is running!")
            msg.setWindowTitle("Info")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        reply = QMessageBox.question(self, 'Question',
                                     "Delete selected cell(s)?",
                                     QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:

            for item in selected_items:

                if isinstance(item, Point):

                    # Get the item (cell) index
                    index = int(item.cell_index)

                    # Remove the object from the data frame
                    df = self.tracker.load_dataframe_for_index(
                        self.current_image_index)
                    self.tracker.store_dataframe_for_index(
                        self.current_image_index,
                        df[(df['cell.index'] != index)])

            # Announce that the data frame was modified
            self.signal_mark_dataframe_as_modified.emit(
                self.current_image_index, False)

            # Mark the results as invalid
            self.tracker.results_up_to_date = False

            # Update the plots
            self.update_plots()

            # Update the data viewer
            self.show_processed_dataframe()

        else:
            return

    @Slot(float, float, name="handle_add_cell_at_position")
    def handle_add_cell_at_position(self, x, y):

        if self.tracker.num_data_frames() == 0:
            return

        if self.tracker_is_running:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Sorry, you cannot modify the data while"
                        " the tracker is running!")
            msg.setWindowTitle("Info")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        # Get the data frame
        df = self.tracker.load_dataframe_for_index(self.current_image_index)

        # Set the cell index for the new cell
        cell_index = np.max(df['cell.index'].values) + 1
        if np.isnan(cell_index):
            cell_index = 1  # Lowest index is 1

        # @TODO: Make this configurable/editable

        # Copy the first row
        s = df.xs(df.index[0])

        # Override some values
        s['cell.index'] = cell_index
        s['cell.center.x'] = round(x)
        s['cell.center.y'] = round(y)
        s['track.index'] = -1
        s['dif.x'] = 0
        s['dif.y'] = 0
        s['filtered.dif.x'] = 0
        s['filtered.dif.y'] = 0
        s['cost'] = np.nan
        s['cost1'] = np.nan
        s['cost2'] = np.nan
        s['cost3'] = np.nan
        s['cost4'] = np.nan
        if 'qc_fingerprint' in s:
            s['qc_fingerprint'] = 0
            s['qc_dist'] = 0.0
            s['qc_validated'] = False
            s['qc_track_index'] = -1
            s['qc_age'] = 0

        # Update the cell.index
        s['cell.index'] = cell_index

        # Append the new row at the end (preserving the index)
        s.name = np.max(df.index.values) + 1
        df = df.append(s, ignore_index=False)

        # Store the updated dataframe
        self.tracker.store_dataframe_for_index(self.current_image_index,
                                               df)

        # Mark the results as invalid
        self.tracker.results_up_to_date = False

        # Announce that the data frame was modified
        self.signal_mark_dataframe_as_modified.emit(
            self.current_image_index, False)

        # Update the plots
        self.update_plots()

        # Update the data viewer
        self.show_processed_dataframe()
