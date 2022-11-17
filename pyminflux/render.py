from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection



from typing import Union

import numpy as np
import pandas as pd


def get_colors_for_unique_ids(
    ids: Union[pd.Series, np.ndarray], make_unique: bool = False, seed: int = 2021
) -> np.ndarray:
    """Return an Nx3 matrix of RGB colors in the range 0.0 ... 1.0 for all unique ids in `ids`

    @param ids: Union[pd.Series, np.ndarray]
        Series or array of ids, that may contain repetitions.

    @param make_unique: bool
        Set to True to make unique (one row per ID) or False to map a unique
        color to each of the original IDs vector.

    @param seed: int
        Seed of the random generator to make sure that the sequence of colors
        is reproducible.

    @return np.ndarray
        Nx3 matrix of RGB colors in the range 0.0 ... 1.0.
    """

    # Make sure the sequence of colors is preserved across runs
    rng = np.random.default_rng(seed)

    # Get the list of unique IDs
    u_ids = np.unique(ids)

    if make_unique:

        # Allocate the matrix of colors
        colors = np.zeros((len(u_ids), 3), dtype=np.float64)

        for i in range(len(u_ids)):
            colors[i, 0] = rng.random(1)
            colors[i, 1] = rng.random(1)
            colors[i, 2] = rng.random(1)

    else:
        # Allocate the matrix of colors
        colors = np.zeros((len(ids), 3), dtype=np.float64)

        for id in u_ids:
            i = np.where(ids == id)
            colors[i, 0] = rng.random(1)
            colors[i, 1] = rng.random(1)
            colors[i, 2] = rng.random(1)

    return colors

def render_mpl(
    points: pd.DataFrame,
    colors: Union[np.ndarray, None] = None,
    filename: Union[Path, str, None] = None,
    point_size: float = 1.0,
    plot_trajectories: bool = False,
    legend: bool = True,
    axes: bool = True,
    dpi: int = 1200,
    skip_ids: tuple = (),
):
    """Render the points with the passed colors using MATPLOTLIB.

    @param points: np.ndarray
        Nx3 matrix of coordinates [x, y, z]N

    @param filename: Union[Path, str, None] (optional, default = None)
        Filename for saving the plot. If not set (or None), the plot will only be shown.

    @param colors: np.ndarray (optional, default = None)
        Nx3 matrix of coordinates [x, y, z]N. If omitted, all points will be painted white.

    @param colors: np.ndarray (optional, default = None)
        Nx3 matrix of coordinates [x, y, z]N. If omitted, all points will be painted white.

    @param point_size: float
        Scaling factor for the points.

    @param plot_trajectories: bool (optional, default = False)
        Set to True to connect consecutive dots for a given 'tid' with a line;
        use to plot tracking experiments.

    @param legend: bool (optional, default = True)
        Set to True to add the plot legend.

    @param axes: bool (optional, default = True)
        Set to True to show the axes.

    @param dpi: int (optional, default = 1200)
        Resolution of the rendered plot.
    """

    # Make sure that the points are sorted by track identifier first and time second.
    sorted_points = points.sort_values(by=["tid", "tim"])

    # Do we plot trajectories or individual points?
    if plot_trajectories:
        line_style = "-"
        line_width = 0.25
        marker = None
        marker_size = 0
    else:
        line_style = None
        line_width = 0.0
        marker = "."
        marker_size = point_size

    # Plot using MATPLOTLIB
    fig, ax = plt.subplots()
    ids = sorted_points["tid"].unique()

    for i, id in enumerate(ids):

        if id in skip_ids:
            continue

        # Get the points for current id
        tmp = sorted_points[sorted_points["tid"] == id]

        # Define the colors
        if colors is not None:
            try:
                color = colors[i, :]
            except:
                color = [0.0, 0.0, 0.0]
        else:
            color = [0.0, 0.0, 0.0]

        # Plot
        ax.plot(
            tmp["x"],
            tmp["y"],
            linestyle=line_style,
            linewidth=line_width,
            marker=marker,
            markersize=marker_size,
            label=str(id),
            color=color,
        )

    if legend:
        ax.legend(loc="best", fontsize="xx-small")

    ax.invert_yaxis()
    ax.axis("equal")

    if not axes:
        ax.set_axis_off()

    if filename is not None:
        try:
            format = Path(filename).suffix[1:]
            fig.savefig(filename, dpi=dpi, format=format)
            plt.close(fig)
        except:
            print(f"Could not save plot to {filename}.")
            plt.show()
    else:
        plt.show()


def plot_time_encoded_trajectory_mpl(
    points: pd.DataFrame,
    tid: int,
    filename: Union[Path, str, None] = None,
    axes: bool = True,
    dpi: int = 1200,
):
    """Plot a time-encoded trajectory for requested ID using MATPLOTLIB.

    @param points: np.ndarray
        Nx3 matrix of coordinates [x, y, z]N

    @param tid: int
        Trajectory id ('tid') to plot.

    @param filename: Union[Path, str, None] (optional, default = None)
        Filename for saving the plot. If not set (or None), the plot will only be shown.

    @param axes: bool (optional, default = True)
        Set to True to show the axes.

    @param dpi: int (optional, default = 1200)
        Resolution of the rendered plot.
    """

    # Make sure that the points are sorted by track identifier first and time second.
    sorted_points = points.sort_values(by=["tid", "tim"])

    # Only consider requested trajectory id
    points_tid = sorted_points[sorted_points["tid"] == tid].copy()

    # Extract needed data and prepare it for plotting
    x = points_tid["x"].values
    y = points_tid["y"].values
    time = points_tid["tim"].values
    points_reshaped = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points_reshaped[:-1], points_reshaped[1:]], axis=1)

    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(time.min(), time.max())
    lc = LineCollection(segments, cmap="Blues", norm=norm)
    # Set the values used for colormapping
    lc.set_array(time)
    lc.set_linewidth(2)

    # Prepare the plot
    fig, ax = plt.subplots()
    line = ax.add_collection(lc)
    fig.colorbar(line, ax=ax)
    ax.invert_yaxis()
    ax.axis("equal")

    if not axes:
        ax.set_axis_off()

    if filename is not None:
        try:
            format = Path(filename).suffix[1:]
            fig.savefig(filename, dpi=dpi, format=format)
            plt.close(fig)
        except:
            print(f"Could not save plot to {filename}.")
            plt.show()
    else:
        plt.show()
