from dataclasses import dataclass

from ..base import Singleton


@dataclass
class State(metaclass=Singleton):
    """State machine (singleton class)."""

    def __init__(self):
        """Constructor.

        A sigleton object of this dataclass acts as a state machine that allows various parts of the
        application to synchronize state among them.
        """
        self.efo_low_threshold: float = 0.0
        self.efo_high_threshold: float = 0.0
        self.cfr_low_threshold: float = 0.0
        self.cfr_high_threshold: float = 0.0
