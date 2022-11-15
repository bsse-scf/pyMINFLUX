from scipy.ndimage import interpolation
from scipy.fftpack import dct
from scipy.spatial.distance import hamming, pdist, squareform
import numpy as np
import pandas as pd

MIN_ACCEPTED_QUALITY = 0.1


def qc_columns_names():
    """
    Returns a list of quality control column names.
    :return: list of quality control column names.

    Remark: the original MATLAB code also defines

        qc_status:   human friendly message regarding the validation or
                     reassignment of tracks by quality control. In current
                     implementation, the quality control does not correct the
                     original tracking and no additional information is stored.

        qc_cell_del: indices of cells to be deleted. In current implementation,
                     the quality control does not mark tracks or cells for
                     deletion. In the original MATLAB implementation, cells are
                     marked as "to be deleted" if a mis-segmentation is
                     recognized.

    Data for the 'qc_status' and 'qc_cell_del' columns would be initialized as
    follows:

        # Quality control -- Human friendly validation result
        data_frame = data_frame.assign(
            qc_status=pd.Series(np.empty(
                len(data_frame.index))).astype(np.unicode))

        # Quality control -- Store deletion flags (this might not be needed)
        data_frame = data_frame.assign(
            qc_cell_del=pd.Series(np.zeros(
                len(data_frame.index))).astype(np.bool))

    """
    return ["qc_fingerprint", "qc_dist", "qc_validated", "qc_age",
            "qc_track_index"]


def add_qc_columns(data_frame):
    """
    Adds the columns for the quality control to the data frame if they do not
    exists, or resets them to zero/empty/false if they do.

    Remark: the original MATLAB code also defines 'qc_status' and 'qc_cell_del'
            (see qc_columns_names()).

    Data for the 'qc_status' and 'qc_cell_del' columns would be initialized as
    follows:

        # Quality control -- Human friendly validation result
        data_frame = data_frame.assign(
            qc_status=pd.Series(np.empty(
                len(data_frame.index))).astype(np.unicode))

        # Quality control -- Store deletion flags (this might not be needed)
        data_frame = data_frame.assign(
            qc_cell_del=pd.Series(np.zeros(
                len(data_frame.index))).astype(np.bool))

    :param data_frame: a Pandas data frame.
    :return data_frame: updated data frame.
    """

    # Quality control -- Finger print
    data_frame = data_frame.assign(
        qc_fingerprint=pd.Series(np.zeros(
            len(data_frame.index))).asobject)

    # Quality control -- Shortest fingerprint distance
    data_frame = data_frame.assign(
        qc_dist=pd.Series(np.zeros(
            len(data_frame.index))).astype(np.float32))

    # Quality control -- Validation result (boolean)
    data_frame = data_frame.assign(
        qc_validated=pd.Series(np.zeros(
            len(data_frame.index))).astype(np.bool))

    # Quality control -- Track index
    data_frame = data_frame.assign(
        qc_track_index=pd.Series(-1 * np.ones(
            len(data_frame.index))).astype(np.uint32))

    # The following column is not being used yet

    # Quality control -- Age
    data_frame = data_frame.assign(
        qc_age=pd.Series(np.zeros(
            len(data_frame.index))).astype(np.uint32))

    return data_frame


def build_distance_matrix(data_frame, radius=40):
    """
    Build a boolean distance matrix for all cells and their neighbors within
    given radius.
    :param data_frame: current data_frame.
    :param radius: distance radius (default = 40 pixels).
    :return: data frame with the distance matrix appended as a property. 
    """

    cell_centers = np.concatenate((
        np.reshape(data_frame['cell.center.x'].values,
                   (data_frame.shape[0], 1)),
        np.reshape(data_frame['cell.center.y'].values,
                   (data_frame.shape[0], 1))
    ), axis=1)
    data_frame.qc_distances = squareform(
        pdist(cell_centers, metric='euclidean') <= radius)

    return data_frame


