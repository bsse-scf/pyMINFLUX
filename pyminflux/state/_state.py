from pprint import pprint
from typing import Union

from ..base import Singleton


class State(metaclass=Singleton):
    """State machine (singleton class)."""

    __SLOTS__ = [
        "plot_average_localisations",
        "color_code_locs_by_tid",
        "default_min_loc_per_trace",
        "min_num_loc_per_trace",
        "efo_thresholds",
        "cfr_thresholds",
        "enable_efo_lower_threshold",
        "enable_efo_upper_threshold",
        "enable_cfr_lower_threshold",
        "enable_cfr_upper_threshold",
        "cfr_threshold_factor",
        "gmm_efo_num_clusters",
        "gmm_efo_use_bayesian",
        "gmm_include_cfr",
        "min_efo_relative_peak_prominence",
        "median_efo_filter_support",
        "efo_bin_size_hz",
        "dwell_time_threshold",
        "dwell_time_smaller_than_threshold",
        "weigh_avg_localization_by_eco",
        "x_param",
        "y_param",
        "num_fluorophores",
        "dcr_bin_size",
    ]

    def __init__(self):
        """Constructor.

        A singleton object of this dataclass acts as a state machine that allows various parts of the
        application to synchronize state among them.
        """

        # Plotting options
        self.plot_average_localisations: bool = False
        self.color_code_locs_by_tid: bool = False

        # Minimum number of localizations to consider a trace
        self.min_num_loc_per_trace: int = 1

        # EFO bin size in Hz (if 0.0, the bin size will be automatically estimated)
        self.efo_bin_size_hz: float = 0.0

        # Lower and upper (absolute) thresholds for the EFO and CFR values
        self.efo_thresholds: Union[None, tuple] = None
        self.cfr_thresholds: Union[None, tuple] = None

        # Parameter bounds
        self.enable_efo_lower_threshold: bool = False
        self.enable_efo_upper_threshold: bool = True
        self.enable_cfr_lower_threshold: bool = False
        self.enable_cfr_upper_threshold: bool = True

        # CFR thresholding parameters
        self.cfr_threshold_factor: float = 2.0

        # EFO peak detector parameters
        self.min_efo_relative_peak_prominence: float = 0.01
        self.median_efo_filter_support: int = 5

        # EFO bin size in Hz
        self.efo_bin_size_hz: float = 0.0

        # Weigh average localization by ECO
        self.weigh_avg_localization_by_eco: bool = False

        # Current parameter selection
        self.x_param: str = "x"
        self.y_param: str = "y"

        # Number of fluorophores in the sample
        self.num_fluorophores: int = 1
        self.dcr_bin_size: float = 0.0

    def asdict(self) -> dict:
        """Return class as dictionary."""
        return {
            "min_num_loc_per_trace": self.min_num_loc_per_trace,
            "plot_average_localisations": self.plot_average_localisations,
            "color_code_locs_by_tid": self.color_code_locs_by_tid,
            "efo_thresholds": self.efo_thresholds,
            "cfr_thresholds": self.cfr_thresholds,
            "enable_efo_lower_threshold": self.enable_efo_lower_threshold,
            "enable_efo_upper_threshold": self.enable_efo_upper_threshold,
            "enable_cfr_lower_threshold": self.enable_cfr_lower_threshold,
            "enable_cfr_upper_threshold": self.enable_cfr_upper_threshold,
            "min_efo_relative_peak_prominence": self.min_efo_relative_peak_prominence,
            "median_efo_filter_support": self.median_efo_filter_support,
            "cfr_threshold_factor": self.cfr_threshold_factor,
            "efo_bin_size_hz": self.efo_bin_size_hz,
            "weigh_avg_localization_by_eco": self.weigh_avg_localization_by_eco,
            "x_param": self.x_param,
            "y_param": self.y_param,
            "num_fluorophores": self.num_fluorophores,
            "dcr_bin_size": self.dcr_bin_size,
        }

    def reset(self):
        """Reset to data-specific settings."""

        self.efo_thresholds = None
        self.cfr_thresholds = None

    def full_reset(self):
        """Reset to defaults."""

        self.min_num_loc_per_trace = 1
        self.plot_average_localisations = False
        self.color_code_locs_by_tid = False
        self.efo_thresholds = None
        self.cfr_thresholds = None
        self.enable_efo_lower_threshold = False
        self.enable_efo_upper_threshold = True
        self.enable_cfr_lower_threshold = False
        self.enable_cfr_upper_threshold = True
        self.min_efo_relative_peak_prominence = 0.01
        self.median_efo_filter_support = 5
        self.cfr_threshold_factor = 2.0
        self.efo_bin_size_hz = 0.0
        self.weigh_avg_localization_by_eco = False
        self.x_param = "x"
        self.y_param = "y"
        self.num_fluorophores = 1
        self.dcr_bin_size = 0.0

    def __str__(self):
        """Human-readable representation."""
        self.__repr__()

    def __repr__(self):
        """State representation."""
        return "\n".join([f"{key}: {value}" for key, value in self.asdict().items()])
