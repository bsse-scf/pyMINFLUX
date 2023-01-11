from typing import Union

from ..base import Singleton


class State(metaclass=Singleton):
    """State machine (singleton class)."""

    def __init__(self):
        """Constructor.

        A sigleton object of this dataclass acts as a state machine that allows various parts of the
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

        # Robust threshold bounds
        self.enable_lower_threshold: bool = False
        self.enable_upper_threshold: bool = True

        # Peak detector parameters
        self.min_relative_peak_prominence: float = 0.01
        self.median_filter_support: int = 5

    def asdict(self) -> dict:
        """Return class as dictionary."""
        return {
            "min_num_loc_per_trace": self.min_num_loc_per_trace,
            "efo_thresholds": self.efo_thresholds,
            "cfr_thresholds": self.cfr_thresholds,
            "enable_filter_efo": self.enable_filter_efo,
            "enable_filter_cfr": self.enable_filter_cfr,
            "enable_lower_bound": self.enable_lower_threshold,
            "enable_upper_bound": self.enable_upper_threshold,
            "min_relative_peak_prominence": self.min_relative_peak_prominence,
            "median_filter_support": self.median_filter_support,
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
        self.enable_lower_threshold = False
        self.enable_upper_threshold = True
        self.min_relative_peak_prominence = 0.01
        self.median_filter_support = 5
