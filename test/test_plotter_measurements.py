import numpy as np

from pyminflux.ui.plotter import compute_measurement_geometry


def test_pca_thickness_symmetric():
    # two parallel lines at y=+5 and y=-5 over same x range -> thickness ~ 10
    xs = np.concatenate([np.linspace(0, 100, 50), np.linspace(0, 100, 50)])
    ys = np.concatenate([np.full(50, 5.0), np.full(50, -5.0)])
    geometry = compute_measurement_geometry(np.column_stack((xs, ys)))
    assert abs(geometry["mean_thickness"] - 10.0) < 1e-6
    assert abs(geometry["median_thickness"] - 10.0) < 1e-6
    assert abs(geometry["p95_thickness"] - 10.0) < 1e-6


def test_pca_thickness_tilted():
    # tilted structure: line at +5 and -5 rotated by 30 degrees
    theta = np.deg2rad(30.0)
    R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    base_x = np.linspace(0, 100, 80)
    p1 = np.vstack((base_x, np.full_like(base_x, 5.0))).T @ R.T
    p2 = np.vstack((base_x, np.full_like(base_x, -5.0))).T @ R.T
    pts = np.vstack((p1, p2))
    geometry = compute_measurement_geometry(pts)
    assert abs(geometry["mean_thickness"] - 10.0) < 1e-6
    assert abs(geometry["median_thickness"] - 10.0) < 1e-6
