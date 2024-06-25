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
    """Global color cache."""

    def __init__(self, fid_color_scheme: str = "green-magenta", seed: int = 42):
        """Constructor."""
        self._seed = seed
        self._fid_color_scheme = fid_color_scheme
        self._white = np.array([255, 255, 255, 127], dtype=int)
        self._white_float = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self._unique_tid = None
        self._unique_tid_colors = None
        self._unique_tid_colors_float = None
        if self._fid_color_scheme == "blue-red":
            self._unique_fid_colors = np.array([[0, 0, 255], [255, 0, 0]], dtype=int)
        elif self._fid_color_scheme == "green-magenta":
            self._unique_fid_colors = np.array([[0, 255, 0], [255, 0, 255]], dtype=int)
        else:
            raise ValueError(f"Unknown color scheme '{self._fid_color_scheme}'.")
        self._unique_fid_colors_float = self._unique_fid_colors / 255.0

        # Initialize the random number generator
        self._rng = np.random.default_rng(self._seed)

    @property
    def unique_tid(self) -> np.ndarray:
        return self._unique_tid

    @property
    def unique_tid_colors(self):
        return self._unique_tid_colors

    @property
    def unique_tid_colors_float(self):
        return self._unique_tid_colors_float

    @property
    def unique_fid_colors(self):
        return self._unique_fid_colors

    @property
    def unique_fid_colors_float(self):
        return self._unique_fid_colors_float

    @property
    def white(self) -> np.ndarray:
        return self._white

    @property
    def white_float(self) -> np.ndarray:
        return self._white_float

    @property
    def tid_colors(self) -> np.ndarray:
        return self._unique_tid_colors

    @property
    def tid_colors_float(self) -> np.ndarray:
        return self._unique_tid_colors_float

    @property
    def fid_colors(self) -> np.ndarray:
        return self._unique_fid_colors

    @property
    def fid_colors_float(self) -> np.ndarray:
        return self._unique_fid_colors_float

    def reset(self):
        """Reset the color caches: only the TID caches need to be reset."""
        self._unique_tid_colors = None
        self._unique_tid_colors_float = None

    def generate_tid_colors(self, tid: np.ndarray):
        """Generate and cache TID colors."""

        # Reset the random number generator
        self._rng = np.random.default_rng(self._seed)

        # Generate unique colors for each identifier
        self._unique_tid = np.unique(tid)
        self._unique_tid_colors = self._rng.integers(
            256, size=(len(self._unique_tid), 3)
        )
        self._unique_tid_colors_float = self._unique_tid_colors / 255.0