def build_fingerprint(full_img, data_frame, roi_size=32, p_roi_size=8,
                      radius=40):
    """
    Build fingerprints based on the DCT transform for all cells.

    Calculate unique cell track quality control feature based on Out Of Focus
    Brightfield image using the discrete cosine transform (DCT).

    Here the quality control features (hash/barcode) are computed for each
    frame using DCT and binarization of the frequencies containing the
    structural information creating a unique hash. It is possible to only
    calculate the qc feature for a number of specified tracks in a frame.
    """

    # Calculate fingerprints and store into the data frame
    for j in range(data_frame.shape[0]):

        cell_index = data_frame['cell.index'].values[j]
        row_index = data_frame[data_frame['cell.index'] == cell_index].index[0]
        data_frame.set_value(row_index, 'qc_fingerprint',
                             calc_fingerprint_for_frame_and_cell(full_img,
                                                                 data_frame,
                                                                 cell_index,
                                                                 roi_size,
                                                                 p_roi_size,
                                                                 radius))

    return data_frame


def calc_fingerprint_for_frame_and_cell(full_img, data_frame, cell_index,
                                        roi_size=32, p_roi_size=8, radius=40):
    """
    Correct the fingerprint of a given cell for a given frame.
    :return: fingerprint as a p_roi_size * p_roi_size numpy array of 0s and
    1s as np.uint8.
    """

    idx = data_frame['cell.index'] == cell_index
    center1x = data_frame['cell.center.x'][idx].values[0]
    center1y = data_frame['cell.center.y'][idx].values[0]

    # Crop area boundaries
    x0 = center1x - radius
    if x0 < 0:
        print("Warning: cell index %d -- cell crop out of bounds!" % cell_index)
        x0 = 0

    x = x0 + 2 * radius
    if x > full_img.shape[1]:
        print("Warning: cell index %d -- cell crop out of bounds!" % cell_index)
        x = full_img.shape[1]

    y0 = center1y - radius
    if y0 < 0:
        print("Warning: cell index %d -- cell crop out of bounds!" % cell_index)
        y0 = 0

    y = y0 + 2 * radius
    if y > full_img.shape[0]:
        print("Warning: cell index %d -- cell crop out of bounds!" % cell_index)
        y = full_img.shape[0]

    # Crop
    img = full_img[y0:y, x0:x]

    # Scaling factor
    factor = 1.0 / (float(img.shape[0]) / float(roi_size))

    # Scale to 32x32
    img_resized = interpolation.zoom(img, factor)

    # Calculate 2D discrete cosine transform and extract the lowest frequencies
    d_1 = dct(dct(img_resized, type=2, norm='ortho').T, type=2, norm="ortho")
    d_2 = d_1[0:p_roi_size, 0:p_roi_size]

    # Compute average of transform
    a_1 = np.mean(d_2)

    # Set final bits
    b_1 = d_2 > a_1

    # Return
    return b_1.ravel().astype(np.uint8)


