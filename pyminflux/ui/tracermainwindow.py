import os
import sys
from pathlib import Path

import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import QSettings, QFile
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QScrollArea
from PySide6.QtUiTools import QUiLoader

#from analysis.tracker import Tracker
from threads import TrackerThread
from ui.Point import Point
from ui.Vector import Vector
from ui.dataviewer import DataViewer
from ui.emittingstream import EmittingStream
from ui.fileviewer import FileViewer
from ui.graphicscene import GraphicScene
from ui.settings import Settings

from ui.ui_main_window import Ui_MainWindow

# # Set up UIs
# Ui_MainWindow, QMainWindow = loadUiType(os.path.join(os.path.dirname(__file__), 'main_window.ui'))


class TracerMainWindow(QMainWindow, Ui_MainWindow):
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

        self.scene = None
        self.current_image_index = 0
        self.input_file_indices_list = []
        self.tracker_thread = None
        self.tracker_is_running = False
        self.last_selected_path = ''
        self.settings_dialog = None
        self.file_viewer = None
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
        self.setWindowTitle('Lineage Tracer')
        self.setup_file_viewer()
        self.setup_data_viewer()
        self.setup_data_plotter()
        self.setup_conn()

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.signal_textWritten.connect(self.print_to_console)

        # Read the application settings
        app_settings = QSettings('BSSE', 'lineage_tracer')
        self.last_selected_path = app_settings.value("io/last_selected_path",
                                                     ".")

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

    @Slot(int, name="handle_changed_image_index")
    def handle_changed_image_index(self, i):
        """
        :param i: new image index.
        """
        if i > len(self.tracker.image_file_list) - 1:
            print("Please load the corresponding image!")
            return

        self.current_image_index = i
        self.show_results_in_data_viewer()
        self.update_plots()

    @Slot(str, name="handle_request_revert_file")
    def handle_request_revert_file(self, file_name):
        """
        :param file_name: name of the file to revert.
        """
        # Reload
        df, index = self.tracker.revert_dataframe_to_file_for_file_name(
            file_name)
        if df is not None:
            print("File successfully reverted.")
            self.signal_mark_dataframe_as_modified.emit(index, True)
        else:
            print("Could not revert file!")

        # Update UI
        self.show_results_in_data_viewer()
        self.update_plots()

    @Slot(int)
    def retrieve_costs_for_track(self, track_index):
        """
        Collect costs for speficied track index.
        :param track_index: track index
        :type track_index: int
        """

        import matplotlib.pyplot as plt

        # X axis
        x = np.arange(1, self.tracker.num_data_frames() + 1)

        # Initialize cost arrays
        cost = np.empty(self.tracker.num_data_frames())
        cost.fill(np.nan)
        cost1 = cost.copy()
        cost2 = cost.copy()
        cost3 = cost.copy()
        cost4 = cost.copy()

        # Process all data frames
        for i in range(self.tracker.num_data_frames()):

            # Get the data frame
            df = self.tracker.load_dataframe_for_index(i)

            # Get the cost for current track index
            try:
                c = df[df['track.index'] == track_index]['cost'].values[0]
                c1 = df[df['track.index'] == track_index]['cost1'].values[0]
                c2 = df[df['track.index'] == track_index]['cost2'].values[0]
                c3 = df[df['track.index'] == track_index]['cost3'].values[0]
                c4 = df[df['track.index'] == track_index]['cost4'].values[0]
            except (KeyError, IndexError):
                c = 0
                c1 = 0
                c2 = 0
                c3 = 0
                c4 = 0

            cost[i] = c
            cost1[i] = c1
            cost2[i] = c2
            cost3[i] = c3
            cost4[i] = c4

        # Open a new figure for this plot
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Plot
        l_c, = ax.plot(x, cost, label='C', linestyle='-', linewidth=1.5)
        l_c1, = ax.plot(x, cost1, label='C1', linestyle='--', linewidth=1)
        l_c2, = ax.plot(x, cost2, label='C2', linestyle='--', linewidth=1)
        l_c3, = ax.plot(x, cost3, label='C3', linestyle='--', linewidth=1)
        l_c4, = ax.plot(x, cost4, label='C4', linestyle='--', linewidth=1)
        plt.legend(handles=[l_c, l_c1, l_c2, l_c3, l_c4])
        plt.title("Cost for track index = %d" % track_index)
        plt.xlabel("Frame number")
        plt.ylabel("Cost")
        plt.show()

    def full_update_ui(self):
        """
        Updates the UI completely (after a project load, for instance).
        :return: 
        """
        self.scene.clear()
        self.show_image()
        self.plot_results()
        self.show_files_in_file_viewer()
        self.show_results_in_data_viewer()

    def update_plots(self):
        """
        Update the UI after a change.
        :return:
        """
        self.scene.clear()
        self.show_image()
        self.plot_results()

    def print_to_console(self, text):
        """
        Append text to the QTextEdit.
        """
        cursor = self.txConsole.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.txConsole.setTextCursor(cursor)

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
                app_settings = QSettings('BSSE', 'lineage_tracer')
                app_settings.setValue("io/last_selected_path",
                                      self.last_selected_path)

            # Now exit
            event.accept()

    def setup_data_plotter(self):
        """
        Setup canvases with respective figures.
        :return: void
        """
        self.scene = GraphicScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.ui.graphicsView.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.ui.graphicsView.setMouseTracking(True)

    def setup_conn(self):
        """
        Set up signals and slots
        :return: void
        """
        self.ui.pbSelectData.clicked.connect(self.select_input_files)
        self.ui.pbSelectImages.clicked.connect(self.select_image_files)
        self.ui.pbSelectProjectFolder.clicked.connect(self.select_project_folder)
        self.ui.pbRunTracker.clicked.connect(self.run_tracker)
        self.ui.pbSaveProject.clicked.connect(self.save_project)
        self.ui.pbExportResults.clicked.connect(self.export_results)
        self.ui.pbSettings.clicked.connect(self.show_settings_dialog)
        self.ui.cbPlotRawVectors.stateChanged.connect(self.plot_results)
        self.ui.cbPlotFiltVectors.stateChanged.connect(self.plot_results)
        self.ui.rbPlotCellIndex.toggled.connect(self.plot_results)
        self.ui.rbPlotTrackIndex.toggled.connect(self.plot_results)
        self.signal_image_index_changed.connect(self.handle_changed_image_index)
        self.file_viewer.signal_request_revert_file.connect(
            self.handle_request_revert_file)
        self.scene.signal_selection_completed.connect(
            self.data_viewer.handle_scene_selection_completed)
        self.data_viewer.signal_selection_completed.connect(
            self.scene.handle_data_viewer_selection_completed)
        self.scene.signal_add_cell_at_position.connect(
            self.handle_add_cell_at_position)
        self.signal_mark_dataframe_as_modified.connect(
            self.file_viewer.mark_as_modified)
        self.data_viewer.signal_retrieve_costs_for_track.connect(
            self.retrieve_costs_for_track)

    def select_input_files(self):
        """
        Select CellX tracking result files to analyze.
        :return: void
        """
        filter_ext = "TXT (*.txt);;All files (*.*)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.FileMode.ExistingFiles)
        res = file_name.getOpenFileNames(self, "Pick CellX result files",
                                         self.last_selected_path, filter_ext)
        names = res[0]
        if len(names) > 0:
            if self.tracker.num_data_frames() > 0:
                print("Previous results discarded!")
            self.tracker.file_list = names
            self.last_selected_path = os.path.dirname(
                self.tracker.file_list[0])
            self.full_update_ui()
            print("Selected %d CellX result files." %
                  (len(self.tracker.file_list)))

    def select_image_files(self):
        """
        Select image files for plotting.
        :return: void
        """
        filter_ext = "TIF (*.tif);;TIFF (*.tiff);;PNG (*.png);;All files (*.*)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.FileMode.ExistingFiles)
        res = file_name.getOpenFileNames(self, "Pick image files",
                                         self.last_selected_path, filter_ext)
        names = res[0]
        if len(names) > 0:
            # Setting the file list to the tracker will sort them
            self.tracker.image_file_list = names
            sorted_image_file_list = self.tracker.image_file_list
            self.last_selected_path = os.path.dirname(sorted_image_file_list[0])
            self.current_image_index = 0
            self.full_update_ui()
            print("Selected %d image files." % (len(sorted_image_file_list)))

    def select_project_folder(self):
        """
        Select folder where to store the results.
        :return: void
        """
        result_dir = QFileDialog.getExistingDirectory(self,
                                                      "Pick project folder",
                                                      self.last_selected_path,
                                                      QFileDialog.Option.ShowDirsOnly |
                                                      QFileDialog.Option.DontResolveSymlinks)

        if result_dir != "":
            self.tracker.result_folder = result_dir
            self.last_selected_path = result_dir
            print("Set project folder to %s." % result_dir)

            # Try loading the project
            self.load_project()

            # Show the folder path on the button
            self.pbSelectProjectFolder.setText(result_dir)

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

    def show_settings_dialog(self):
        """
        Show the settings dialog (initialize if needed).
        :return: void
        """
        if self.settings_dialog is None:
            # We pass a reference to the settings stored in the tracker
            self.settings_dialog = Settings(self.tracker.settings)
            self.settings_dialog.signal_settings_changed.connect(
                self.on_settings_changed)

        # Start it modal
        self.settings_dialog.exec()

    @Slot(dict, name="on_settings_changed")
    def on_settings_changed(self, changed_settings):
        """
        Update the UI
        :return: void
        """

        # Update the settings in the Tracker
        self.tracker.settings = changed_settings

        # Update the plots
        self.update_plots()

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
        self.pbSelectProjectFolder.setEnabled(False)
        self.wgAnalysis.setEnabled(False)
        self.wgInputFiles.setEnabled(False)

    def enable_buttons(self):
        """
        Enable all buttons.
        :return: void
        """
        self.pbSelectProjectFolder.setEnabled(True)
        self.wgAnalysis.setEnabled(True)
        self.wgInputFiles.setEnabled(True)

    def show_image(self, path=None):
        """
        Load and show image.
        @todo: cache at least part of the images
        :param path: (optional, default=None) file name with pull path.
        Set to None to show currently active image.
        :return: void
        """
        if path is None:
            if self.current_image_index > len(
                    self.tracker.image_file_list) - 1:
                return
            path = self.tracker.image_file_list[self.current_image_index]
        img = QImage(path)

        self.scene.display_image(img)

        self.setWindowTitle('Lineage Tracer (%d/%d)' %
                            (self.current_image_index + 1,
                             len(self.tracker.image_file_list)))

    def plot_results(self):
        """
        Plot results of the analysis.

        :return: void
        """
        if self.tracker.result_folder == '':
            self.scene.redraw()
            return

        if len(self.tracker.image_file_list) == 0:
            self.scene.redraw()
            return

        if self.tracker.num_data_frames() == 0:
            self.scene.redraw()
            return

        # Remove the previous plots
        # TODO: Make this a bit cleverer
        self.scene.remove_points()
        self.scene.remove_vectors()

        # Retrieve the options
        plot_raw_vectors = self.cbPlotRawVectors.isChecked()
        plot_filtered_vectors = self.cbPlotFiltVectors.isChecked()
        plot_cell_indices = self.rbPlotCellIndex.isChecked()

        # If the results are not valid (i.e. the user added or removed cells)
        # we do not display the track information
        if not self.tracker.results_up_to_date:
            plot_filtered_vectors = False
            plot_raw_vectors = False

        # Get the data frame
        current_data_frame = self.tracker.load_dataframe_for_index(
            self.current_image_index)

        if current_data_frame is None:
            return

        # Display the positions
        try:

            X = current_data_frame['cell.center.x'].values
            Y = current_data_frame['cell.center.y'].values
            C = current_data_frame["cell.index"].values

            # If there are no results, we disable plotting tracks
            if 'dif.x' not in current_data_frame.columns:
                plot_filtered_vectors = False
                plot_raw_vectors = False
                T = -1 * np.ones(X.shape)
            else:
                U = current_data_frame['dif.x'].values
                V = current_data_frame['dif.y'].values
                fU = current_data_frame['filtered.dif.x'].values
                fV = current_data_frame['filtered.dif.y'].values
                T = current_data_frame["track.index"].values

            # Plot the positions
            points = []
            for i in range(X.shape[0]):
                if plot_cell_indices:
                    point_color = Qt.GlobalColor.red
                    plot_track_index = False
                else:
                    point_color = Qt.GlobalColor.magenta
                    plot_track_index = True
                points.append(Point(float(X[i]), float(Y[i]), 3.0,
                                    cell_index=C[i],
                                    track_index=T[i],
                                    plot_track_index=plot_track_index,
                                    color=point_color))
            self.scene.display_points(points)

            # Plot the vectors
            if plot_raw_vectors:
                vectors = []
                for i in range(X.shape[0]):
                    vectors.append(Vector(float(X[i]), float(Y[i]),
                                          float(U[i]), float(V[i]),
                                          T[i], "raw", True, Qt.GlobalColor.yellow))
                self.scene.display_vectors(vectors)

            # Plot the filtered vectors
            if plot_filtered_vectors:
                filtered_vectors = []
                for i in range(X.shape[0]):
                    filtered_vectors.append(Vector(float(X[i]), float(Y[i]),
                                                   float(fU[i]), float(fV[i]),
                                                   T[i], "filtered", True,
                                                   Qt.GlobalColor.darkGreen))
                self.scene.display_vectors(filtered_vectors)

        except Exception as e:
            print("Could not plot current coordinate! The error was: {0}"
                  .format(e))

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
            self.show_image()
            self.plot_results()

            # Save to disk
            plot_file_name = os.path.join(plot_folder, "plot%05d.tif" % (i + 1))
            self.canvas.figure.savefig(plot_file_name,
                                       dpi=150,
                                       bbox_inches='tight')

            # Inform
            print("Saved plot %s." % plot_file_name)

            # Force redraw
            QApplication.processEvents()

        # Enable buttons
        self.enable_buttons()

        print("Done.")

    def save_project(self):
        """
        Save the project into an HDF5 file..
        """
        if self.tracker.result_folder == "":
            print("Please pick a result folder.")

        # Save the project
        print("Saving...")
        if self.tracker.save():
            print("Done.")
        else:
            print("Could not save the project.")

    def load_project(self):
        """
        Load the information stored in the project HDF5 file.
        :return: True if loading was successful, False otherwise.
        """

        # Full file name (prepend the result folder)
        if self.tracker.result_folder == '':
            return

        # Load the project
        print("Loading...")
        self.tracker.load()
        print("Done.")

    def export_results(self):
        """
        Export results from tracker.
        :return:
        """
        if self.tracker.result_folder == "":
            print("Please pick a result folder.")

        print("Exporting results...")
        self.tracker.export()
        print("Done.")

    def setup_file_viewer(self):
        """
        Set up the file viewer.
        """

        # Initialize widget if need
        if self.file_viewer is None:
            self.file_viewer = FileViewer()

        # Connect the signal
        self.file_viewer.signal_image_index_changed.connect(
            self.handle_changed_image_index)

        # Add a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.file_viewer)
        self.ui.data_layout.addWidget(scroll_area)

        # Show the widget
        self.file_viewer.show()

    def setup_data_viewer(self):
        """
        Set up the data viewer.
        """

        # Initialize widget if need
        if self.data_viewer is None:
            self.data_viewer = DataViewer()

        # Add a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.data_viewer)
        self.ui.result_layout.addWidget(scroll_area)

        # Show the widget
        self.data_viewer.show()

    def show_files_in_file_viewer(self):
        """
        Display the file names om the file viewer.
        :return:
        """
        # Display it
        self.file_viewer.set_data(self.tracker.file_list,
                                  self.tracker.image_file_list)

    def show_results_in_data_viewer(self):
        """
        Displays the results for current frame in the data viewer.
        """
        if self.data_viewer is None:
            return

        if self.tracker.result_folder == '':
            self.data_viewer.clear()
            return

        if len(self.tracker.image_file_list) == 0:
            self.data_viewer.clear()
            return

        if self.tracker.num_data_frames() == 0:
            self.data_viewer.clear()
            return

        if not self.tracker.results_up_to_date:
            self.data_viewer.clear()
            return

        # Load the results if needed
        current_data_frame = self.tracker.load_dataframe_for_index(
            self.current_image_index)

        if current_data_frame is None:
            self.data_viewer.clear()
            return

        # If no results yet, we cannot retrieve track indices and costs.
        if 'track.index' not in current_data_frame.columns:
            self.data_viewer.clear()
            return

        # Display the positions
        X = current_data_frame['cell.center.x'].values
        Y = current_data_frame['cell.center.y'].values
        C = current_data_frame["cell.index"].values
        T = current_data_frame["track.index"].values
        A = current_data_frame["cell.area"].values
        E = current_data_frame["cell.eccentricity"].values

        # Get the costs
        try:
            # The first time point does not have costs associated with it.
            Cost = current_data_frame["cost"].values
            Cost1 = current_data_frame["cost1"].values
            Cost2 = current_data_frame["cost2"].values
            Cost3 = current_data_frame["cost3"].values
            Cost4 = current_data_frame["cost4"].values

        except KeyError:
            Cost = np.empty(X.shape)
            Cost.fill(np.nan)
            Cost1 = np.empty(X.shape)
            Cost1.fill(np.nan)
            Cost2 = np.empty(X.shape)
            Cost2.fill(np.nan)
            Cost3 = np.empty(X.shape)
            Cost3.fill(np.nan)
            Cost4 = np.empty(X.shape)
            Cost4.fill(np.nan)

        # Get the quality control track indices
        try:
            TQC = current_data_frame["qc_track_index"].values
        except KeyError:
            TQC = -1 * np.ones(X.shape)

        # Display it
        self.data_viewer.set_data(T, C, TQC, A, E, Cost,
                                  Cost1, Cost2, Cost3, Cost4)

    @Slot(name="delete_selection")
    def delete_selection(self):
        # DataViewer and Scene are in sync. So we collect the objects to be
        # deleted from the Scene.
        selected_items = self.scene.selectedItems()
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
            self.show_results_in_data_viewer()

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
        self.show_results_in_data_viewer()
