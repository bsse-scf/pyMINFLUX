from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QSizePolicy, QTableView

from .pandas_datamodel import PandasDataModel


class DataViewer(QTableView):
    """
    A QTableWidget to display track data.
    """

    def __init__(self, *args):
        super().__init__()

        self.data_model = None

        # #self.setup()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred
        )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setWindowTitle("Parameters")

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

    def clear(self):
        """
        Remove all rows.
        :return:
        """
        self.setRowCount(0)
        self.viewport().update()

    def select_and_scroll_to_rows(self, indices):
        """Select the rows at given indices and then scroll to the first."""

        # Clear current selection
        self.clearSelection()

        # Select the rows corresponding to the selected points
        for index in indices:
            self.selectRow(index)

        # Scroll to the first selected row
        selected_rows = self.selectedIndexes()
        if len(selected_rows) > 0:
            self.scrollTo(selected_rows[0])

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
