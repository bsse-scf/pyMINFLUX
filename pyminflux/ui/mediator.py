#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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
import sys

from pyminflux.ui.emittingstream import EmittingStream


class Mediator:
    def __init__(self):
        self.dialogs = {}

    def register_dialog(self, dialog_name, dialog_instance):
        """Register a dialog and set up its connections."""
        self.dialogs[dialog_name] = dialog_instance
        self.setup_dialog_connections(dialog_name)

    def unregister_dialog(self, dialog_name):
        """Unregister a dialog and disconnect its connections."""
        if dialog_name in self.dialogs:
            self.remove_dialog_connections(dialog_name)
            del self.dialogs[dialog_name]

    def setup_dialog_connections(self, dialog_name):
        """Set up the connections for the specified dialog."""

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        # Plotter Toolbar
        if dialog_name == "plotter_toolbar":
            self._setup_plotter_toolbar_connections()

        # Plotter
        elif dialog_name == "plotter":
            self._setup_plotter_connections()

        # Wizard
        elif dialog_name == "wizard":
            self._setup_wizard_connections()

        # Options
        elif dialog_name == "options" and "options" in self.dialogs:
            self._setup_options_connections()

        elif dialog_name == "analyzer" and "analyzer" in self.dialogs:
            self._setup_analyzer_connections()

        elif dialog_name == "time_inspector" and "time_inspector" in self.dialogs:
            self._setup_time_inspector_connections()

        elif dialog_name == "histogram_plotter" and "histogram_plotter" in self.dialogs:
            self._setup_histogram_plotter_connections()

        elif dialog_name == "txt_console" and "txt_console" in self.dialogs:
            self._setup_txt_console_connections()

        elif (
            dialog_name == "trace_stats_viewer" and "trace_stats_viewer" in self.dialogs
        ):
            self._setup_trace_stats_viewer_connections()

        elif dialog_name == "color_unmixer" and "color_unmixer" in self.dialogs:
            self._setup_color_unmixer_connections()

        elif dialog_name == "data_viewer" and "data_viewer" in self.dialogs:
            self._setup_data_viewer_connections()

        elif dialog_name == "main_window":
            pass

        else:
            print(f"DEBUG: '{dialog_name}' not found in dialog dictionary!")

    def _setup_analyzer_connections(self):
        """Set up the Analyzer connections."""

        if "wizard" not in self.dialogs:
            raise Exception("The Wizard must always be registered in the Mediator.")

        self.dialogs["wizard"].wizard_filters_run.connect(self.dialogs["analyzer"].plot)
        self.dialogs["main_window"].request_sync_external_tools.connect(
            self.dialogs["analyzer"].plot
        )
        self.dialogs["wizard"].efo_bounds_modified.connect(
            self.dialogs["analyzer"].change_efo_bounds
        )
        self.dialogs["wizard"].cfr_bounds_modified.connect(
            self.dialogs["analyzer"].change_cfr_bounds
        )
        self.dialogs["analyzer"].data_filters_changed.connect(
            self.dialogs["main_window"].full_update_ui
        )
        self.dialogs["analyzer"].efo_bounds_changed.connect(
            self.dialogs["wizard"].change_efo_bounds
        )
        self.dialogs["analyzer"].cfr_bounds_changed.connect(
            self.dialogs["wizard"].change_cfr_bounds
        )

        if "histogram_plotter" in self.dialogs:
            self.dialogs["analyzer"].data_filters_changed.connect(
                self.dialogs["histogram_plotter"].plot_histogram
            )

        if "time_inspector" in self.dialogs:
            self.dialogs["analyzer"].data_filters_changed.connect(
                self.dialogs["time_inspector"].update
            )

        if "trace_stats_viewer" in self.dialogs:
            self.dialogs["analyzer"].data_filters_changed.connect(
                self.dialogs["trace_stats_viewer"].update
            )

    def _setup_color_unmixer_connections(self):
        """Set up the Color Unmixer connections."""

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        if "wizard" not in self.dialogs:
            raise Exception("The Wizard must always be registered in the Mediator.")

        self.dialogs["color_unmixer"].fluorophore_ids_assigned.connect(
            self.dialogs["wizard"].set_fluorophore_list
        )
        self.dialogs["color_unmixer"].fluorophore_ids_assigned.connect(
            self.dialogs["main_window"].plot_selected_parameters
        )

        self.dialogs["wizard"].wizard_filters_run.connect(
            self.dialogs["main_window"].plot_selected_parameters
        )

        if "trace_stats_viewer" in self.dialogs:
            self.dialogs["color_unmixer"].fluorophore_ids_assigned.connect(
                self.dialogs["trace_stats_viewer"].update
            )

    def _setup_data_viewer_connections(self):
        """Set up the Data Viewer connections."""

        # Nothing to set up
        return

    def _setup_histogram_plotter_connections(self):
        """Set up the Histogram Plotter connections."""

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        if "wizard" not in self.dialogs:
            raise Exception("The Wizard must always be registered in the Mediator.")

        self.dialogs["main_window"].request_sync_external_tools.connect(
            self.dialogs["histogram_plotter"].plot_histogram
        )
        self.dialogs["wizard"].wizard_filters_run.connect(
            self.dialogs["histogram_plotter"].plot_histogram
        )
        self.dialogs["wizard"].fluorophore_id_changed.connect(
            self.dialogs["histogram_plotter"].plot_histogram
        )

        if "analyzer" in self.dialogs:
            self.dialogs["analyzer"].data_filters_changed.connect(
                self.dialogs["histogram_plotter"].plot_histogram
            )

        if "color_unmixer" in self.dialogs:
            self.dialogs["color_unmixer"].fluorophore_ids_assigned.connect(
                self.dialogs["histogram_plotter"].plot_histogram
            )

        if "time_inspector" in self.dialogs:
            self.dialogs["time_inspector"].dataset_time_filtered.connect(
                self.dialogs["histogram_plotter"].plot_histogram
            )

    def _setup_options_connections(self):
        """Set up the Options connections."""

        self.dialogs["options"].weigh_avg_localization_by_eco_option_changed.connect(
            self.dialogs[
                "main_window"
            ].update_weighted_average_localization_option_and_plot
        )
        self.dialogs["options"].min_trace_length_option_changed.connect(
            self.dialogs["main_window"].update_min_trace_length
        )

    def _setup_plotter_connections(self):
        """Set up the Plotter connections."""

        if "plotter" not in self.dialogs:
            raise Exception("The Plotter must always be registered in the Mediator.")

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        self.dialogs["plotter"].locations_selected.connect(
            self.dialogs["main_window"].show_selected_points_by_indices_in_dataviewer
        )
        self.dialogs["plotter"].locations_selected_by_range.connect(
            self.dialogs["main_window"].show_selected_points_by_range_in_dataviewer
        )
        self.dialogs["plotter"].crop_region_selected.connect(
            self.dialogs["main_window"].crop_data_by_range
        )

    def _setup_plotter_toolbar_connections(self):
        """Set up the Plotter Toolbar connections."""

        if "plotter_toolbar" not in self.dialogs:
            raise Exception(
                "The Plotter Toolbar must always be registered in the Mediator."
            )

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        self.dialogs["plotter_toolbar"].plot_requested_parameters.connect(
            self.dialogs["main_window"].plot_selected_parameters
        )

        self.dialogs["plotter_toolbar"].plot_average_positions_state_changed.connect(
            self.dialogs["main_window"].full_update_ui
        )

        self.dialogs["plotter_toolbar"].color_code_locs_changed.connect(
            self.dialogs["main_window"].plot_selected_parameters
        )

    def _setup_time_inspector_connections(self):
        """Set up the Time Inspector connections."""

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        if "wizard" not in self.dialogs:
            raise Exception("The Wizard must always be registered in the Mediator.")

        self.dialogs["time_inspector"].dataset_time_filtered.connect(
            self.dialogs["main_window"].full_update_ui
        )
        self.dialogs["wizard"].wizard_filters_run.connect(
            self.dialogs["time_inspector"].update
        )
        self.dialogs["main_window"].request_sync_external_tools.connect(
            self.dialogs["time_inspector"].update
        )

        if "analyzer" in self.dialogs:
            self.dialogs["analyzer"].data_filters_changed.connect(
                self.dialogs["time_inspector"].update
            )
            self.dialogs["time_inspector"].dataset_time_filtered.connect(
                self.dialogs["analyzer"].plot
            )

        if "histogram_plotter" in self.dialogs:
            self.dialogs["time_inspector"].dataset_time_filtered.connect(
                self.dialogs["histogram_plotter"].plot_histogram
            )

        if "trace_stats_viewer" in self.dialogs:
            self.dialogs["time_inspector"].dataset_time_filtered.connect(
                self.dialogs["trace_stats_viewer"].update
            )

    def _setup_trace_stats_viewer_connections(self):
        """Set up the Trace Stats Viewer connections."""

        if "main_window" not in self.dialogs:
            raise Exception(
                "The Main Window must always be registered in the Mediator."
            )

        if "wizard" not in self.dialogs:
            raise Exception("The Wizard must always be registered in the Mediator.")

        self.dialogs["main_window"].request_sync_external_tools.connect(
            self.dialogs["trace_stats_viewer"].update
        )
        self.dialogs["wizard"].request_fluorophore_ids_reset.connect(
            self.dialogs["trace_stats_viewer"].update
        )
        self.dialogs["wizard"].wizard_filters_run.connect(
            self.dialogs["trace_stats_viewer"].update
        )
        self.dialogs["trace_stats_viewer"].export_trace_stats_requested.connect(
            self.dialogs["main_window"].export_filtered_stats
        )
        self.dialogs["wizard"].fluorophore_id_changed.connect(
            self.dialogs["trace_stats_viewer"].update
        )

        if "time_inspector" in self.dialogs:
            self.dialogs["time_inspector"].dataset_time_filtered.connect(
                self.dialogs["trace_stats_viewer"].update
            )

        if "color_unmixer" in self.dialogs:
            self.dialogs["color_unmixer"].fluorophore_ids_assigned.connect(
                self.dialogs["trace_stats_viewer"].update
            )

        if "analyzer" in self.dialogs:
            self.dialogs["analyzer"].data_filters_changed.connect(
                self.dialogs["trace_stats_viewer"].update
            )

    def _setup_txt_console_connections(self):
        """Set up text console connections."""

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.signal_text_written.connect(
            self.dialogs["main_window"].print_to_console
        )

    def _setup_wizard_connections(self):
        """Set up the Wizard connections."""

        if "wizard" not in self.dialogs:
            raise Exception("The Wizard must always be registered in the Mediator.")

        self.dialogs["wizard"].load_data_triggered.connect(
            self.dialogs["main_window"].select_and_load_or_import_data_file
        )
        self.dialogs["wizard"].reset_filters_triggered.connect(
            self.dialogs["main_window"].reset_filters_and_broadcast
        )
        self.dialogs["wizard"].open_unmixer_triggered.connect(
            self.dialogs["main_window"].open_color_unmixer
        )
        self.dialogs["wizard"].open_time_inspector_triggered.connect(
            self.dialogs["main_window"].open_time_inspector
        )
        self.dialogs["wizard"].open_analyzer_triggered.connect(
            self.dialogs["main_window"].open_analyzer
        )
        self.dialogs["wizard"].fluorophore_id_changed.connect(
            self.dialogs["main_window"].update_fluorophore_id_in_processor_and_broadcast
        )
        self.dialogs["wizard"].request_fluorophore_ids_reset.connect(
            self.dialogs["main_window"].reset_fluorophore_ids
        )
        self.dialogs["wizard"].wizard_filters_run.connect(
            self.dialogs["main_window"].full_update_ui
        )
        self.dialogs["wizard"].save_data_triggered.connect(
            self.dialogs["main_window"].save_native_file
        )
        self.dialogs["wizard"].export_data_triggered.connect(
            self.dialogs["main_window"].export_filtered_data
        )
        self.dialogs["wizard"].load_filename_triggered.connect(
            self.dialogs["main_window"].select_and_load_or_import_data_file
        )

    def remove_dialog_connections(self, dialog_name):
        """Remove the connections of the specified dialog.

        The Qt object model disconnects signals and slots
        automatically when dialogs are closed. We only restore
        the redirection from sys.stdout.
        """

        if dialog_name == "txt_console" and dialog_name in self.dialogs:
            # Restore sys.stdout
            sys.stdout = sys.__stdout__
            sys.stdout.flush()
