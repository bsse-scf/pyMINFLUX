from typing import Union

from ..base import Singleton


class State(metaclass=Singleton):
    """State machine (singleton class)."""

    def __init__(self):
        """Constructor.

        A sigleton object of this dataclass acts as a state machine that allows various parts of the
        application to synchronize state among them.
        """

        # Lower and upper (absolute) thresholds for the EFO and CFR values
        self.efo_thresholds: Union[None, tuple] = None
        self.cfr_thresholds: Union[None, tuple] = None

        # Flags for enabling disabling filtering using thresholds on EFO and CFR value (and global switch)
        self.filter: bool = False
        self.filter_efo: bool = False
        self.filter_cfr: bool = False

        # Multiplicative factor for the robust threshold
        self.filter_thresh_factor: float = 2.0

    def asdict(self) -> dict:
        """Return class as dictionary."""
        return {
            "efo_thresholds": self.efo_thresholds,
            "cfr_thresholds": self.cfr_thresholds,
            "filter": self.filter,
            "filter_efo": self.filter_efo,
            "filter_cfr": self.filter_cfr,
            "filter_thresh_factor": self.filter_thresh_factor,
        }
