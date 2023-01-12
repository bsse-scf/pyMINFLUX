from typing import Union

from ..base import Singleton


class State(metaclass=Singleton):
    """State machine (singleton class)."""

    __SLOTS__ = [
        "default_min_loc_per_trace",
        "min_num_loc_per_trace",
        "efo_thresholds",
        "cfr_thresholds",
        "enable_filter_efo",
        "enable_filter_cfr",
        "enable_efo_lower_threshold",
        "enable_efo_upper_threshold",
        "enable_cfr_lower_threshold",
        "enable_cfr_upper_threshold",
        "cfr_threshold_factor",
        "min_efo_relative_peak_prominence",
        "median_efo_filter_support",
    ]

    def __init__(self):
        """Constructor.

        A singleton object of this dataclass acts as a state machine that allows various parts of the
        application to synchronize state among them.
        """

        # Minimum number of localizations to consider a trace
        self.default_min_loc_per_trace: int = 1
        self.min_num_loc_per_trace: int = 1

        # Lower and upper (absolute) thresholds for the EFO and CFR values
        self.efo_thresholds: Union[None, tuple] = None
        self.cfr_thresholds: Union[None, tuple] = None

        # Flags for enabling disabling filtering using thresholds on EFO and CFR value (and global switch)
        self.enable_filter_efo: bool = False
        self.enable_filter_cfr: bool = False

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

    def asdict(self) -> dict:
        """Return class as dictionary."""
        return {
            "min_num_loc_per_trace": self.min_num_loc_per_trace,
            "efo_thresholds": self.efo_thresholds,
            "cfr_thresholds": self.cfr_thresholds,
            "enable_filter_efo": self.enable_filter_efo,
            "enable_filter_cfr": self.enable_filter_cfr,
            "enable_efo_lower_threshold": self.enable_efo_lower_threshold,
            "enable_efo_upper_threshold": self.enable_efo_upper_threshold,
            "enable_cfr_lower_threshold": self.enable_cfr_lower_threshold,
            "enable_cfr_upper_threshold": self.enable_cfr_upper_threshold,
            "min_efo_relative_peak_prominence": self.min_efo_relative_peak_prominence,
            "median_efo_filter_support": self.median_efo_filter_support,
            "cfr_threshold_factor": self.cfr_threshold_factor
        }

    def reset(self):
        """Reset to data-specific settings."""

        self.efo_thresholds = None
        self.cfr_thresholds = None

    def full_reset(self):
        """Reset to defaults."""

        self.min_num_loc_per_trace = 1
        self.efo_thresholds = None
        self.cfr_thresholds = None
        self.enable_filter_efo = False
        self.enable_filter_cfr = False
        self.enable_efo_lower_threshold = False
        self.enable_efo_upper_threshold = True
        self.enable_cfr_lower_threshold = False
        self.enable_cfr_upper_threshold = True
        self.min_efo_relative_peak_prominence = 0.01
        self.median_efo_filter_support = 5
        self.cfr_threshold_factor = 2.0
