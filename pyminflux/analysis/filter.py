"""
__author__ = 'Aaron Ponti'
"""
import numpy as np
from scipy.stats import multivariate_normal


def filter_vector_field(X, Y, dX, dY, radius_support_x, radius_support_y):
    """
    Filters a vector field by calculating a Gaussian-weighted average of
    neighboring vector components at each position in the vector field.

    The support of the Gaussian weighting kernel is defined as the radius of
    the 2D Gaussian from the center to the location where the support falls
    to a 1% of the central value.

    :param X: list of X coordinates of the vector field.
    :param Y: list of Y coordinates of the vector field.
    :param dX: list of X components at each position in the vector field.
    :param dY: list of Y components at each position in the vector field.
    :param radius_support_x: radius of the Gaussian weighting function
    support in X direction
    :param radius_support_y:  radius of the Gaussian weighting function
    support in X direction
    :return: (wdX, wdY) filtered components ate the X, Y positions with
    calculated Gaussian weights.
    """

    # Make sure we have numpy arrays
    if type(X) is list:
        X = np.array(X, dtype='float64')

    if type(Y) is list:
        Y = np.array(Y, dtype='float64')

    if type(dX) is list:
        dX = np.array(dX, dtype='float64')

    if type(dY) is list:
        dY = np.array(dY, dtype='float64')

    # Make sure that the vector positions and components are floats
    if X.dtype is not np.dtype('float64'):
        X = X.astype(np.float64)
    if Y.dtype is not np.dtype('float64'):
        Y = Y.astype(np.float64)
    if dX.dtype is not np.dtype('float64'):
        dX = dX.astype(np.float64)
    if dY.dtype is not np.dtype('float64'):
        dY = dY.astype(np.float64)

    # Make sure the dimensions are correct
    X = X.reshape((len(X), 1))
    Y = Y.reshape((len(Y), 1))
    dX = dX.reshape((len(dX), 1))
    dY = dY.reshape((len(dY), 1))

    # Prepare the output
    wdX = np.zeros(X.shape[0], dtype='float64')
    wdY = np.zeros(Y.shape[0], dtype='float64')

    # Calculate sigma from the support
    sigma_x = radius_support_x / np.sqrt(2.0 * np.log(100))
    sigma_y = radius_support_y / np.sqrt(2.0 * np.log(100))

    for i in range(len(X)):

        # Calculate relative displacements around current position
        x0 = X - X[i]
        y0 = Y - Y[i]

        # Gaussian weight function - integral set to 1
        P = np.concatenate((x0, y0), axis=1)
        W = multivariate_normal.pdf(P, mean=[0, 0], cov=[sigma_x, sigma_y])
        W = W / np.sum(W)

        # Calculate weighted components wdX[i], wdY[i]
        wdX[i] = np.dot(dX.T, W)
        wdY[i] = np.dot(dY.T, W)

    # Return the weighted components
    return wdX, wdY
