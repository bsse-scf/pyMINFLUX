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

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QSizePolicy, QTableView

from ..processor import MinFluxProcessor
from ..state import State
from .pandas_datamodel import PandasDataModel


class DataViewer(QTableView):
    """
    A QTableWidget to display track data.
    """

    def __init__(self, *args):
        super().__init__()

        # Initialize data model to None
        self.data_model = None

        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred
        )
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setWindowTitle("Parameters")

        # Initialize the model with an empty dataframe with the correct columns
        self.set_data(pd.DataFrame(columns=MinFluxProcessor.processed_properties()))

        # Keep a reference to the singleton State class
        self.state = State()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            value = self.data_model[index.row()][index.column()]
            if isinstance(value, float):  # Check if the value is a float
                return f"{value:.2f}"  # Format the float value with 2 decimal places
            return value
        return None

    def set_data(self, df):
        """Display the Pandas dataframe."""
        self.data_model = PandasDataModel(df)
        self.setModel(self.data_model)
        self.show()

    def clear(self):
        """Clear the model."""
        if self.model() is None:
            # Nothing to clear
            return

        # Pass an empty dataframe with correct columns
        df = pd.DataFrame(columns=MinFluxProcessor.processed_properties())
        self.set_data(df)
