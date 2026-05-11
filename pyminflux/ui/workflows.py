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

from typing import Optional

import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pyminflux.processor import MinFluxProcessor
from pyminflux.processor._dataset import MinFluxDataset
from pyminflux.ui.colors import ColorCode
from pyminflux.ui.state import State
from pyminflux.ui.wizard import WizardDialog


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
        self.processor = None
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

    def export_data_to_csv(self, file_name) -> bool:
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return False
        try:
            dataframe.to_csv(file_name, index=False)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False
        return True

    def workflow_action_names(self) -> list[str]:
        """Return QAction attribute names exposed by this workflow."""
        return []

    def available_color_codes(self, dataframe: Optional[pd.DataFrame]) -> list[ColorCode]:
        """Return semantic color modes supported by the plot dataframe."""
        color_codes = [ColorCode.NONE]
        if dataframe is None:
            return color_codes

        columns = set(dataframe.columns)
        if "tid" in columns:
            color_codes.append(ColorCode.BY_TID)
        if "fluo" in columns:
            color_codes.append(ColorCode.BY_FLUO)
        if "z" in columns:
            color_codes.append(ColorCode.BY_DEPTH)
        if "tim" in columns:
            color_codes.append(ColorCode.BY_TIME)
        return color_codes


class LocalizationWorkflow(BaseWorkflow):
    """The existing localization-oriented workflow."""

    name = "localization"

    def __init__(
        self,
        dataset: Optional[MinFluxDataset] = None,
        min_trace_length: int = 1,
    ):
        super().__init__(dataset=dataset, min_trace_length=min_trace_length)
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

    def can_save(self) -> bool:
        return self.processor is not None

    def export_data_to_csv(self, file_name) -> bool:
        from pyminflux.writer import MinFluxWriter

        if self.processor is None:
            return False
        return MinFluxWriter.write_csv(self.processor, file_name)

    def workflow_action_names(self) -> list[str]:
        return [
            "actionExport_stats",
            "actionHistogram_Plotter",
            "actionUnmixer",
            "actionSet_Fluorophore_Names",
            "actionTime_Inspector",
            "actionAnalyzer",
            "actionTrace_Stats_Viewer",
            "actionFRC_analyzer",
        ]


class TrackingWorkflowPanel(QWidget):
    """Minimal workflow panel for tracking datasets."""

    save_data_triggered = Signal()
    export_data_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataset = None

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Tracking workflow")
        title.setObjectName("trackingWorkflowTitle")
        layout.addWidget(title)

        self.pbSaveData = QPushButton("Save")
        self.pbExportData = QPushButton("Export data")
        self.pbSaveData.clicked.connect(lambda _: self.save_data_triggered.emit())
        self.pbExportData.clicked.connect(lambda _: self.export_data_triggered.emit())
        layout.addWidget(self.pbSaveData)
        layout.addWidget(self.pbExportData)

        placeholder = QLabel("Tracking-specific tools will appear here.")
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder)
        layout.addStretch(1)

        self.setLayout(layout)
        self.enable_controls(False)

    def set_dataset(self, dataset: Optional[MinFluxDataset]) -> None:
        self.dataset = dataset
        self.enable_controls(dataset is not None)

    def enable_controls(self, enabled: bool = False):
        self.pbSaveData.setVisible(False)
        self.pbExportData.setVisible(enabled)


class TrackingWorkflow(BaseWorkflow):
    """Initial tracking workflow.

    It is intentionally dataset-backed for now; workflow implementers can later
    replace plot_dataframe() with a native tracking-model adapter.
    """

    name = "tracking"

    def create_panel(self, parent=None) -> TrackingWorkflowPanel:
        self.panel = TrackingWorkflowPanel(parent)
        if self.dataset is not None:
            self.panel.set_dataset(self.dataset)
        return self.panel

    def stats_dataframe(self) -> Optional[pd.DataFrame]:
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None
        return MinFluxProcessor.calculate_statistics_on(dataframe, is_tracking=True)

    def workflow_action_names(self) -> list[str]:
        return [
            "actionExport_stats",
        ]
