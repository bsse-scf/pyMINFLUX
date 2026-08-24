#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pyminflux.processor import MinFluxProcessor
from pyminflux.processor._dataset import MinFluxDataset
from pyminflux.ui.state import State
from pyminflux.ui.wizard import WizardDialog


@dataclass(frozen=True)
class WorkflowAction:
    """Description of a workflow-owned menu action.

    This is intentionally independent from Qt object names. MainWindow turns
    these descriptors into QActions and dispatches them.
    """

    id: str
    text: str
    handler_name: str
    owner: str = "main_window"
    menu: str | None = "analysis"
    group: str = "default"
    requires_data: bool = True
    refresh_after: bool = False


class BaseWorkflow:
    """Base class for UI workflows.

    Workflows own workflow-specific panels and declare which workflow-specific
    main-window actions should be exposed. The application shell owns common
    actions such as loading data.
    """

    name = "base"

    def __init__(
        self,
        dataset: Optional[MinFluxDataset] = None,
        min_trace_length: int = 1,
    ):
        self.dataset = dataset
        self.min_trace_length = min_trace_length
        self.panel = None
        self.state = State()

    def create_panel(self, parent=None) -> QWidget:
        raise NotImplementedError

    def set_dataset(self, dataset: Optional[MinFluxDataset]) -> None:
        self.dataset = dataset
        if hasattr(self.panel, "set_dataset"):
            self.panel.set_dataset(dataset)

    def plot_dataframe(self) -> Optional[pd.DataFrame]:
        if self.dataset is None:
            return None
        return self.dataset.processed_dataframe

    @property
    def filtered_dataframe_stats(self) -> Optional[pd.DataFrame]:
        return self.stats_dataframe()

    def stats_dataframe(self) -> Optional[pd.DataFrame]:
        return None

    def can_save(self) -> bool:
        return False

    def can_export_data(self) -> bool:
        dataframe = self.plot_dataframe()
        return dataframe is not None and len(dataframe.index) > 0

    @property
    def filename(self):
        if self.dataset is None:
            return None
        return self.dataset.filename

    def export_data_to_csv(self, file_name: str) -> bool:
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return False
        try:
            dataframe.to_csv(file_name, index=False)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False
        return True

    def select_by_index_labels(self, labels: list[int]) -> Optional[pd.DataFrame]:
        """Return plotted rows matching dataframe index labels."""
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None
        labels = [label for label in labels if label in dataframe.index]
        if not labels:
            return dataframe.iloc[[]]
        return dataframe.loc[labels]

    def select_by_2d_range(
        self,
        x_param: str,
        y_param: str,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
    ) -> Optional[pd.DataFrame]:
        """Return plotted rows inside the selected 2D range."""
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None
        if x_param not in dataframe.columns or y_param not in dataframe.columns:
            return dataframe.iloc[[]]

        x_min, x_max = sorted(x_range)
        y_min, y_max = sorted(y_range)
        return dataframe.loc[
            (dataframe[x_param] >= x_min)
            & (dataframe[x_param] < x_max)
            & (dataframe[y_param] >= y_min)
            & (dataframe[y_param] < y_max)
        ]

    def crop_by_2d_range(
        self,
        x_param: str,
        y_param: str,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
    ) -> bool:
        """Crop workflow data by a 2D range.

        The base workflow does not own mutable filtered data, so cropping is a
        no-op by default. Workflows with native filtering should override this.
        """
        return False

    def workflow_actions(self) -> list[WorkflowAction]:
        """Return workflow-specific menu actions exposed by this workflow."""
        return []

    def color_columns(self, dataframe: Optional[pd.DataFrame]) -> list[str]:
        """Return dataframe columns that can be used for point coloring."""
        if dataframe is None:
            return []

        color_columns = []
        columns = set(dataframe.columns)
        if "tid" in columns:
            color_columns.append("tid")
        if "fluo" in columns:
            color_columns.append("fluo")
        if "z" in columns:
            color_columns.append("z")
        if "tim" in columns:
            color_columns.append("tim")
        return color_columns


class LocalizationWorkflow(BaseWorkflow):
    """The existing localization-oriented workflow."""

    name = "localization"

    def __init__(
        self,
        dataset: Optional[MinFluxDataset] = None,
        min_trace_length: int = 1,
    ):
        super().__init__(dataset=dataset, min_trace_length=min_trace_length)
        self.processor = None
        if dataset is not None:
            self.processor = MinFluxProcessor(dataset, min_trace_length)

    def set_dataset(self, dataset: Optional[MinFluxDataset]) -> None:
        self.dataset = dataset
        self.processor = (
            MinFluxProcessor(dataset, self.min_trace_length)
            if dataset is not None
            else None
        )
        if hasattr(self.panel, "set_processor"):
            self.panel.set_processor(self.processor)

    def create_panel(self, parent=None) -> WizardDialog:
        self.panel = WizardDialog(parent)
        self.panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding,
        )
        if self.processor is not None:
            self.panel.set_processor(self.processor)
        return self.panel

    def plot_dataframe(self) -> Optional[pd.DataFrame]:
        if self.processor is None:
            return None
        if (
            self.state.plot_average_localisations
            and self.state.x_param in ["x", "y", "z"]
            and self.state.y_param in ["x", "y", "z"]
        ):
            return self.processor.weighted_localizations
        return self.processor.filtered_dataframe

    def stats_dataframe(self) -> Optional[pd.DataFrame]:
        if self.processor is None:
            return None
        return self.processor.filtered_dataframe_stats

    def crop_by_2d_range(
        self,
        x_param: str,
        y_param: str,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
    ) -> bool:
        if self.processor is None:
            return False
        self.processor.filter_by_2d_range(x_param, y_param, x_range, y_range)
        return True

    def can_save(self) -> bool:
        return self.processor is not None

    def export_data_to_csv(self, file_name) -> bool:
        from pyminflux.writer import MinFluxWriter

        if self.processor is None:
            return False
        return MinFluxWriter.write_csv(self.processor, file_name)

    def workflow_actions(self) -> list[WorkflowAction]:
        return [
            WorkflowAction(
                id="export_stats",
                text="Export stats",
                handler_name="export_filtered_stats",
                menu="file",
            ),
            WorkflowAction(
                id="histogram_plotter",
                text="Histogram Plotter",
                handler_name="open_histogram_plotter",
                group="plots",
            ),
            WorkflowAction(
                id="unmixer",
                text="Unmixer",
                handler_name="open_color_unmixer",
                group="fluorophores",
            ),
            WorkflowAction(
                id="set_fluorophore_names",
                text="Set Fluorophore Names",
                handler_name="open_fluorophore_naming_dialog",
                group="fluorophores",
            ),
            WorkflowAction(
                id="time_inspector",
                text="Time Inspector",
                handler_name="open_time_inspector",
                group="inspection",
            ),
            WorkflowAction(
                id="analyzer",
                text="Analyzer",
                handler_name="open_analyzer",
                group="inspection",
            ),
            WorkflowAction(
                id="trace_stats_viewer",
                text="Trace Stats Viewer",
                handler_name="open_trace_stats_viewer",
                group="plots",
            ),
            WorkflowAction(
                id="frc_analyzer",
                text="FRC analyzer",
                handler_name="open_frc_tool",
                group="plots",
            ),
        ]
