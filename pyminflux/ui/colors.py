from enum import IntEnum
from typing import Optional, Union

import numpy as np
import pyqtgraph as pg
from PySide6.QtGui import QBrush

from pyminflux.base import Singleton


class ColorCode(IntEnum):
    """Used to color-code dots in Plotter and Plotter3D."""

    NONE = 0
    BY_TID = 1
    BY_FLUO = 2


class Colors(metaclass=Singleton):
    """Color manager (singleton class)."""

    def __init__(self, fid_color_scheme: str = "green-magenta", seed: int = 42):
        self._tid_to_brushes = None
        self._fid_to_brushes = None
        self._single_tid_to_brush_map = None
        self._single_fid_to_brush_map = None
        self._last_tid = np.array([])
        self._last_fid = np.array([])
        self._unique_tid = np.array([])
        self._unique_fid = np.array([])
        self._fid_color_scheme = fid_color_scheme
        self._tid_unique_colors = None
        self._fid_unique_colors = None
        self._seed = seed
        self._white_brush = pg.mkBrush(255, 255, 255, 128)

        # Initialize the random number generator
        self._rng = np.random.default_rng(self._seed)

    def get_brushes(
        self,
        mode: ColorCode,
        tid: Optional[np.ndarray] = None,
        fid: Optional[np.ndarray] = None,
    ) -> Union[QBrush, list[QBrush]]:
        """Get brushes for passed tid or fid.

        Parameters
        ----------

        mode: ColorCode
            One of `ColorCode.NONE`, `ColorCode.BY_TID`, or `ColorCode.BY_FLUO`.

        tid: Optional[np.ndarray] = None
            Array of trace IDs. If tid is not None, fid must be.

        fid: Optional[np.ndarray] = None
            Array of fluorophore IDs.  If fid is not None, tid must be.

        Returns
        -------

        brushes: Union[list[Qt.Brush], Qt.Brush]
            Either a single Qt.Brush, or a list.
        """

        # If mode is ColorCode.NONE, we just return the default white brush
        if mode == ColorCode.NONE:
            return self._white_brush

        # Only one of tid and fid can be passed
        if tid is None and fid is None:
            raise ValueError("Please specify one of `tid` or `fid`.")

        if (tid is None and fid is not None) or (tid is not None and fid is None):
            raise ValueError("Please specify only one of `tid` or `fid`.")

        if mode == ColorCode.BY_TID and tid is not None:
            return self._get_or_create_brush_by_tid(tid)

        if mode == ColorCode.BY_FLUO and fid is not None:
            return self._get_or_create_brush_by_fid(fid)

        raise ValueError(f"Unknown color mode: {mode}")

    def _get_or_create_brush_by_tid(self, tid: np.ndarray) -> list:
        """Create QBrush instances to be used in a ScatterPlotItem to prevent
        cache misses in SymbolAtlas.
        As an illustration, this speeds up the plotting of 200,000 dots with
        600 unique colors by ca. 20x.

        See explanation at PyQtGraph.graphicsItems.ScatterPlotItem._mkBrush()

        Parameters
        ----------

        tid: np.ndarray
            Identifiers to be used to assign colors.

        Returns
        -------

        brushes: list[QBrush]
            List of brushes corresponding to the list of identifiers. Each identifier references
            a unique QBrush instance.
        """

        # Get the list of unique tid
        current_unique_tid = np.unique(tid)

        # Update what needs to be updated
        if self._tid_unique_colors is None or len(current_unique_tid) > len(
            self._unique_tid
        ):

            # Reset the random number genetator
            self._rng = np.random.default_rng(self._seed)

            # Generate unique colors for each brush (and identifier)
            self._tid_unique_colors = self._rng.integers(
                256, size=(len(current_unique_tid), 3)
            )

            # Map each unique identifier to a unique QBrush, thus reducing
            # the number of QBrush object creations to the minimum
            self._single_tid_to_brush_map = {
                uid: pg.mkBrush(*self._tid_unique_colors[i])
                for i, uid in enumerate(current_unique_tid)
            }

        if len(self._last_tid) != len(tid) or np.any(self._last_tid != tid):
            # Map each identifier in the full array to its corresponding QBrush for fast lookup
            self._tid_to_brushes = [
                self._single_tid_to_brush_map[identifier] for identifier in tid
            ]

        # Keep track of the passed tid
        self._last_tid = tid
        self._unique_tid = current_unique_tid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._tid_to_brushes

    def _get_or_create_brush_by_fid(self, fid: np.ndarray) -> list:
        """Create QBrush instances to be used in a ScatterPlotItem to prevent
        cache misses in SymbolAtlas.
        As an illustration, this speeds up the plotting of 200,000 dots with
        600 unique colors by ca. 20x.

        See explanation at PyQtGraph.graphicsItems.ScatterPlotItem._mkBrush()

        Parameters
        ----------

        fid: np.ndarray
            Identifiers to be used to assign colors.

        Returns
        -------

        brushes: list[QBrush]
            List of brushes corresponding to the list of identifiers. Each identifier references
            a unique QBrush instance.
        """

        # Get the list of unique fid
        current_unique_fid = np.unique(fid)

        # Update what needs to be updated
        if self._fid_unique_colors is None or len(current_unique_fid) > len(
            self._unique_fid
        ):

            # Initialize colors for the fid_color_scheme
            if self._fid_color_scheme == "blue-red":
                self._fid_unique_colors = [[0, 0, 255], [255, 0, 0]]
            elif self._fid_color_scheme == "green-magenta":
                self._fid_unique_colors = [[0, 255, 0], [255, 0, 255]]
            else:
                raise ValueError(f"Unknown color scheme '{self._fid_color_scheme}'.")

            # Map each unique identifier to a unique QBrush, thus reducing
            # the number of QBrush object creations to the minimum
            self._single_fid_to_brush_map = {
                uid: pg.mkBrush(*self._fid_unique_colors[i])
                for i, uid in enumerate(current_unique_fid)
            }

        if len(self._last_fid) != len(fid) or np.any(self._last_fid != fid):
            # Map each identifier in the full array to its corresponding QBrush for fast lookup
            self._fid_to_brushes = [
                self._single_fid_to_brush_map[identifier] for identifier in fid
            ]

        # Keep track of the passed fid
        self._last_fid = fid
        self._unique_fid = current_unique_fid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._fid_to_brushes
