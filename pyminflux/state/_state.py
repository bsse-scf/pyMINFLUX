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
        "dwell_time_threshold",
        "dwell_time_larger_than_threshold",
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
        self.default_min_loc_per_trace: int = 1
        self.min_num_loc_per_trace: int = 1

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

        # EFO GMM fitting number of clusters
        self.gmm_efo_num_clusters: int = 3
        self.gmm_efo_use_bayesian: bool = False
        self.gmm_include_cfr: bool = False

        # EFO peak detector parameters
        self.min_efo_relative_peak_prominence: float = 0.01
        self.median_efo_filter_support: int = 5

        # Dwell time thresholding
        self.dwell_time_threshold: float = 0.0
        self.dwell_time_larger_than_threshold: bool = True

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
            "gmm_efo_num_clusters": self.gmm_efo_num_clusters,
            "gmm_efo_use_bayesian": self.gmm_efo_use_bayesian,
            "gmm_include_cfr": self.gmm_include_cfr,
            "min_efo_relative_peak_prominence": self.min_efo_relative_peak_prominence,
            "median_efo_filter_support": self.median_efo_filter_support,
            "cfr_threshold_factor": self.cfr_threshold_factor,
            "self.dwell_time_threshold": self.dwell_time_threshold,
            "self.dwell_time_larger_than_threshold": self.dwell_time_larger_than_threshold,
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
        self.gmm_efo_num_clusters = 3
        self.gmm_efo_use_bayesian = False
        self.gmm_include_cfr = False
        self.median_efo_filter_support = 5
        self.cfr_threshold_factor = 2.0
        self.dwell_time_threshold: float = 0.0
        self.dwell_time_larger_than_threshold: bool = True
