from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import pandas as pd
from pathlib import Path
import pptk
from typing import Union


def render_pptk(
        points: np.ndarray,
        colors: Union[np.ndarray, None] = None,
        point_size: float = 1.0
):
    """Render the points with the passed colors using pptk.

    @param points: np.ndarray
        Nx3 matrix of coordinates [x, y, z]N

    @param colors: np.ndarray (optional, default = None)
        Nx3 matrix of coordinates [x, y, z]N. If omitted, all points will be painted white.

    @param point_size: float
        Scaling factor for the points.
    """

    # Initialize the viewer (blocking)
    v = pptk.viewer(points)

    # If no colors were specified, set them all to white
    if colors is None:
        colors = np.ones(points.shape, dtype=np.float32)

    # Assign the colors
    v.attributes(colors)
    v.color_map('cool')

    # Draw the point cloud
    v.set(
        point_size=point_size,
        bg_color=[0, 0, 0, 0],
        show_axis=0,
        show_grid=0
    )


def render_o3d(
        points: np.ndarray,
        colors: Union[np.ndarray, None] = None,
        point_size: float = 1.0,
        on_grid: bool = False,
        voxel_size: float = 1.0,
        calc_normals: bool = False
):
    """Render the points with the passed colors using pptk.

    @param points: np.ndarray
        Nx3 matrix of coordinates [x, y, z]N

    @param colors: np.ndarray (optional, default = None)
        Nx3 matrix of coordinates [x, y, z]N. If omitted, all points will be painted white.

    @param point_size: float
        Scaling factor for the points.

    @param on_grid: bool (optional, default = True)
        Set to True to interpolate points on a regular grid with given voxel size.

    @param voxel_size: float (optional, default = 1.0)
        Voxel size for the interpolation of the points. Ignored if on_grid is False.

    @param calc_normals: bool
        Set to True to calculate and use normals.

    """

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    if calc_normals:
        pcd.estimate_normals()

    # Initialize the Visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    opt = vis.get_render_option()
    opt.background_color = np.array([0.0, 0.0, 0.0])
    opt.point_size = point_size

    if on_grid:
        # Interpolate the point cloud on a grid with given voxel size
        voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(
            pcd,
            voxel_size=voxel_size
        )
        vis.add_geometry(voxel_grid)
    else:
        # Render point cloud as is
        vis.add_geometry(pcd)

    # Blocking
    vis.run()


def render_mpl(
        points: pd.DataFrame,
        colors: Union[np.ndarray, None] = None,
        filename: Union[Path, str, None] = None,
        point_size: float = 1.0,
        plot_trajectories: bool = False,
        legend: bool = True,
        axes: bool = True,
        dpi: int = 1200,
        skip_ids: tuple = ()
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
    sorted_points = points.sort_values(by=['tid', 'tim'])

    # Do we plot trajectories or individual points?
    if plot_trajectories:
        line_style = '-'
        line_width = 0.25
        marker = None
        marker_size = 0
    else:
        line_style = None
        line_width = 0.0
        marker = '.'
        marker_size = point_size

    # Plot using MATPLOTLIB
    fig, ax = plt.subplots()
    ids = sorted_points['tid'].unique()

    for i, id in enumerate(ids):

        if id in skip_ids:
            continue

        # Get the points for current id
        tmp = sorted_points[sorted_points['tid'] == id]

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
            tmp['x'],
            tmp['y'],
            linestyle=line_style,
            linewidth=line_width,
            marker=marker,
            markersize=marker_size,
            label=str(id),
            color=color
        )

    if legend:
        ax.legend(loc="best", fontsize="xx-small")

    ax.invert_yaxis()
    ax.axis('equal')

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
        dpi: int = 1200
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
    sorted_points = points.sort_values(by=['tid', 'tim'])

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
    lc = LineCollection(segments, cmap='Blues', norm=norm)
    # Set the values used for colormapping
    lc.set_array(time)
    lc.set_linewidth(2)

    # Prepare the plot
    fig, ax = plt.subplots()
    line = ax.add_collection(lc)
    fig.colorbar(line, ax=ax)
    ax.invert_yaxis()
    ax.axis('equal')

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
