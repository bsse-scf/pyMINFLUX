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

from enum import IntEnum
from typing import Union

from ..base import Singleton
from ..reader.metadata import NativeMetadata


class ColorCode(IntEnum):
    NONE = 0
    BY_TID = 1
    BY_FLUO = 2


class State(metaclass=Singleton):
    """State machine (singleton class).

    This keeps the State for the user interface! That is, only classes under pyminflux.ui
    should use State()! The core API must remain independent of State!
    """

    __SLOTS__ = [
        "applied_cfr_thresholds",
        "applied_efo_thresholds",
        "applied_time_thresholds",
        "applied_tr_len_thresholds",
        "cfr_range",
        "cfr_threshold_factor",
        "cfr_thresholds",
        "color_code",
        "dcr_bin_size",
        "dcr_manual_threshold",
        "dwell_time",
        "efo_bin_size_hz",
        "efo_expected_frequency",
        "efo_range",
        "efo_thresholds",
        "enable_cfr_lower_threshold",
        "enable_cfr_upper_threshold",
        "frc_endpoint_only",
        "frc_lateral_resolution",
        "frc_num_repeats",
        "frc_temporal_resolution",
        "is_tracking",
        "loc_precision_range",
        "min_trace_length",
        "num_fluorophores",
        "open_console_at_start",
        "plot_average_localisations",
        "plot_export_dpi",
        "scale_bar_size",
        "time_thresholds",
        "tr_len_range",
        "tr_len_thresholds",
        "tr_len_top_percentile",
        "weigh_avg_localization_by_eco",
        "x_param",
        "y_param",
        "z_scaling_factor",
    ]

    def __init__(self):
        """Constructor.

        A singleton object of this dataclass acts as a state machine that allows various parts of the
        application to synchronize state among them.
        """

        # Plotting options
        self.plot_average_localisations: bool = False
        self.color_code: ColorCode = ColorCode.NONE

        # Minimum number of localizations to consider a trace
        self.min_trace_length: int = 1

        # EFO bin size in Hz (if 0.0, the bin size will be automatically estimated)
        self.efo_bin_size_hz: float = 1000.0

        # EFO expected frequency for single emitters
        self.efo_expected_frequency: float = 0.0

        # Lower and upper (absolute) thresholds for the EFO, CFR, trace length values and time
        self.efo_thresholds: Union[None, tuple] = None
        self.cfr_thresholds: Union[None, tuple] = None
        self.tr_len_thresholds: Union[None, tuple] = None
        self.time_thresholds: Union[None, tuple] = None

        # Applied lower and upper (absolute) thresholds for the EFO, CFR, trace length values and time
        self.applied_efo_thresholds: Union[None, tuple] = None
        self.applied_cfr_thresholds: Union[None, tuple] = None
        self.applied_tr_len_thresholds: Union[None] = None
        self.applied_time_thresholds: Union[None] = None

        # Histogram ranges
        self.efo_range: Union[None, tuple] = None
        self.cfr_range: Union[None, tuple] = None
        self.tr_len_range: Union[None, tuple] = None
        self.loc_precision_range: Union[None, tuple] = None

        # Parameter bounds
        self.enable_cfr_lower_threshold: bool = False
        self.enable_cfr_upper_threshold: bool = True

        # CFR thresholding parameters
        self.cfr_threshold_factor: float = 2.0

        # Trace length top percentile
        self.tr_len_top_percentile: float = 100.0

        # Weigh average localization by ECO
        self.weigh_avg_localization_by_eco: bool = False

        # Current parameter selection
        self.x_param: str = "x"
        self.y_param: str = "y"

        # Number of fluorophores in the sample
        self.num_fluorophores: int = 1
        self.dcr_bin_size: float = 0.0
        self.dcr_manual_threshold: float = 0.0

        # Z scaling factor
        self.z_scaling_factor: float = 0.7

        # Resolution for exporting plots as images
        self.plot_export_dpi: int = 600

        # FRC analysis
        self.frc_lateral_resolution: float = 4.0
        self.frc_temporal_resolution: float = 1800.0
        self.frc_num_repeats: int = 5
        self.frc_endpoint_only: bool = False

        # Whether to open the console at application start
        self.open_console_at_start: bool = False

        # Dwell time in milliseconds
        self.dwell_time: float = 1.0

        # Is the dataset a tracking acquisition?
        self.is_tracking: bool = False

        # Scale bar size in um
        self.scale_bar_size: float = 500.0

    def asdict(self) -> dict:
        """Return class as dictionary."""
        return {
            "applied_cfr_threshold": self.applied_cfr_thresholds,
            "applied_efo_thresholds": self.applied_efo_thresholds,
            "applied_time_thresholds": self.applied_time_thresholds,
            "applied_tr_len_thresholds": self.applied_tr_len_thresholds,
            "cfr_range": self.cfr_range,
            "cfr_threshold_factor": self.cfr_threshold_factor,
            "cfr_thresholds": self.cfr_thresholds,
            "color_code": str(ColorCode(self.color_code)),
            "dcr_bin_size": self.dcr_bin_size,
            "dcr_manual_threshold": self.dcr_manual_threshold,
            "dwell_time": self.dwell_time,
            "efo_bin_size_hz": self.efo_bin_size_hz,
            "efo_expected_frequency": self.efo_expected_frequency,
            "efo_range": self.efo_range,
            "efo_thresholds": self.efo_thresholds,
            "enable_cfr_lower_threshold": self.enable_cfr_lower_threshold,
            "enable_cfr_upper_threshold": self.enable_cfr_upper_threshold,
            "frc_endpoint_only": self.frc_endpoint_only,
            "frc_lateral_resolution": self.frc_lateral_resolution,
            "frc_num_repeats": self.frc_num_repeats,
            "frc_temporal_resolution": self.frc_temporal_resolution,
            "is_tracking": self.is_tracking,
            "loc_precision_range": self.loc_precision_range,
            "min_trace_length": self.min_trace_length,
            "num_fluorophores": self.num_fluorophores,
            "open_console_at_start": self.open_console_at_start,
            "plot_average_localisations": self.plot_average_localisations,
            "plot_export_dpi": self.plot_export_dpi,
            "scale_bar_size": self.scale_bar_size,
            "time_thresholds": self.time_thresholds,
            "tr_len_range": self.tr_len_range,
            "tr_len_thresholds": self.tr_len_thresholds,
            "tr_len_top_percentile": self.tr_len_top_percentile,
            "weigh_avg_localization_by_eco": self.weigh_avg_localization_by_eco,
            "x_param": self.x_param,
            "y_param": self.y_param,
            "z_scaling_factor": self.z_scaling_factor,
        }

    def reset(self):
        """Reset to data-specific settings."""

        self.applied_cfr_thresholds = None
        self.applied_efo_thresholds = None
        self.applied_time_thresholds = None
        self.applied_tr_len_thresholds = None
        self.cfr_thresholds = None
        self.efo_thresholds = None
        self.time_thresholds = None
        self.tr_len_thresholds = None

    def full_reset(self):
        """Reset to defaults."""

        self.applied_cfr_thresholds = None
        self.applied_efo_thresholds = None
        self.applied_time_thresholds = None
        self.applied_tr_len_thresholds = None
        self.cfr_range = None
        self.cfr_threshold_factor = 2.0
        self.cfr_thresholds = None
        self.color_code: ColorCode = ColorCode.NONE
        self.dcr_bin_size = 0.0
        self.dcr_manual_threshold = 0.0
        self.dwell_time = 1.0
        self.efo_bin_size_hz = 1000.0
        self.efo_expected_frequency = 0.0
        self.efo_range = None
        self.efo_thresholds = None
        self.enable_cfr_lower_threshold = False
        self.enable_cfr_upper_threshold = True
        self.frc_endpoint_only = False
        self.frc_lateral_resolution = 4.0
        self.frc_num_repeats = 5
        self.frc_temporal_resolution = 1800.0
        self.is_tracking = False
        self.loc_precision_range = None
        self.min_trace_length = 1
        self.num_fluorophores = 1
        self.open_console_at_start = False
        self.plot_average_localisations = False
        self.plot_export_dpi = 300
        self.scale_bar_size = 500.0
        self.time_thresholds = None
        self.tr_len_range = None
        self.tr_len_thresholds = None
        self.tr_len_top_percentile = 100.0
        self.weigh_avg_localization_by_eco = False
        self.x_param = "x"
        self.y_param = "y"
        self.z_scaling_factor = 0.7

    def update_from_metadata(self, metadata: NativeMetadata):
        """Update State from the NativeMetadata parameters from a `.pmx` file."""
        self.applied_cfr_thresholds = metadata.cfr_thresholds
        self.applied_efo_thresholds = metadata.efo_thresholds
        self.applied_tr_len_thresholds = metadata.tr_len_thresholds
        self.cfr_thresholds = metadata.cfr_thresholds
        self.dwell_time = metadata.dwell_time
        self.efo_thresholds = metadata.efo_thresholds
        self.is_tracking = metadata.is_tracking
        self.min_trace_length = metadata.min_trace_length
        self.num_fluorophores = metadata.num_fluorophores
        self.scale_bar_size = metadata.scale_bar_size
        self.time_thresholds = metadata.time_thresholds
        self.tr_len_thresholds = metadata.tr_len_thresholds
        self.z_scaling_factor = metadata.z_scaling_factor

    def __str__(self):
        """Human-readable representation."""
        self.__repr__()

    def __repr__(self):
        """State representation."""
        return "\n".join([f"{key}: {value}" for key, value in self.asdict().items()])
