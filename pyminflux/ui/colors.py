#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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
#  limitations under the License.

from enum import IntEnum
from typing import Optional, Union

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PySide6.QtGui import QBrush

from pyminflux.analysis import prepare_histogram
from pyminflux.base import Singleton


def reset_all_colors():
    """Reset all colors."""
    Colors().reset()
    ColorsToBrushes().reset()
    ColorsToRGB().reset()


class ColorCode(IntEnum):
    """Used to color-code dots in Plotter and Plotter3D."""

    NONE = 0
    BY_TID = 1
    BY_FLUO = 2
    BY_DEPTH = 3
    BY_TIME = 4


class ColorMap:

    @staticmethod
    def generate_jet_colormap(n_colors: int = 256) -> tuple[np.ndarray, np.ndarray]:
        """Create jet colormap with the requested number of colors.

        Parameters
        ----------

        n_colors: int
            Number of colors.

        Returns
        -------

        jet_colors_float: np.ndarray
            Colormap as an (n_colors, 3) array with floating-point values between 0.0 and 1.0.

        jet_colors: np.ndarray
            Colormap as an (n_colors, 3) array with integer values between 0 and 255.
        """

        if n_colors < 2:
            raise ValueError("The number of colors must be greater than or equal to 2.")

        # Define the transition points and corresponding color intensities for the jet colormap
        def interpolate(v, y0, x0, y1, x1):
            return (v - x0) * (y1 - y0) / (x1 - x0) + y0

        def base(v):
            if v <= -0.75:
                return 0
            elif v <= -0.25:
                return interpolate(v, 0.0, -0.75, 1.0, -0.25)
            elif v <= 0.25:
                return 1.0
            elif v <= 0.75:
                return interpolate(v, 1.0, 0.25, 0.0, 0.75)
            else:
                return 0.0

        # Define the red function
        def red(v):
            return base(v - 0.5)

        # Define the green function
        def green(v):
            return base(v)

        # Define the blue function
        def blue(v):
            return base(v + 0.5)

        # Generate the RGB colors
        colors_float = np.zeros((n_colors, 3))
        for i in range(n_colors):
            val = i / (n_colors - 1) * 2 - 1  # Normalize to range [-1, 1]
            colors_float[i, 0] = red(val)
            colors_float[i, 1] = green(val)
            colors_float[i, 2] = blue(val)

        # And now create a copy cast as integer
        colors = (255.0 * colors_float).astype(int)

        return colors_float, colors

    @staticmethod
    def generate_cividis_colormap(n_colors: int = 256) -> tuple[np.ndarray, np.ndarray]:
        """Create cividis colormap with the requested number of colors.

        Parameters
        ----------

        n_colors: int
            Number of colors.

        Returns
        -------

        cividis_colors_float: np.ndarray
            Colormap as an (n_colors, 3) array with floating-point values between 0.0 and 1.0.

        cividis_colors: np.ndarray
            Colormap as an (n_colors, 3) array with integer values between 0 and 255.
        """

        if n_colors < 2:
            raise ValueError("The number of colors must be greater than or equal to 2.")

        # The RGB values defining the Cividis colormap
        cividis_data = np.array(
            [
                [0.0, 0.135112, 0.304751],
                [0.03211, 0.201199, 0.440785],
                [0.208926, 0.272546, 0.424809],
                [0.309601, 0.340399, 0.42479],
                [0.401418, 0.41179, 0.440708],
                [0.488697, 0.485318, 0.471008],
                [0.582087, 0.55867, 0.468118],
                [0.68395, 0.638793, 0.444251],
                [0.785965, 0.720438, 0.399613],
                [0.896818, 0.81103, 0.320982],
                [0.995737, 0.909344, 0.217772],
            ]
        )

        # Interpolate the cividis colormap to n_steps
        indices = np.linspace(0, len(cividis_data) - 1, n_colors)
        colors_float = np.zeros((n_colors, 3))

        for i in range(3):  # For each color channel (R, G, B)
            colors_float[:, i] = np.interp(
                indices, np.arange(len(cividis_data)), cividis_data[:, i]
            )

        # And now create a copy cast as integer
        colors = (255.0 * colors_float).astype(int)

        return colors_float, colors

    @staticmethod
    def generate_plasma_colormap(n_colors: int = 256) -> tuple[np.ndarray, np.ndarray]:
        """Create plasma colormap with the requested number of colors.

        Parameters
        ----------

        n_colors: int
            Number of colors.

        Returns
        -------

        colors_float: np.ndarray
            Colormap as an (n_colors, 3) array with floating-point values between 0.0 and 1.0.

        colors: np.ndarray
            Colormap as an (n_colors, 3) array with integer values between 0 and 255.
        """

        if n_colors < 2:
            raise ValueError("The number of colors must be greater than or equal to 2.")

        # The RGB values defining the Plasma colormap
        plasma_data = np.array(
            [
                [5.03830e-02, 2.98030e-02, 5.27975e-01],
                [2.54627e-01, 1.38820e-02, 6.15419e-01],
                [4.17642e-01, 5.64000e-04, 6.58390e-01],
                [5.62738e-01, 5.15450e-02, 6.41509e-01],
                [6.92840e-01, 1.65141e-01, 5.64522e-01],
                [7.98216e-01, 2.80197e-01, 4.69538e-01],
                [8.81443e-01, 3.92529e-01, 3.83229e-01],
                [9.49217e-01, 5.17763e-01, 2.95662e-01],
                [9.88260e-01, 6.52325e-01, 2.11364e-01],
                [9.88648e-01, 8.09579e-01, 1.45357e-01],
                [9.40015e-01, 9.75158e-01, 1.31326e-01],
            ]
        )

        # Interpolate the cividis colormap to n_steps
        indices = np.linspace(0, len(plasma_data) - 1, n_colors)
        colors_float = np.zeros((n_colors, 3))

        for i in range(3):  # For each color channel (R, G, B)
            colors_float[:, i] = np.interp(
                indices, np.arange(len(plasma_data)), plasma_data[:, i]
            )

        # And now create a copy cast as integer
        colors = (255.0 * colors_float).astype(int)

        return colors_float, colors


