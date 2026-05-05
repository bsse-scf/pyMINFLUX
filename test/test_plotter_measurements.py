import numpy as np


def compute_thickness(xs, ys):
    pts = np.vstack((xs, ys)).T
    mean_pt = pts.mean(axis=0)
    centered = pts - mean_pt
    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    direction = vh[0]
    perp = np.array([-direction[1], direction[0]])
    signed_perp = centered @ perp
    perp_dists = np.abs(signed_perp)
    avg_perp = float(np.mean(perp_dists))
    return 2.0 * avg_perp


def test_pca_thickness_symmetric():
    # two parallel lines at y=+5 and y=-5 over same x range -> thickness ~ 10
    xs = np.concatenate([np.linspace(0, 100, 50), np.linspace(0, 100, 50)])
    ys = np.concatenate([np.full(50, 5.0), np.full(50, -5.0)])
    thickness = compute_thickness(xs, ys)
    assert abs(thickness - 10.0) < 1e-6


def test_pca_thickness_tilted():
    # tilted structure: line at +5 and -5 rotated by 30 degrees
    theta = np.deg2rad(30.0)
    R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    base_x = np.linspace(0, 100, 80)
    p1 = np.vstack((base_x, np.full_like(base_x, 5.0))).T @ R.T
    p2 = np.vstack((base_x, np.full_like(base_x, -5.0))).T @ R.T
    pts = np.vstack((p1, p2))
    thickness = compute_thickness(pts[:, 0], pts[:, 1])
    assert abs(thickness - 10.0) < 1e-6
