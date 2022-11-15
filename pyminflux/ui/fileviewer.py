from PyQt6 import QtCore

from PyQt6.QtCore import pyqtSignal, QPoint
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QSizePolicy, QAbstractItemView, QMenu
from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtWidgets import QHeaderView
import ntpath


class FileViewer(QTableWidget, QObject):
    """
    A QTableWidget to display files.
    """

    # Define signals
    signal_image_index_changed = pyqtSignal(int, name='signal_image_index_changed')
    signal_request_revert_file = pyqtSignal(str, name='signal_request_revert_file')

    def __init__(self):
        """
        Constructor.
        :param func: A function that is called with the index of selected (clicked) row
        """
        QTableWidget.__init__(self, 1, 3)
        self.setup()
        self.resizeRowsToContents()
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.cellClicked.connect(self.handle_cell_clicked)
        self.setWindowTitle("Lineage Tracer :: File Viewer")

        # Add a context menu to the table
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    @pyqtSlot(QPoint, name="context_menu")
    def context_menu(self, position):
        if self.rowCount() == 0:
            return
        menu = QMenu()
        revert_action = QAction("Revert to file", self)
        menu.addAction(revert_action)
        action = menu.exec_(self.mapToGlobal(position))
        if action == revert_action:
            row = self.rowAt(position.y())
            try:
                file_name = self.item(row, 1).text()
            except ValueError:
                print("Could not retrieve file name! This seems to be a "
                      "bug. Please report it!")
                return
            self.signal_request_revert_file.emit(file_name)

    def set_data(self, input_files, image_files):
        """
        Displays the files.
        """
        # Delete current content
        self.setRowCount(0)

        # Create enough rows to fit the data
        num_elements = max(len(input_files), len(image_files))
        if num_elements == 0:
            self.viewport().update()
            return

        # Fill the table
        self.setRowCount(num_elements)
        for i in range(num_elements):

            # Modified flag
            new_item = QTableWidgetItem("")
            new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
                              QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.setItem(i, 0, new_item)

            # Input file name
            try:
                input_file = ntpath.basename(input_files[i])
            except IndexError:
                input_file = ''

            new_item = QTableWidgetItem(ntpath.basename(input_file))
            new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
                              QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.setItem(i, 1, new_item)

            # Image file name index
            try:
                image_file = ntpath.basename(image_files[i])
            except IndexError:
                image_file = ''

            new_item = QTableWidgetItem(ntpath.basename(image_file))
            new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
                              QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.setItem(i, 2, new_item)

    def setup(self):
        """
        Sets the column headers.
        """
        headers = ['M', 'Data frame', 'Image']
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(0)
        for i in range(2):
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
                                QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.setItem(0, i, empty_item)

        # Set column sizes and modes
        self.horizontalHeader().resizeSection(0, 20)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    @pyqtSlot(int, int)
    def handle_cell_clicked(self, row, col):
        """
        Emits the signal_image_index_changed signal after a user click on a cell.

        :param row: row number of the cell clicked on.
        :param col: column number of the cell clicked on.
        """
        self.signal_image_index_changed.emit(row)

    @pyqtSlot(int, bool)
    def mark_as_modified(self, index, reverted=False):
        """
        Mark the row corresponding to the selected data frame as modified.
        :param reverted: boolean to indicate whether the data frame was
        modified from or reverted to the original file. If reverted is False,
        the dataframe is no longer in sync with the file, if reverted is True,
        it is.
        :type reverted: bool
        :param index row index
        :type index int
        """
        item = self.item(index, 0)
        if reverted:
            item.setText('')
        else:
            item.setText('*')