class Colors(metaclass=Singleton):
    """Global color cache."""

    def __init__(self, fid_color_scheme: str = "green-magenta", seed: int = 42):
        """Constructor."""
        self._seed = seed

        # None
        self._white = np.array([255, 255, 255, 127], dtype=int)
        self._white_float = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)

        # TID
        self._unique_tid = None
        self._unique_tid_colors = None
        self._unique_tid_colors_float = None

        # FID
        self._fid_color_scheme = fid_color_scheme
        if self._fid_color_scheme == "blue-red":
            self._unique_fid_colors = np.array([[0, 0, 255], [255, 0, 0]], dtype=int)
        elif self._fid_color_scheme == "green-magenta":
            self._unique_fid_colors = np.array([[0, 255, 0], [255, 0, 255]], dtype=int)
        else:
            raise ValueError(f"Unknown color scheme '{self._fid_color_scheme}'.")
        self._unique_fid_colors_float = self._unique_fid_colors / 255.0

        # DEPTH
        self._unique_depth_colors = None
        self._unique_depth_colors_float = None

        # TIME
        self._unique_time_colors = None
        self._unique_time_colors_float = None

        # Initialize the random number generator
        self._rng = np.random.default_rng(self._seed)

    @property
    def unique_tid(self) -> Union[None, np.ndarray]:
        return self._unique_tid

    @property
    def unique_tid_colors(self) -> Union[None, np.ndarray]:
        return self._unique_tid_colors

    @property
    def unique_tid_colors_float(self) -> Union[None, np.ndarray]:
        return self._unique_tid_colors_float

    @property
    def unique_fid_colors(self) -> Union[None, np.ndarray]:
        return self._unique_fid_colors

    @property
    def unique_fid_colors_float(self) -> Union[None, np.ndarray]:
        return self._unique_fid_colors_float

    @property
    def unique_depth_colors(self) -> Union[None, np.ndarray]:
        return self._unique_depth_colors

    @property
    def unique_depth_colors_float(self) -> Union[None, np.ndarray]:
        return self._unique_depth_colors_float

    @property
    def unique_time_colors(self) -> Union[None, np.ndarray]:
        return self._unique_time_colors

    @property
    def unique_time_colors_float(self) -> Union[None, np.ndarray]:
        return self._unique_time_colors_float

    @property
    def white(self) -> np.ndarray:
        return self._white

    @property
    def white_float(self) -> np.ndarray:
        return self._white_float

    @property
    def tid_colors(self) -> Union[None, np.ndarray]:
        return self._unique_tid_colors

    @property
    def tid_colors_float(self) -> Union[None, np.ndarray]:
        return self._unique_tid_colors_float

    @property
    def fid_colors(self) -> np.ndarray:
        return self._unique_fid_colors

    @property
    def fid_colors_float(self) -> np.ndarray:
        return self._unique_fid_colors_float

    def reset(self):
        """Reset the color caches"""
        self._unique_tid = None
        self._unique_tid_colors = None
        self._unique_tid_colors_float = None
        self._unique_depth_colors = None
        self._unique_depth_colors_float = None
        self._unique_time_colors = None
        self._unique_time_colors_float = None

    def generate_tid_colors(self, tid: pd.Series):
        """Generate and cache TID colors.

        tid: pd.Series
            Identifiers to be used to assign colors.
        """

        # Reset the random number generator
        self._rng = np.random.default_rng(self._seed)

        # Generate unique colors for each identifier
        self._unique_tid = np.unique(tid)
        self._unique_tid_colors = self._rng.integers(
            256, size=(len(self._unique_tid), 3)
        )
        self._unique_tid_colors_float = self._unique_tid_colors / 255.0

    def generate_depth_colors(self, num_colors: int = 256):
        """Generate and cache depth colors.

        Parameters
        ----------

        num_colors: int = 256
            Number of colors to be generated for the colormap.
        """

        # Generate the colormap
        self._unique_depth_colors_float, self._unique_depth_colors = (
            ColorMap().generate_jet_colormap(num_colors)
        )

    def generate_time_colors(self, num_colors: int = 256):
        """Generate and cache depth colors.

        Parameters
        ----------

        num_colors: int = 256
            Number of colors to be generated for the colormap.
        """

        # Generate the colormap
        self._unique_time_colors_float, self._unique_time_colors = (
            ColorMap().generate_plasma_colormap(num_colors)
        )