def validate_tracking(old_data_frame, new_data_frame, radius):
    """
    Validate tracking based on fingerprint.

    Set radius to None to use all cells as candidates.
    :return: 
    """

    # Initialize results for new_data_frame, since we process all tracks
    # defined in old_data_frame, and in most cases new_data_frame has more
    # cells.
    new_data_frame['qc_dist'] = -1
    new_data_frame['qc_track_index'] = -1
    new_data_frame['qc_validated'] = False

    # Now process all tracks from old_data_frame

    # Get all cell coordinates from new_data_frame
    x_new = new_data_frame['cell.center.x'].values
    y_new = new_data_frame['cell.center.y'].values

    # Squared radius
    sq_radius = radius * radius

    # Loop over all cells and compare their fingerprints to
    # validate the tracking results
    for old_row_index in old_data_frame.index:

        # Get the fingerprint for current cell
        old_fingerprint = old_data_frame.loc[old_row_index, 'qc_fingerprint']

        # Get track index for this cell
        old_track_index = old_data_frame.loc[old_row_index, 'track.index']

        # Get the corresponding row in the new dataframe
        new_row_index = new_data_frame['track.index'] == old_track_index

        # Get the cell picked by the original tracker
        new_tracked_cell_list = \
            new_data_frame.loc[new_row_index, 'cell.index'].values

        if len(new_tracked_cell_list) == 0:
            # The track ended in the previous time point
            new_tracked_cell = -1
        elif len(new_tracked_cell_list) == 1:
            new_tracked_cell = new_tracked_cell_list[0]
        else:
            raise Exception("One track with two target cells found!")

        # If we have a cell candidate we continue
        if new_tracked_cell != -1:

            if radius is None:

                new_fingerprint = new_data_frame.loc[:, 'qc_fingerprint']

            else:

                # Get the coordinates
                x_old = old_data_frame.loc[old_row_index, 'cell.center.x']
                y_old = old_data_frame.loc[old_row_index, 'cell.center.y']

                # Extract the fingerprints from the cells in new_data_frame
                # that are within 'radius' from current cell in old_data_frame
                new_indices, = np.where(((x_old - x_new) * (x_old - x_new) +
                                         (y_old - y_new) * (y_old - y_new)) <
                                        sq_radius)
                # Use iloc() to map into the original index
                new_fingerprint = new_data_frame.iloc[
                    new_indices.tolist()]['qc_fingerprint']

            # Compare fingerprints
            all_hamming_distances = []
            for f_index in new_fingerprint.index:
                all_hamming_distances.append(hamming(old_fingerprint,
                                                     new_fingerprint[f_index]))

            # The original track is compared with the one given by the
            # comparison of fingerprints and marked as confirmed or not
            # confirmed.

            # The minimum distance between fingerprints determines the match.
            qc_min_dist = np.Inf
            if len(all_hamming_distances) > 0:
                qc_min_dist = np.min(all_hamming_distances)
                min_index, = np.where(all_hamming_distances == qc_min_dist)
                if len(min_index) == 0:
                    idx_predicted_cell = -1
                elif len(min_index) == 1:
                    idx_predicted_cell = new_data_frame.loc[
                        new_fingerprint.index[min_index],
                        'cell.index'].values[0]
                    assert(np.all(new_data_frame.index[new_indices] ==
                                  new_fingerprint.index.values))
                else:
                    # More than one cell with the same fingerprint distance from
                    # the source. If one of the candidates is the one picked by
                    # the original tracker, choose that; otherwise just pick the
                    # first.
                    if new_tracked_cell in new_data_frame.loc[
                            new_fingerprint.index[min_index],
                            'cell.index'].index:
                        idx_predicted_cell = new_tracked_cell
                    else:
                        idx_predicted_cell = new_data_frame.loc[
                            new_fingerprint.index[min_index],
                            'cell.index'].values[0]

            else:
                idx_predicted_cell = -1

        else:
            idx_predicted_cell = -1

        # Do we have a match?
        is_match = idx_predicted_cell != -1 and \
            idx_predicted_cell == new_tracked_cell

        # Compare the cell indices
        if is_match:

            # Tracking result confirmed
            new_data_frame.loc[new_row_index, 'qc_validated'] = True

            # Get the track to the predicted cell
            pred_tracked_cell = int(new_data_frame.loc[
                new_data_frame['cell.index'] == idx_predicted_cell,
                'track.index'].values[0])

            # Min fingerprint distance
            min_f_distance = qc_min_dist

        else:

            # Tracking result not confirmed
            new_data_frame.loc[new_row_index, 'qc_validated'] = False

            # Track to the prediced cell is undefined
            pred_tracked_cell = -1

            # Min fingerprint distance is irrelevant
            min_f_distance = -1

        print("Match: %r: original cell: %d --(%d|%d)--> predicted cell: %d" %
              (is_match, new_tracked_cell, old_track_index,
               pred_tracked_cell, idx_predicted_cell))

        # Store information
        new_data_frame.loc[new_row_index, 'qc_dist'] = min_f_distance
        new_data_frame.loc[new_row_index, 'qc_track_index'] = pred_tracked_cell

    return new_data_frame