class ColorsToBrushes(metaclass=Singleton):
    """Color manager (singleton class)."""

    def __init__(self):
        self._tid_brushes = None
        self._fid_brushes = None
        self._tid_to_brush_map = None
        self._fid_to_brush_map = None
        self._last_tid = None
        self._last_fid = None
        self._white_brush = pg.mkBrush(Colors().white)

        # Map each unique fid identifier to a unique QBrush
        self._fid_to_brush_map = {
            1: pg.mkBrush(Colors().unique_fid_colors[0]),
            2: pg.mkBrush(Colors().unique_fid_colors[1]),
        }

    def get_brushes(
        self,
        mode: ColorCode,
        tid: Optional[np.ndarray] = None,
        fid: Optional[np.ndarray] = None,
    ) -> Union[QBrush, list[QBrush]]:
        """Get brushes for passed tid or fid arrays.

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

    def reset(self):
        """Reset the color caches."""
        self._tid_brushes = None
        self._fid_brushes = None
        self._tid_to_brush_map = None
        self._fid_to_brush_map = None
        self._last_tid = None
        self._last_fid = None

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
        if (
            Colors().unique_tid is None
            or self._tid_to_brush_map is None
            or not np.isin(current_unique_tid, Colors().unique_tid).all()
        ):

            # Generate unique colors for each brush (and identifier)
            Colors().generate_tid_colors(tid)

            # Map each unique identifier to a unique QBrush, thus reducing
            # the number of QBrush object creations to the minimum
            unique_tid_colors = Colors().unique_tid_colors
            self._tid_to_brush_map = {
                uid: pg.mkBrush(*unique_tid_colors[i])
                for i, uid in enumerate(current_unique_tid)
            }

        # Map each identifier in the full array to its corresponding QBrush for fast lookup
        if (
            self._last_tid is None
            or len(self._last_tid) != len(tid)
            or np.any(self._last_tid != tid)
        ):
            self._tid_brushes = [
                self._tid_to_brush_map[identifier] for identifier in tid
            ]

        # Keep track of the passed tid
        self._last_tid = tid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._tid_brushes

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

        # Map each identifier in the full array to its corresponding QBrush for fast lookup
        if (
            self._last_fid is None
            or len(self._last_fid) != len(fid)
            or np.any(self._last_fid != fid)
        ):
            self._fid_brushes = [
                self._fid_to_brush_map[identifier] for identifier in fid
            ]

        # Keep track of the passed tid
        self._last_fid = fid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._fid_brushes


class ColorsToRGB(metaclass=Singleton):
    """Color manager (singleton class)."""

    def __init__(self):
        self._tid_colors = None
        self._fid_colors = None
        self._tid_to_color_map = None
        self._fid_to_color_map = None
        self._last_tid = None
        self._last_fid = None
        self._white_color = Colors().white_float

        # Map each unique identifier to a unique RGB color
        self._fid_to_color_map = {
            1: Colors().unique_fid_colors_float[0],
            2: Colors().unique_fid_colors_float[1],
        }

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

        colors: np.ndarray
            RGBA colors for each of the tid or fid.
        """

        # If mode is ColorCode.NONE, we just return the default white color
        if mode == ColorCode.NONE:
            return Colors().white_float

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
        self._tid_colors = None
        self._fid_colors = None
        self._tid_to_color_map = None
        self._fid_to_color_map = None
        self._last_tid = None
        self._last_fid = None

    def _get_or_create_rgb_by_tid(self, tid) -> np.ndarray:
        """Create an Nx3 NumPy array of colors in the range [0.0 to 1.0].

        Parameters
        ----------

        tid: np.ndarray
            Identifiers to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            Nx3 NumPy array of colors in the range [0.0 to 1.0] corresponding to the list of identifiers.
        """

        # Get the list of unique tid
        current_unique_tid = np.unique(tid)

        # Update what needs to be updated
        if (
            Colors().unique_tid is None
            or not np.isin(current_unique_tid, Colors().unique_tid).all()
        ):

            # Generate unique colors for each brush (and identifier)
            Colors().generate_tid_colors(tid)

        # Map each unique identifier to a unique RGB color
        if (
            self._last_tid is None
            or len(self._last_tid) != len(tid)
            or np.any(self._last_tid != tid)
        ):
            unique_tid_colors_float = Colors().unique_tid_colors_float
            self._tid_colors = np.zeros((len(tid), 3), dtype=np.float32)
            self._tid_to_color_map = {
                tid: unique_tid_colors_float[i]
                for i, tid in enumerate(current_unique_tid)
            }
            for i, t in enumerate(tid):
                self._tid_colors[i] = self._tid_to_color_map[t]

        # Keep track of the passed tid
        self._last_tid = tid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._tid_colors

    def _get_or_create_rgb_by_fid(self, fid) -> np.ndarray:
        """Create an 2x3 NumPy array of colors in the range [0.0 to 1.0].

        Parameters
        ----------

        fid: np.ndarray
            Identifiers to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            2x3 NumPy array of colors in the range [0.0 to 1.0] corresponding to the list of identifiers.
        """

        # Map each identifier in the full array to its corresponding QBrush for fast lookup
        if (
            self._last_fid is None
            or len(self._last_fid) != len(fid)
            or np.any(self._last_fid != fid)
        ):
            self._fid_colors = [
                self._fid_to_color_map[identifier] for identifier in fid
            ]

        # Keep track of the passed tid
        self._last_fid = fid

        # Return the list of brushes (and references) and the mapping between id and brush
        return np.array(self._fid_colors)