class ColorsToBrushes(metaclass=Singleton):
    """Color manager (singleton class)."""

    def __init__(self):
        self._tid_brushes = None
        self._fid_brushes = None
        self._depth_brushes = None
        self._tid_to_brush_map = None
        self._fid_to_brush_map = None
        self._depth_to_brush_map = None
        self._depth_to_color_map = None
        self._depth_bin_edges = None
        self._time_to_brush_map = None
        self._time_to_color_map = None
        self._time_bin_edges = None
        self._last_tid = None
        self._last_fid = None
        self._last_depth = None
        self._last_time = None
        self._white_brush = pg.mkBrush(Colors().white)

        # Map each unique fid identifier to a unique QBrush
        self._fid_to_brush_map = {
            1: pg.mkBrush(Colors().unique_fid_colors[0]),
            2: pg.mkBrush(Colors().unique_fid_colors[1]),
        }

    def get_brushes(
        self,
        mode: ColorCode,
        tid: Optional[pd.Series] = None,
        fid: Optional[pd.Series] = None,
        depth: Optional[pd.Series] = None,
        time: Optional[pd.Series] = None,
    ) -> Union[QBrush, list[QBrush]]:
        """Get brushes for passed tid or fid arrays.

        Parameters
        ----------

        mode: ColorCode
            One of `ColorCode.NONE`, `ColorCode.BY_TID`, or `ColorCode.BY_FLUO`.

        tid: Optional[pd.Series] = None
            Array of trace IDs. If tid is not None, fid must be; depth and time must be None.

        fid: Optional[pd.Series] = None
            Array of fluorophore IDs.  If fid is not None, tid must be; depth and time must be None.

        depth: Optional[pd.Series] = None
            Array of depths (z values). fid, tid and time must be None.

        time: Optional[pd.Series] = None
            Array of time stamps. fid, tid and depth must be None.

        Returns
        -------

        brushes: Union[list[Qt.Brush], Qt.Brush]
            Either a single Qt.Brush, or a list.
        """

        # If mode is ColorCode.NONE, we just return the default white brush
        if mode == ColorCode.NONE:
            return self._white_brush

        elif mode == ColorCode.BY_TID:
            if tid is None:
                raise ValueError("If mode is ColorCode.BY_TID, `tid` cannot be None.")
            return self._get_or_create_brush_by_tid(tid)

        elif mode == ColorCode.BY_FLUO:
            if fid is None:
                raise ValueError("If mode is ColorCode.BY_FLUO, `fid` cannot be None.")
            return self._get_or_create_brush_by_fid(fid)

        elif mode == ColorCode.BY_DEPTH:
            if depth is None:
                raise ValueError(
                    "If mode is ColorCode.BY_DEPTH, `depth` cannot be None."
                )
            return self._get_or_create_brush_by_depth(depth)

        elif mode == ColorCode.BY_TIME:
            if time is None:
                raise ValueError("If mode is ColorCode.BY_TIME, `time` cannot be None.")
            return self._get_or_create_brush_by_time(time)

        else:
            raise ValueError(f"Unknown color mode: {mode}")

    def reset(self):
        """Reset the color caches."""
        self._tid_brushes = None
        self._fid_brushes = None
        self._depth_brushes = None
        self._tid_to_brush_map = None
        self._depth_to_brush_map = None
        self._depth_bin_edges = None
        self._time_to_brush_map = None
        self._time_bin_edges = None
        self._last_tid = None
        self._last_fid = None
        self._last_depth = None
        self._last_time = None

        # Map each unique fid identifier to a unique QBrush
        self._fid_to_brush_map = {
            1: pg.mkBrush(Colors().unique_fid_colors[0]),
            2: pg.mkBrush(Colors().unique_fid_colors[1]),
        }

    def _get_or_create_brush_by_tid(self, tid: pd.Series) -> list:
        """Create QBrush instances to be used in a ScatterPlotItem to prevent
        cache misses in SymbolAtlas.
        As an illustration, this speeds up the plotting of 200,000 dots with
        600 unique colors by ca. 20x.

        See explanation at PyQtGraph.graphicsItems.ScatterPlotItem._mkBrush()

        Parameters
        ----------

        tid: pd.Series
            Identifiers to be used to assign colors.

        Returns
        -------

        brushes: list[QBrush]
            List of brushes corresponding to the list of identifiers. Each identifier references
            a unique QBrush instance.
        """

        assert type(tid) == pd.Series, "`tid` must be a pd.Series."

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

    def _get_or_create_brush_by_fid(self, fid: pd.Series) -> list:
        """Create QBrush instances to be used in a ScatterPlotItem to prevent
        cache misses in SymbolAtlas.
        As an illustration, this speeds up the plotting of 200,000 dots with
        600 unique colors by ca. 20x.

        See explanation at PyQtGraph.graphicsItems.ScatterPlotItem._mkBrush()

        Parameters
        ----------

        fid: pd.Series
            Identifiers to be used to assign colors.

        Returns
        -------

        brushes: list[QBrush]
            List of brushes corresponding to the list of identifiers. Each identifier references
            a unique QBrush instance.
        """

        assert type(fid) == pd.Series, "`fid` must be a pd.Series."

        # Map each identifier in the full array to its corresponding QBrush for fast lookup
        if (
            self._last_fid is None
            or len(self._last_fid) != len(fid)
            or np.any(self._last_fid.index != fid.index)
            or np.any(self._last_fid.values != fid.values)
        ):
            self._fid_brushes = [
                self._fid_to_brush_map[identifier] for identifier in fid
            ]

        # Keep track of the passed tid
        self._last_fid = fid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._fid_brushes

    def _get_or_create_brush_by_depth(self, depth: pd.Series) -> list:
        """Create QBrush instances to be used in a ScatterPlotItem to prevent
        cache misses in SymbolAtlas.
        As an illustration, this speeds up the plotting of 200,000 dots with
        600 unique colors by ca. 20x.

        See explanation at PyQtGraph.graphicsItems.ScatterPlotItem._mkBrush()

        Parameters
        ----------

        depth: pd.Series
            Depths (z values) to be used to assign colors.

        Returns
        -------

        brushes: list[QBrush]
            List of brushes corresponding to the list of depth (z values) bins. Each identifier references
            a unique QBrush instance.
        """

        assert type(depth) == pd.Series, "`depth` must be a pd.Series."

        # Calculate current histogram bins
        _, current_depth_bin_edges, bin_centers, _ = prepare_histogram(
            depth.to_numpy(),
            auto_bins=True,
        )

        # Update what needs to be updated
        if (
            self._depth_bin_edges is None
            or self._depth_to_brush_map is None
            or not np.isin(current_depth_bin_edges, self._depth_bin_edges).all()
        ):
            # Generate unique colors for each brush (and identifier)
            Colors().generate_depth_colors(current_depth_bin_edges.shape[0])

            # Map each unique identifier to a unique QBrush, thus reducing
            # the number of QBrush object creations to the minimum
            unique_depth_colors = Colors().unique_depth_colors
            self._depth_to_brush_map = {
                i: pg.mkBrush(*unique_depth_colors[i])
                for i in range(len(current_depth_bin_edges))
            }

        # Map each identifier in the full array to its corresponding QBrush for fast lookup
        if (
            self._last_depth is None
            or len(self._last_depth) != len(depth)
            or np.any(self._last_depth.index != depth.index)
            or np.any(self._last_depth.values != depth.values)
        ):
            # Assign the depths to the corresponding bins
            depth_indices = np.digitize(depth, current_depth_bin_edges, right=True) - 1

            assert np.min(depth_indices) >= 0, "Minimum bin index is smaller than zero!"
            assert (
                np.max(depth_indices) <= len(current_depth_bin_edges) - 1
            ), "Maximum bin index is out of range!"

            self._depth_brushes = [
                self._depth_to_brush_map[index] for index in depth_indices
            ]

        # Keep track of the passed tid
        self._last_depth = depth

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._depth_brushes

    def _get_or_create_brush_by_time(self, time: pd.Series) -> list:
        """Create QBrush instances to be used in a ScatterPlotItem to prevent
        cache misses in SymbolAtlas.
        As an illustration, this speeds up the plotting of 200,000 dots with
        600 unique colors by ca. 20x.

        See explanation at PyQtGraph.graphicsItems.ScatterPlotItem._mkBrush()

        Parameters
        ----------

        time: pd.Series
            Delta times to be used to assign colors.

        Returns
        -------

        brushes: list[QBrush]
            List of brushes corresponding to the list of time bins. Each identifier references
            a unique QBrush instance.
        """

        assert type(time) == pd.Series, "`time` must be a pd.Series."

        # Calculate current histogram bins
        _, current_time_bin_edges, _, _ = prepare_histogram(
            time.to_numpy(),
            auto_bins=True,
        )

        # Update what needs to be updated
        if (
            self._time_bin_edges is None
            or self._time_to_brush_map is None
            or not np.isin(current_time_bin_edges, self._time_bin_edges).all()
        ):
            # Generate unique colors for each brush (and identifier)
            Colors().generate_time_colors(current_time_bin_edges.shape[0])

            # Map each unique identifier to a unique QBrush, thus reducing
            # the number of QBrush object creations to the minimum
            unique_time_colors = Colors().unique_time_colors
            self._time_to_brush_map = {
                i: pg.mkBrush(*unique_time_colors[i])
                for i in range(len(current_time_bin_edges))
            }

        # Map each identifier in the full array to its corresponding QBrush for fast lookup
        if (
            self._last_time is None
            or len(self._last_time) != len(time)
            or np.any(self._last_time.index != time.index)
            or np.any(self._last_time.values != time.values)
        ):
            # Assign the depths to the corresponding bins
            time_indices = np.digitize(time, current_time_bin_edges, right=True) - 1

            assert np.min(time_indices) >= 0, "Minimum bin index is smaller than zero!"
            assert (
                np.max(time_indices) <= len(current_time_bin_edges) - 1
            ), "Maximum bin index is out of range!"

            self._time_brushes = [
                self._time_to_brush_map[index] for index in time_indices
            ]

        # Keep track of the passed time vector
        self._last_time = time

        # Return the list of brushes (and references)
        return self._time_brushes


