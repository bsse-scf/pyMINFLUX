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

from enum import IntEnum
from pprint import pprint
from typing import Union

from ..base import Singleton


class ColorCode(IntEnum):
    NONE = 0
    BY_TID = 1
    BY_FLUO = 2


class State(metaclass=Singleton):
    """State machine (singleton class)."""

    __SLOTS__ = [
        "plot_average_localisations",
        "color_code",
        "min_num_loc_per_trace",
        "efo_expected_frequency",
        "efo_thresholds",
        "cfr_thresholds",
        "efo_range",
        "cfr_range",
        "loc_precision_range",
        "enable_cfr_lower_threshold",
        "enable_cfr_upper_threshold",
        "cfr_threshold_factor",
        "efo_bin_size_hz",
        "weigh_avg_localization_by_eco",
        "x_param",
        "y_param",
        "num_fluorophores",
        "dcr_bin_size",
        "dcr_manual_threshold",
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
        self.min_num_loc_per_trace: int = 1

        # EFO bin size in Hz (if 0.0, the bin size will be automatically estimated)
        self.efo_bin_size_hz: float = 1000.0

        # EFO expected frequency for single emitters
        self.efo_expected_frequency: float = 0.0

        # Lower and upper (absolute) thresholds for the EFO and CFR values
        self.efo_thresholds: Union[None, tuple] = None
        self.cfr_thresholds: Union[None, tuple] = None

        # Histogram ranges
        self.efo_range: Union[None, tuple] = None
        self.cfr_range: Union[None, tuple] = None
        self.loc_precision_range: Union[None, tuple] = None

        # Parameter bounds
        self.enable_cfr_lower_threshold: bool = False
        self.enable_cfr_upper_threshold: bool = True

        # CFR thresholding parameters
        self.cfr_threshold_factor: float = 2.0

        # Weigh average localization by ECO
        self.weigh_avg_localization_by_eco: bool = False

        # Current parameter selection
        self.x_param: str = "x"
        self.y_param: str = "y"

        # Number of fluorophores in the sample
        self.num_fluorophores: int = 1
        self.dcr_bin_size: float = 0.0
        self.dcr_manual_threshold: float = 0.0

    def asdict(self) -> dict:
        """Return class as dictionary."""
        return {
            "min_num_loc_per_trace": self.min_num_loc_per_trace,
            "plot_average_localisations": self.plot_average_localisations,
            "color_code": str(ColorCode(self.color_code)),
            "efo_expected_frequency": self.efo_expected_frequency,
            "efo_thresholds": self.efo_thresholds,
            "cfr_thresholds": self.cfr_thresholds,
            "efo_range": self.efo_range,
            "cfr_range": self.cfr_range,
            "loc_precision_range": self.loc_precision_range,
            "enable_cfr_lower_threshold": self.enable_cfr_lower_threshold,
            "enable_cfr_upper_threshold": self.enable_cfr_upper_threshold,
            "cfr_threshold_factor": self.cfr_threshold_factor,
            "efo_bin_size_hz": self.efo_bin_size_hz,
            "weigh_avg_localization_by_eco": self.weigh_avg_localization_by_eco,
            "x_param": self.x_param,
            "y_param": self.y_param,
            "num_fluorophores": self.num_fluorophores,
            "dcr_bin_size": self.dcr_bin_size,
            "dcr_manual_threshold": self.dcr_manual_threshold,
        }

    def reset(self):
        """Reset to data-specific settings."""

        self.efo_thresholds = None
        self.cfr_thresholds = None

    def full_reset(self):
        """Reset to defaults."""

        self.min_num_loc_per_trace = 1
        self.plot_average_localisations = False
        self.color_code: ColorCode = ColorCode.NONE
        self.efo_expected_frequency = 0.0
        self.efo_thresholds = None
        self.cfr_thresholds = None
        self.efo_range = None
        self.cfr_range = None
        self.loc_precision_range = None
        self.enable_cfr_lower_threshold = False
        self.enable_cfr_upper_threshold = True
        self.cfr_threshold_factor = 2.0
        self.efo_bin_size_hz = 1000.0
        self.weigh_avg_localization_by_eco = False
        self.x_param = "x"
        self.y_param = "y"
        self.num_fluorophores = 1
        self.dcr_bin_size = 0.0
        self.dcr_manual_threshold = 0.0

    def __str__(self):
        """Human-readable representation."""
        self.__repr__()

    def __repr__(self):
        """State representation."""
        return "\n".join([f"{key}: {value}" for key, value in self.asdict().items()])
