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

    def select_by_index_labels(self, labels: list) -> Optional[pd.DataFrame]:
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


class TrackingWorkflowPanel(QWidget):
    """Minimal workflow panel for tracking datasets."""

    workflow_action_triggered = Signal(str)
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
        self.pbCalculateLengths = QPushButton("Calculate lengths")
        self.pbRemoveLargestTrack = QPushButton("Remove largest track")
        self.pbExportData = QPushButton("Export data")
        self.pbSaveData.clicked.connect(lambda _: self.save_data_triggered.emit())
        self.pbCalculateLengths.clicked.connect(
            lambda _: self.workflow_action_triggered.emit("calculate_track_lengths")
        )
        self.pbRemoveLargestTrack.clicked.connect(
            lambda _: self.workflow_action_triggered.emit("remove_largest_track")
        )
        self.pbExportData.clicked.connect(lambda _: self.export_data_triggered.emit())
        layout.addWidget(self.pbSaveData)
        layout.addWidget(self.pbCalculateLengths)
        layout.addWidget(self.pbRemoveLargestTrack)
        layout.addWidget(self.pbExportData)

        placeholder = QLabel("Tracks are stored internally as lists of spots.")
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
        self.pbCalculateLengths.setVisible(enabled)
        self.pbRemoveLargestTrack.setVisible(enabled)
        self.pbExportData.setVisible(enabled)


class TrackingWorkflow(BaseWorkflow):
    """Initial tracking workflow.

    It is intentionally dataset-backed for now; workflow implementers can later
    replace plot_dataframe() with a native tracking-model adapter.
    """

    name = "tracking"

    def __init__(
        self,
        dataset: Optional[MinFluxDataset] = None,
        min_trace_length: int = 1,
    ):
        super().__init__(dataset=dataset, min_trace_length=min_trace_length)
        self.tracks = []
        self._tracks_dataframe = None
        self._build_tracks()

    def set_dataset(self, dataset: Optional[MinFluxDataset]) -> None:
        super().set_dataset(dataset)
        self._build_tracks()

    def create_panel(self, parent=None) -> TrackingWorkflowPanel:
        self.panel = TrackingWorkflowPanel(parent)
        if self.dataset is not None:
            self.panel.set_dataset(self.dataset)
        return self.panel

    def _build_tracks(self):
        """Build list-of-dicts track representation from the dataset dataframe."""
        self.tracks = []
        self._tracks_dataframe = None
        if self.dataset is None or self.dataset.processed_dataframe is None:
            return

        dataframe = self.dataset.processed_dataframe
        if "tid" not in dataframe.columns:
            return

        for tid, group in dataframe.groupby("tid", sort=False):
            if "tim" in group.columns:
                group = group.sort_values("tim")
            spots = group.to_dict(orient="records")
            for spot in spots:
                spot["tid"] = tid
            self.tracks.append(
                {
                    "spots": spots,
                    "properties": {},
                }
            )

    def calculate_track_lengths(self):
        """Calculate total path length for each track and store it as a property."""
        for track in self.tracks:
            track["properties"]["length"] = self._calculate_track_length(track)

        self._tracks_dataframe = None

    def remove_largest_track(self):
        """Remove the track with the largest calculated path length."""
        if not self.tracks:
            return

        lengths = [self._track_length(track) for track in self.tracks]
        largest_track_index = int(np.nanargmax(lengths))
        del self.tracks[largest_track_index]
        self._tracks_dataframe = None

    def _track_length(self, track) -> float:
        length = track["properties"].get("length")
        if length is None:
            length = self._calculate_track_length(track)
            track["properties"]["length"] = length
        return length

    def _calculate_track_length(self, track) -> float:
        spots = track["spots"]
        if len(spots) < 2:
            return 0.0

        use_z = bool(self.dataset is not None and self.dataset.is_3d)
        coords = [
            [
                float(spot.get("x", np.nan)),
                float(spot.get("y", np.nan)),
                *([float(spot.get("z", np.nan))] if use_z else []),
            ]
            for spot in spots
        ]
        coords = np.asarray(coords, dtype=float)
        diffs = np.diff(coords, axis=0)
        return float(np.nansum(np.linalg.norm(diffs, axis=1)))

    def plot_dataframe(self) -> Optional[pd.DataFrame]:
        return self._tracks_to_dataframe()

    def export_data_to_csv(self, file_name) -> bool:
        dataframe = self._tracks_to_dataframe()
        if dataframe is None:
            return False
        try:
            dataframe.to_csv(file_name, index=False)
        except Exception as e:
            print(f"Could not save {file_name}: {e}")
            return False
        return True

    def _tracks_to_dataframe(self) -> Optional[pd.DataFrame]:
        if self._tracks_dataframe is not None:
            return self._tracks_dataframe

        rows = []
        for track_index, track in enumerate(self.tracks):
            properties = track["properties"]
            for spot_index, spot in enumerate(track["spots"]):
                row = dict(spot)
                row["track_index"] = track_index
                row["spot_index"] = spot_index
                for name, value in properties.items():
                    row[name] = value
                rows.append(row)

        if not rows:
            return None

        self._tracks_dataframe = pd.DataFrame(rows)
        return self._tracks_dataframe

    def stats_dataframe(self) -> Optional[pd.DataFrame]:
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None
        return MinFluxProcessor.calculate_statistics_on(dataframe, is_tracking=True)

    def workflow_actions(self) -> list[WorkflowAction]:
        return [
            WorkflowAction(
                id="export_stats",
                text="Export stats",
                handler_name="export_filtered_stats",
                menu="file",
            ),
            WorkflowAction(
                id="calculate_track_lengths",
                text="Calculate lengths",
                handler_name="calculate_track_lengths",
                owner="workflow",
                menu=None,
                refresh_after=True,
            ),
            WorkflowAction(
                id="remove_largest_track",
                text="Remove largest track",
                handler_name="remove_largest_track",
                owner="workflow",
                group="tracks",
                refresh_after=True,
            ),
        ]

    def color_columns(self, dataframe: Optional[pd.DataFrame]) -> list[str]:
        """Tracking exposes only track-level length as an optional color column."""
        if dataframe is not None and "length" in dataframe.columns:
            return ["length"]
        return []