class ColorsToRGB(metaclass=Singleton):
    """Color manager (singleton class)."""

    def __init__(self):
        self._tid_colors = None
        self._fid_colors = None
        self._tid_to_color_map = None
        self._fid_to_color_map = None
        self._depth_to_color_map = None
        self._depth_bin_edges = None
        self._last_tid = None
        self._last_fid = None
        self._last_depth = None
        self._last_time = None
        self._time_bin_edges = None
        self._time_to_color_map = None
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
        depth: Optional[np.ndarray] = None,
        time: Optional[np.ndarray] = None,
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

        depth: Optional[np.ndarray] = None
            Array of depths (z values). fid, tid and time must be None.

        time: Optional[np.ndarray] = None
            Array of time stamps. fid, tid and depth must be None.

        Returns
        -------

        colors: np.ndarray
            RGBA colors for each of the tid or fid.
        """

        # If mode is ColorCode.NONE, we just return the default white color

        if mode == ColorCode.NONE:
            return Colors().white_float

        elif mode == ColorCode.BY_TID:
            if tid is None:
                raise ValueError("If mode is ColorCode.BY_TID, `tid` cannot be None.")
            return self._get_or_create_rgb_by_tid(tid)

        elif mode == ColorCode.BY_FLUO:
            if fid is None:
                raise ValueError("If mode is ColorCode.BY_FLUO, `fid` cannot be None.")
            return self._get_or_create_rgb_by_fid(fid)

        elif mode == ColorCode.BY_DEPTH:
            if depth is None:
                raise ValueError(
                    "If mode is ColorCode.BY_DEPTH, `depth` cannot be None."
                )
            return self._get_or_create_rgb_by_depth(depth)

        elif mode == ColorCode.BY_TIME:
            if time is None:
                raise ValueError("If mode is ColorCode.BY_TIME, `time` cannot be None.")
            return self._get_or_create_rgb_by_time(time)

        else:
            raise ValueError(f"Unknown color mode: {mode}")

    def reset(self):
        """Reset the color caches."""
        self._tid_colors = None
        self._tid_to_color_map = None
        self._depth_to_color_map = None
        self._depth_bin_edges = None
        self._last_tid = None
        self._last_fid = None
        self._last_depth = None
        self._last_time = None
        self._time_bin_edges = None
        self._time_to_color_map = None

    def _get_or_create_rgb_by_tid(self, tid: pd.Series) -> np.ndarray:
        """Create an Nx3 NumPy array of colors in the range [0.0 to 1.0].

        Parameters
        ----------

        tid: pd.Series
            Identifiers to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            Nx3 NumPy array of colors in the range [0.0 to 1.0] corresponding to the list of identifiers.
        """

        assert type(tid) == pd.Series, "`tid` must be a pd.Series."

        # Get the list of unique tid
        current_unique_tid = np.unique(tid)

        # Update what needs to be updated
        if (
            Colors().unique_tid is None
            or self._tid_to_color_map is None
            or not np.isin(current_unique_tid, Colors().unique_tid).all()
        ):
            # Generate unique colors for each brush (and identifier)
            Colors().generate_tid_colors(tid)

            # Map each unique identifier to a unique RGB color
            unique_tid_colors_float = Colors().unique_tid_colors_float
            self._tid_to_color_map = {
                uid: unique_tid_colors_float[i]
                for i, uid in enumerate(current_unique_tid)
            }

        if (
            self._last_tid is None
            or len(self._last_tid) != len(tid)
            or np.any(self._last_tid != tid)
        ):
            self._tid_colors = np.zeros((len(tid), 3), dtype=np.float32)
            for i, t in enumerate(tid):
                self._tid_colors[i] = self._tid_to_color_map[t]

        # Keep track of the passed tid
        self._last_tid = tid

        # Return the list of brushes (and references) and the mapping between id and brush
        return self._tid_colors

    def _get_or_create_rgb_by_fid(self, fid: pd.Series) -> np.ndarray:
        """Create an 2x3 NumPy array of colors in the range [0.0 to 1.0].

        Parameters
        ----------

        fid: pd.Series
            Identifiers to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            2x3 NumPy array of colors in the range [0.0 to 1.0] corresponding to the list of identifiers.
        """

        assert type(fid) == pd.Series, "`fid` must be a pd.Series."

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

    def _get_or_create_rgb_by_depth(self, depth: pd.Series) -> np.ndarray:
        """Create an Nx3 NumPy array of colors in the range [0.0 to 1.0].

        Parameters
        ----------

        depth: pd.Series
            Depths (z values) to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            Nx3 NumPy array of colors in the range [0.0 to 1.0] corresponding to the list of identifiers.
        """

        assert type(depth) == pd.Series, "`depth` must be a pd.Series."

        # Calculate current histogram bins
        _, current_depth_bin_edges, _, _ = prepare_histogram(
            depth,
            auto_bins=True,
        )

        # Update what needs to be updated
        if (
            self._depth_bin_edges is None
            or self._depth_to_color_map is None
            or not np.isin(current_depth_bin_edges, self._depth_bin_edges).all()
        ):
            # Generate unique colors for each brush (and identifier)
            Colors().generate_depth_colors(current_depth_bin_edges.shape[0])

            # Assign the depths to the corresponding bins
            depth_indices = np.digitize(depth, current_depth_bin_edges, right=True) - 1

            assert np.min(depth_indices) >= 0, "Minimum bin index is smaller than zero!"
            assert (
                np.max(depth_indices) <= len(current_depth_bin_edges) - 1
            ), "Maximum bin index is out of range!"

            self._depth_to_color_map = depth_indices

        if (
            self._last_depth is None
            or len(self._last_depth) != len(depth)
            or np.any(self._last_depth != depth)
        ):
            colors = Colors().unique_depth_colors_float
            depth_colors = [colors[index] for index in self._depth_to_color_map]
            self._depth_colors = np.array(depth_colors, dtype=np.float32)

        # Keep track of the passed depth
        self._last_depth = depth

        # Return the list of colors (and references)
        return self._depth_colors

    def _get_or_create_rgb_by_time(self, time: pd.Series) -> np.ndarray:
        """Create an Nx3 NumPy array of colors in the range [0.0 to 1.0].

        Parameters
        ----------

        time: pd.Series
            Delta times to be used to assign colors.

        Returns
        -------

        rgb: np.ndarray
            Nx3 NumPy array of colors in the range [0.0 to 1.0] corresponding to the list of identifiers.
        """

        assert type(time) == pd.Series, "`time` must be a pd.Series."

        # Calculate current histogram bins
        _, current_time_bin_edges, _, _ = prepare_histogram(
            time,
            auto_bins=True,
        )

        # Update what needs to be updated
        if (
            self._time_bin_edges is None
            or self._time_to_color_map is None
            or not np.isin(current_time_bin_edges, self._time_bin_edges).all()
        ):
            # Generate unique colors for each brush (and identifier)
            Colors().generate_time_colors(current_time_bin_edges.shape[0])

            # Assign the depths to the corresponding bins
            time_indices = np.digitize(time, current_time_bin_edges, right=True) - 1

            assert np.min(time_indices) >= 0, "Minimum bin index is smaller than zero!"
            assert (
                np.max(time_indices) <= len(current_time_bin_edges) - 1
            ), "Maximum bin index is out of range!"

            self._time_to_color_map = time_indices

        if (
            self._last_time is None
            or len(self._last_time) != len(time)
            or np.any(self._last_time != time)
        ):
            colors = Colors().unique_time_colors_float
            time_colors = [colors[index] for index in self._time_to_color_map]
            self._time_colors = np.array(time_colors, dtype=np.float32)

        # Keep track of the passed time vector
        self._last_time = time

        # Return the list of colors (and references)
        return self._time_colors
