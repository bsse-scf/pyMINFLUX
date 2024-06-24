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
        self._tid_to_rgb = None
        self._fid_to_rgb = None
        self._single_tid_to_brush_map = None
        self._single_fid_to_brush_map = None
        self._last_tid = np.array([])
        self._last_fid = np.array([])
        self._last_unique_tid = np.array([])
        self._last_unique_fid = np.array([])
        self._fid_color_scheme = fid_color_scheme
        self._tid_unique_colors = None
        self._fid_unique_colors = None
        self._tid_unique_colors_float = None
        self._fid_unique_colors_float = None
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

    def get_rgb(
        self,
        mode: ColorCode,
        tid: Optional[np.ndarray] = None,
        fid: Optional[np.ndarray] = None,
    ):
        """Get RGB colors for passed tid or fid.

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

        # If mode is ColorCode.NONE, we just return the default white color
        if mode == ColorCode.NONE:
            return np.array([1.0, 1.0, 1.0])

        # Only one of tid and fid can be passed
        if tid is None and fid is None:
            raise ValueError("Please specify one of `tid` or `fid`.")

        if (tid is None and fid is not None) or (tid is not None and fid is None):
            raise ValueError("Please specify only one of `tid` or `fid`.")

        if mode == ColorCode.BY_TID and tid is not None:
            return self._get_or_create_rgb_by_tid(tid)

        if mode == ColorCode.BY_FLUO and fid is not None:
            return self._get_or_create_rgb_by_fid(fid)

        raise ValueError(f"Unknown color mode: {mode}")

    def reset(self):
        """Reset the color caches."""
        self._tid_to_brushes = None
        self._fid_to_brushes = None
        self._tid_to_rgb = None
        self._fid_to_rgb = None
        self._single_tid_to_brush_map = None
        self._single_fid_to_brush_map = None
        self._last_tid = np.array([])
        self._last_fid = np.array([])
        self._last_unique_tid = np.array([])
        self._last_unique_fid = np.array([])
        self._tid_unique_colors = None
        self._tid_unique_colors_float = None
        self._fid_unique_colors = None
        self._fid_unique_colors_float = None

    def _generate_unique_tid_colors(self, tid):
        """Create tid colors.

        Parameters
        ----------

        tid: np.ndarray
            Identifiers to be used to assign colors.
        """

        # Reset the random number generator
        self._rng = np.random.default_rng(self._seed)

        # Generate unique colors for each brush (and identifier)
        self._last_unique_tid = np.unique(tid)
        self._tid_unique_colors = self._rng.integers(
            256, size=(len(self._last_unique_tid), 3)
        )
        self._tid_unique_colors_float = self._tid_unique_colors / 255.0

    def _generate_unique_fid_colors(self):
        """Create fid colors."""

        if self._fid_color_scheme == "blue-red":
            self._fid_unique_colors = np.array([[0, 0, 255], [255, 0, 0]])
        elif self._fid_color_scheme == "green-magenta":
            self._fid_unique_colors = np.array([[0, 255, 0], [255, 0, 255]])
        else:
            raise ValueError(f"Unknown color scheme '{self._fid_color_scheme}'.")

        self._fid_unique_colors_float = self._fid_unique_colors / 255.0

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
            self._last_unique_tid
        ):

            # Generate unique colors for each brush (and identifier)
            self._generate_unique_tid_colors(tid)

            # Map each unique identifier to a unique QBrush, thus reducing
            # the number of QBrush object creations to the minimum
            self._single_tid_to_brush_map = {
                uid: pg.mkBrush(*self._tid_unique_colors[i])
                for i, uid in enumerate(current_unique_tid)
            }

        if (
            self._tid_to_brushes is None
            or len(self._last_tid) != len(tid)
            or np.any(self._last_tid != tid)
        ):
            # Map each identifier in the full array to its corresponding QBrush for fast lookup
            self._tid_to_brushes = [
                self._single_tid_to_brush_map[identifier] for identifier in tid
            ]

        # Keep track of the passed tid
        self._last_tid = tid
        self._last_unique_tid = current_unique_tid

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
            self._last_unique_fid
        ):

            # Initialize colors for the fid_color_scheme
            self._generate_unique_fid_colors()

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
        self._last_unique_fid = current_unique_fid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._fid_to_brushes

    def _get_or_create_rgb_by_tid(self, tid) -> np.ndarray:
        """Create an Nx3 NumPy array of colors in the range [0.0 to 1.0] that correspond to the
        brushes returned by `_get_or_create_brush_by_tid()`.

        Parameters
        ----------

        tid: np.ndarray
            Identifiers to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            Nx3 NumPy array of colors in the range [0.0 to 1.0].
        """

        # Get the list of unique tid
        current_unique_tid = np.unique(tid)

        # Update what needs to be updated
        if self._tid_unique_colors_float is None or len(current_unique_tid) > len(
            self._last_unique_tid
        ):

            # Generate unique colors for each brush (and identifier)
            self._generate_unique_tid_colors(tid)

        if (
            self._tid_to_rgb is None
            or len(self._last_tid) != len(tid)
            or np.any(self._last_tid != tid)
        ):
            # Map each unique identifier to a unique RGB color
            self._tid_to_rgb = np.zeros((len(tid), 3), dtype=np.float32)
            tid_to_color = {
                tid: self._tid_unique_colors_float[i]
                for i, tid in enumerate(current_unique_tid)
            }
            for i, t in enumerate(tid):
                self._tid_to_rgb[i] = tid_to_color[t]

        # Keep track of the passed tid
        self._last_tid = tid
        self._last_unique_tid = current_unique_tid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._tid_to_rgb

    def _get_or_create_rgb_by_fid(self, fid) -> np.ndarray:
        """Create an 2x3 NumPy array of colors in the range [0.0 to 1.0] that correspond to the
        brushes returned by `_get_or_create_brush_by_tid()`.

        Parameters
        ----------

        fid: np.ndarray
            Identifiers to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            2x3 NumPy array of colors in the range [0.0 to 1.0].
        """

        # Get the list of unique tid
        current_unique_fid = np.unique(fid)

        # Update what needs to be updated
        if self._fid_unique_colors_float is None or len(current_unique_fid) > len(
            self._last_unique_fid
        ):

            # Generate unique colors for each brush (and identifier)
            self._generate_unique_fid_colors()

        if (
            self._fid_to_rgb is None
            or len(self._last_fid) != len(fid)
            or np.any(self._last_fid != fid)
        ):
            # Map each unique identifier to a unique RGB color
            self._fid_to_rgb = np.zeros((len(fid), 3), dtype=np.float32)
            fid_to_color = {
                fid: self._fid_unique_colors_float[i]
                for i, fid in enumerate(current_unique_fid)
            }
            for i, f in enumerate(fid):
                self._fid_to_rgb[i] = fid_to_color[f]

        # Keep track of the passed fid
        self._last_fid = fid
        self._last_unique_fid = current_unique_fid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._fid_to_rgb
