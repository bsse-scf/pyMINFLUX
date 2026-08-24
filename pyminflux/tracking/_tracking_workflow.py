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

import numpy as np
import pandas as pd
from pathlib import Path
from overrides import override

from MinSpt import Dataset as SptDataset

from pyminflux.ui.state import State
from pyminflux.processor import MinFluxProcessor
from pyminflux.processor._dataset import MinFluxDataset as PyMinfluxDataset
from pyminflux.ui.workflows import BaseWorkflow, WorkflowAction
from pyminflux.tracking._tracking_panel import MinSptTrackingWorkflowPanel


class MinSptTrackingWorkflow(BaseWorkflow):
    """Initial tracking workflow.

    It is intentionally dataset-backed for now; workflow implementers can later
    replace plot_dataframe() with a native tracking-model adapter.
    """

    name = "MinSpt_tracking"

    @override
    def __init__(
        self,
        dataset: Optional[PyMinfluxDataset] = None,
        min_trace_length: int = 1,
    ):
        self.min_trace_length = min_trace_length
        self.dataset = self._make_SptDataset_from_MinFluxDataset(dataset)
        self.panel = None
        self.state = State()

        # write import path to dataset META tag for later retrieval
        if self.dataset is not None and dataset is not None:
            self.dataset.set_meta(
                "file_name",
                dataset.filename if dataset.filename is not None else "Unknown",
            )

        # run post initialization to ensure dataset is properly initialized
        self.__post_init__()

    def __post_init__(self):
        # Ensure that the dataset is properly initialized after the object is created
        if self.dataset is None:
            raise ValueError("Dataset must be provided for MinSptTrackingWorkflow.")

    @override
    def set_dataset(self, dataset: Optional[PyMinfluxDataset]) -> None:
        # try to build MinSptDataset object from the new PyMinfluxDataset object
        try:
            self.dataset = self._make_SptDataset_from_MinFluxDataset(dataset)
        except Exception as e:
            print(f"Error occurred while building SptDataset: {e}")

    @override
    def create_panel(self, parent=None) -> MinSptTrackingWorkflowPanel:
        self.panel = MinSptTrackingWorkflowPanel(parent)
        if self.dataset is not None:
            self.panel.set_dataset(self.dataset)
        return self.panel

    # %% Main interface of UI workflow contract
    @override
    def plot_dataframe(self) -> Optional[pd.DataFrame]:
        """
        This method collects all localizations from all trajectories by sequence of their ID and exposes them as a pandas DataFrame.
        This method is the main compatibility layer between the workflow and the UI visualization, as the UI expects a DataFrame representation of the dataset for plotting.

        Returns:
            Optional[pd.DataFrame]: A pandas DataFrame containing all localizations from the dataset, with columns for each plottable axis and additional columns for "tid", "track_index", and "spot_index". If the dataset is None, returns None.
        """

        if self.dataset is None:
            return None

        # collect plottable axes keys from the MinSptDataset object
        plottable_axes = [
            key
            for key in sorted(self.dataset.collect_plottable(), reverse=True)
            if key not in ["ID", "META"]
        ]
        ID_array = np.concatenate(
            [
                np.full(len(trajectory), trajectory.get("ID"))
                for i, trajectory in enumerate(self.dataset.trajectories)
            ]
        )
        table = self.dataset.to_table(select_axes=plottable_axes)

        # make pd df from tabular dataset for UI visualization
        pd_df = pd.DataFrame(table, columns=plottable_axes)
        # add ID column to the pd df
        pd_df["tid"] = ID_array

        # make sure all column names are lowercase to match the original datasetframe structure
        # Important because the MinSpt Dataset uses uppercase column names, while the original PyMinfluxDataset uses lowercase column names.
        pd_df.columns = [col.lower() for col in pd_df.columns]

        return pd_df

    # %% I/O
    @override
    def export_data_to_csv(self, file_name: str) -> bool:
        """
        Export the current dataset to a CSV file using the pandas DataFrame representation of the dataset.
        This method ensures that the dataset is properly converted to a DataFrame and then saved to the specified CSV file.

        Args:
            file_name (str): The name of the CSV file to which the dataset will be exported.

        Returns:
            bool: True if the export was successful, False otherwise.
        """

        if self.dataset is None:
            return False
        try:
            # Convert the dataset to a DataFrame
            df = self.plot_dataframe()
            # catch None case
            if df is None:
                print("No data available to export.")
                return False
            # Export the DataFrame to a CSV file
            df.to_csv(file_name, index=False)
            return True
        except Exception as e:
            print(f"An error occurred while exporting the dataset to CSV: {e}")
            return False

    @override
    def stats_dataframe(self) -> Optional[pd.DataFrame]:
        raise NotImplementedError("This method is not yet implemented.")

        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None
        return MinFluxProcessor.calculate_statistics_on(dataframe, is_tracking=True)

    @override
    def color_columns(self, dataframe: Optional[pd.DataFrame]) -> list[str]:
        """
        Return a list of column names that can be used for coloring the plot.
        The list is based on the columns present in the provided dataframe and the plottable keys collected from the dataset.

        Args:
            dataframe (Optional[pd.DataFrame]): The DataFrame for which to identify colorable columns.

        Returns:
            list[str]: A list of column names that can be used for coloring the plot.
        """
        if dataframe is None:
            return []

        # colect all plottable keys from the dataset and filter them to match the dataframe columns
        plottable_keys = self.dataset.collect_plottable()
        plottable_keys = [
            key
            for key in dataframe.columns
            if key.upper() in plottable_keys and key not in ["ID", "META"]
        ]

        # add ID as a color column option if it is present in the dataframe
        if "tid" in dataframe.columns:
            plottable_keys.append("tid")

        return plottable_keys

    @override
    def select_by_index_labels(self, labels: list[int]) -> Optional[pd.DataFrame]:
        """
        Return plotted rows matching dataframe index labels.
        This method ensures that all localizations belonging to the same trace (tid) are included in the selection,
        even if only a subset of the localizations fall within the specified index labels.

        Args:
            labels (list[int]): List of index labels to select.

        Returns:
            Optional[pd.DataFrame]: The filtered DataFrame.
        """
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None

        # catch empty labels
        if not labels:
            return dataframe.iloc[[]]

        # collect roq indices of selected localizations
        labels = [label for label in labels if label in dataframe.index]
        # collect the unique IDs of the selected localizations
        u_IDs = dataframe.loc[labels, "tid"].unique()
        # collect the index labels of all localizations belonging to the selected IDs
        labels = dataframe[dataframe["tid"].isin(u_IDs)].index.tolist()

        return dataframe.loc[labels]

    @override
    def select_by_2d_range(
        self,
        x_param: str,
        y_param: str,
        x_range: tuple[float, float],
        y_range: tuple[float, float],
    ) -> Optional[pd.DataFrame]:
        """
        Return plotted rows inside the selected 2D range.
        This version of the method ensures that all localizations belonging to the same trace (tid) are included in the selection,
        even if only a subset of the localizations fall within the specified 2D range.

        Args:
            x_param (str): X axis parameter name (column name in the dataframe).
            y_param (str): Y axis parameter name (column name in the dataframe).
            x_range (tuple[float, float]): X axis range.
            y_range (tuple[float, float]): Y axis range.

        Returns:
            Optional[pd.DataFrame]: The filtered DataFrame.
        """
        dataframe = self.plot_dataframe()
        if dataframe is None:
            return None
        if x_param not in dataframe.columns or y_param not in dataframe.columns:
            return dataframe.iloc[[]]

        # gather the rows of all selected localizations
        x_min, x_max = sorted(x_range)
        y_min, y_max = sorted(y_range)
        selected_locs = dataframe.loc[
            (dataframe[x_param] >= x_min)
            & (dataframe[x_param] < x_max)
            & (dataframe[y_param] >= y_min)
            & (dataframe[y_param] < y_max)
        ]

        # gather the unique IDs of all selected rows
        u_IDs = selected_locs["tid"].unique()

        # gather the index labels of all localizations belonging to the selected IDs
        labels = dataframe[dataframe["tid"].isin(u_IDs)].index.tolist()

        return dataframe.loc[labels]

    # %% Workflow Test
    def find_longest_track(self) -> None:
        """Test Workflow Action: Find the longest track in the dataset and print its ID and length."""
        longest_track = self.dataset.get_longest_track()
        print(
            f"Longest track ID: {longest_track.get('ID')}, Length: {len(longest_track.get('T'))} time points."
        )

    # %% Workflow Actions (UI Elements)
    @override
    def workflow_actions(self) -> list[WorkflowAction]:
        return [
            WorkflowAction(
                id="find_longest_track",
                text="Find longest track",
                handler_name="find_longest_track",
                owner="workflow",
                menu=None,
                refresh_after=False,
            ),
        ]

    # %% Helpers
    def _filter_by_tid_length(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the dataset by the length of each trace.
        Removes any trace with less than self.min_trace_length localizations.

        Args:
            dataframe (pd.DataFrame): The input DataFrame to filter.

        Returns:
            pd.DataFrame: The filtered DataFrame.
        """

        # Make sure to count only currently selected rows
        df = dataframe.copy()

        # Select all rows where the count of TIDs is larger than self._min_trace_num
        counts = df["tid"].value_counts(normalize=False)
        mask = df["tid"].isin(counts[counts >= self.min_trace_length].index)
        return df[mask]

    def _make_conversion_dict_from_mfx_PyMinfluxDataset(
        self, py_mfx_dataset: Optional[PyMinfluxDataset]
    ) -> dict[int, dict[str, np.ndarray]]:
        """
        Build a conversion dictionary from a PyMinfluxDataset object to a dictionary format suitable for SptDataset.
        The methods also writes the MINFLUX iMSPECTOR version to the META tag in the conversion dict for the trajectories to inherit.
        Importantly, the MinSpt backend expects time to be called "T" and the ID to be called "ID" in the conversion dict.

        Args:
            py_mfx_dataset (Optional[PyMinfluxDataset]): A PyMinfluxDataset object containing the processed data, i.e. only valid localizations and traces. If None, an empty dictionary is returned.

        Returns:
            dict[int, dict[str, np.ndarray]]: A conversion dictionary where each key is a trace ID (tid) and the value is another dictionary containing the data for that trace, including time ("T"), ID ("ID"), and other relevant axes. The META tag contains the MINFLUX iMSPECTOR version.
        """

        # catch None case
        if py_mfx_dataset is None:
            return {}
        # write MINFLUX iMSPECTOR version to META tag in the conversion dict for the trajectories to inherit
        mfx_version = {
            "MINFLUX_version": {1: "m2205", 2: "m2410"}[py_mfx_dataset._version]
        }

        # extract the dataframe representation of the dataset
        py_mfx_dataframe = py_mfx_dataset.processed_dataframe.copy()

        # apply min_length filter to the dataframe to remove short traces on load-up
        py_mfx_dataframe = self._filter_by_tid_length(py_mfx_dataframe)

        # create conversion dict and populate it with the data from the filtered dataframe
        conversion_dict: dict[int, dict[str, np.ndarray]] = {}
        for tid in np.unique(py_mfx_dataframe["tid"]):
            trace_df = py_mfx_dataframe[py_mfx_dataframe["tid"] == tid]
            # track formation
            # assign localizations to the correct id in chronological order
            # collect everything into arrays but skip the tid column
            trace_dict = {
                key.upper(): trace_df[key].values
                for key in trace_df.columns
                if key not in ["tid", "tim"]
            }

            # add time
            trace_dict["T"] = trace_df["tim"].values

            # add ID
            trace_dict["ID"] = int(tid)

            # add meta tag
            trace_dict["META"] = mfx_version

            conversion_dict[int(tid)] = trace_dict

        # return the conversion dict
        return conversion_dict

    def _make_SptDataset_from_MinFluxDataset(
        self, py_mfx_dataset: Optional[PyMinfluxDataset]
    ) -> SptDataset:
        """
        Create a MinSpt Dataset object from a PyMinfluxDataset object.
        This is the main compatibility layer between the PyMinfluxDataset and the MinSpt Dataset object.

        Args:
            py_mfx_dataset (Optional[PyMinfluxDataset]): A PyMinfluxDataset object containing the processed data, i.e. only valid localizations and traces. If None, an error is raised.

        Raises:
            ValueError: If py_mfx_dataset is None, indicating that a valid PyMinfluxDataset is required to create a MinSpt Dataset.

        Returns:
            SptDataset: A MinSpt Dataset object initialized with the data from the PyMinfluxDataset.
        """
        if py_mfx_dataset is None:
            raise ValueError("Cannot create SptDataset from None PyMinfluxDataset.")
        conversion_dict = self._make_conversion_dict_from_mfx_PyMinfluxDataset(
            py_mfx_dataset
        )
        dataset = SptDataset.with_additional_data(conversion_dict)

        # Basic Pre-Processing on Dataset Creation from Minflux File
        dataset.rescale_time()  # <- make every track start at t=0 and write the original time to the AQT (Aquisition Time) column
        dataset.rescale_IDs()  # <- make every track have a unique ID starting from 0; this way the Id matches the index of the track in the dataset.trajectories list

        return dataset

    # %% Properties
    @property
    @override
    def filename(self) -> Optional[Path]:
        if self.dataset is None:
            return None
        return self.dataset.get_meta("file_name", default=None)

    @filename.setter
    def filename(self, *args, **kwargs) -> None:
        raise ValueError(
            "Cannot set filename on a tracking workflow; it is read-only and derived from the dataset."
        )
