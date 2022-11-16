from PySide6 import QtCore
from PySide6.QtCore import Signal, QPoint
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QSizePolicy, QAbstractItemView, QMenu, QTableView, QFrame
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QAction
import numpy as np

from .Point import Point
from .pandas_datamodel import PandasDataModel


class DataViewer(QTableView):
    """
    A QTableWidget to display track data.
    """

    # Add a signal for changing selection in the data viewer
    signal_selection_completed = Signal(list, name='signal_selection_completed')

    def __init__(self, *args):
        super().__init__()

        self.data_model = None

        # #self.setup()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        #self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setWindowTitle("Parameters")
        #self.itemSelectionChanged.connect(self.selection_changed)

        # Add a context menu to the table
        #self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.context_menu)

    # @Slot(QPoint, name="context_menu")
    # def context_menu(self, position):
    #     if self.rowCount() == 0:
    #         return
    #     menu = QMenu()
    #     plot_action = QAction("Plot track costs", self)
    #     menu.addAction(plot_action)
    #     action = menu.exec_(self.mapToGlobal(position))
    #     if action == plot_action:
    #         row = self.rowAt(position.y())
    #         try:
    #             track_index = int(self.item(row, 0).text())
    #         except ValueError:
    #             print("Could not retrieve track index! This seems to be a "
    #                   "bug. Please report it!")
    #             return
    #         self.signal_retrieve_costs_for_track.emit(track_index)

    def set_data(self, df):
        """Display the Pandas dataframe."""
        self.data_model = PandasDataModel(df)
        self.setModel(self.data_model)
        self.show()

    def optimize(self):
        """Asking the QTableView to automatically resize the columns is very slow for large models.

        With this function, the column can be resized only once on demand.
        """
        for c in range(self.model().columnCount()):
            self.resizeColumnToContents(c)


        # def set_data(self, tid, aid, vld, x, y, z, tim, efo, cfr, dcr):
    #     """
    #     Displays the input data.
    #     """
    #
    #     # Delete current content
    #     self.setRowCount(0)
    #
    #     # Create enough rows to fit the data
    #     num_elements = len(tid)
    #     if num_elements == 0:
    #         self.viewport().update()
    #         return
    #
    #     # Fill the table
    #     self.setRowCount(num_elements)
    #     for i in range(num_elements):
    #
    #         # Track index
    #         new_item = QTableWidgetItem(str(int(tid[i])))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 0, new_item)
    #
    #         # Cell index
    #         new_item = QTableWidgetItem(str(int(tid[i])))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 1, new_item)
    #
    #         # Track index (quality control)
    #         if np.isnan(TQC[i]):
    #             v = -1
    #         else:
    #             v = int(TQC[i])
    #         new_item = QTableWidgetItem(str(v))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 2, new_item)
    #
    #         # Area
    #         new_item = QTableWidgetItem(str(A[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 3, new_item)
    #
    #         # Eccentricity
    #         new_item = QTableWidgetItem(str(E[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 4, new_item)
    #
    #         # Cost
    #         new_item = QTableWidgetItem(str(Cost[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 5, new_item)
    #
    #         # Cost1
    #         new_item = QTableWidgetItem(str(Cost1[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 6, new_item)
    #
    #         # Cost2
    #         new_item = QTableWidgetItem(str(Cost2[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 7, new_item)
    #
    #         # Cost3
    #         new_item = QTableWidgetItem(str(Cost3[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 8, new_item)
    #
    #         # Cost4
    #         new_item = QTableWidgetItem(str(Cost4[i]))
    #         new_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                           QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(i, 9, new_item)

    # def setup(self):
    #     """
    #     Sets the column headers.
    #     """
    #     headers = ['Ti', 'Ci', 'Ti (QC)',
    #                'A', 'E', 'C', 'C1',
    #                'C2', 'C3', 'C4']
    #     tooltips = ['Track index', 'Cell index', 'Track index (QC)',
    #                 'Cell area', 'Cell eccentricity', 'Total cost', 'Cost 1',
    #                 'Cost 2', 'Cost 3', 'Cost 4']
    #     self.setHorizontalHeaderLabels(headers)
    #     self.setRowCount(0)
    #     for i in range(10):
    #
    #         # Set a tool tip for the column
    #         self.horizontalHeaderItem(i).setToolTip(tooltips[i])
    #
    #         # Add an empty cell
    #         empty_item = QTableWidgetItem("")
    #         empty_item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable |
    #                             QtCore.Qt.ItemFlag.ItemIsEnabled)
    #         self.setItem(0, i, empty_item)

    def clear(self):
        """
        Remove all rows.
        :return:
        """
        self.setRowCount(0)
        self.viewport().update()

    @Slot(name="selection_changed")
    def selection_changed(self):
        """
        Called on selection change.
        """
        cell_indices = []
        rows = self.selectionModel().selectedRows()
        for row in rows:
            cell_index = self.model().index(row.row(), 1).data()
            cell_indices.append(cell_index)
        self.signal_selection_completed.emit(cell_indices)

    @Slot(list, name="handle_scene_selection_completed")
    def handle_scene_selection_completed(self, items):

        cell_indices = []
        for item in items:
            if isinstance(item, Point):
                cell_indices.append(item.cell_index)

        self.highlight_rows_for_cell_indices(cell_indices)

    def highlight_rows_for_cell_indices(self, indices):
        """
        Highlight the rows with cell index corresponding to the indices of the selected Points. 
        :param indices: cell indices of the selected Points.
        :return: 
        """
        self.selectionModel().clearSelection()

        for i in range(self.rowCount()):
            if self.item(i, 1).text() in indices:
                self.selectRow(i)

    def delete_rows(self, cell_indices):
        """
        Delete rows for given cell indices.
        :param cell_indices: cell indices
        :return: 
        """
        rows = []
        for i in range(self.rowCount()):
            if int(self.item(i, 1).text()) in cell_indices:
                rows.append(i)

        self.selectionModel().removeRows(rows)
