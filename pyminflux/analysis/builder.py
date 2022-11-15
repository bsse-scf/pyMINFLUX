import argparse
import pandas as pd
import numpy as np
import sys
import os
from .defaults import DEFAULT_NUMBER_OF_FILES, DEFAULT_QC
from ..tools.fio import retrieve_sorted_file_list, save_variables_to_hdf5_file, sort_file_list


def __mjriam(data_frames):
    """
    Build the trajectories from the tracked data files.
    :param data_frames: list of Pandas data frames.
    :return: tuple of (x, y)-coordinate vs. time ordered per trajector (row)

    @todo Optimize storage!!!!
    """

    # Inform
    print("Building trajectories...")

    # Count the trajectories
    max_index = -1
    for i in range(len(data_frames)):
        current_max_index = np.max(data_frames[i]["track.index"])
        if current_max_index > max_index:
            max_index = current_max_index
    max_index = int(max_index)

    # Allocate memory for all trajectories and displacement vectors
    trajectories_x = np.empty((max_index + 1, len(data_frames)))
    trajectories_y = np.empty((max_index + 1, len(data_frames)))
    cell_indices = np.empty((max_index + 1, len(data_frames)))
    track_indices = np.empty((max_index + 1, len(data_frames)))
    trajectories_dx = np.empty((max_index + 1, len(data_frames)))
    trajectories_dy = np.empty((max_index + 1, len(data_frames)))
    trajectories_filtered_dx = np.empty((max_index + 1, len(data_frames)))
    trajectories_filtered_dy = np.empty((max_index + 1, len(data_frames)))
    cost = np.empty((max_index + 1, len(data_frames)))
    cost1 = np.empty((max_index + 1, len(data_frames)))
    cost2 = np.empty((max_index + 1, len(data_frames)))
    cost3 = np.empty((max_index + 1, len(data_frames)))
    cost4 = np.empty((max_index + 1, len(data_frames)))
    trajectories_x[:] = np.nan
    trajectories_y[:] = np.nan
    trajectories_dx[:] = np.nan
    trajectories_dy[:] = np.nan
    trajectories_filtered_dx[:] = np.nan
    trajectories_filtered_dy[:] = np.nan
    cell_indices[:] = np.nan
    track_indices[:] = np.nan
    cost[:] = np.NaN
    cost1[:] = np.nan
    cost2[:] = np.nan
    cost3[:] = np.nan
    cost4[:] = np.nan

    # Build trajectory matrices
    for i in range(len(data_frames)):
        for j in range(data_frames[i].shape[0]):
            track_index = int(data_frames[i]["track.index"][j])
            track_indices[track_index, i] = track_index
            trajectories_x[track_index, i] = data_frames[i]["cell.center.x"][j]
            trajectories_y[track_index, i] = data_frames[i]["cell.center.y"][j]
            trajectories_dx[track_index, i] = data_frames[i]["dif.x"][j]
            trajectories_dy[track_index, i] = data_frames[i]["dif.y"][j]
            trajectories_filtered_dx[track_index, i] = data_frames[i]["filtered.dif.x"][j]
            trajectories_filtered_dy[track_index, i] = data_frames[i]["filtered.dif.y"][j]
            cell_indices[track_index, i] = data_frames[i]["cell.index"][j]
            if i > 0:
                # There are no costs associated to the first time point
                cost[track_index, i] = data_frames[i]["cost"][j]
                cost1[track_index, i] = data_frames[i]["cost1"][j]
                cost2[track_index, i] = data_frames[i]["cost2"][j]
                cost3[track_index, i] = data_frames[i]["cost3"][j]
                cost4[track_index, i] = data_frames[i]["cost4"][j]
        print("Processed frame %d of %d." % (i+1, len(data_frames)))

    print("Done.")

    return (trajectories_x, trajectories_y, trajectories_dx, trajectories_dy,
            trajectories_filtered_dx, trajectories_filtered_dy, cell_indices,
            track_indices, cost, cost1, cost2, cost3, cost4)


def __load(sorted_file_list, sorted_indices):
    """
    Build the trajectories

    :param sorted_file_list: sorted list of file names with full path
    :param sorted_indices: sorted list of numeric indices from file names
    :return: list of dataframes
    """

    # Initialize space to store the trajectories by time point
    data_frames = [None] * sorted_indices[np.max(sorted_indices) - 1]

    # Load the files
    for i in range(len(sorted_file_list)):

        # Corresponding time point
        t = sorted_indices[i] - sorted_indices[0]

        try:
            print("Loading file " + sorted_file_list[i] + "...")
            data_frames[t] = pd.read_csv(sorted_file_list[i], sep='\t')

        except OSError:
            print("This error is not recoverable. Quitting...")
            sys.exit(1)

    # Return the loaded data frames
    return data_frames


def builder(file_list: list,
            result_folder: str,
            qc: bool = DEFAULT_QC) -> bool:
    """
    Build trajectories from tracking results.
    :param file_list: list of files to process
    :param result_folder: folder where to store the results
    :param qc: whether to create quality control figures
    :return: True if the tracking was successful, False otherwise
    """
    print("Function called with parameters: \n"
          "\tFile list = %d files\n"
          "\tResult folder = %s\n"
          "\tQuality control = %r\n"
          % (len(file_list), result_folder, qc))

    # Sort the file list and the sorted indices
    local_sorted_file_list, local_sorted_indices = sort_file_list(file_list)

    # Load the data files into data frames
    data_frames = __load(local_sorted_file_list, local_sorted_indices)

    # Perform the trajectory building
    (traj_x, traj_y, traj_dx, traj_dy, traj_filt_dx, traj_filt_dy, cell_indices,
     track_indices, cost, cost1, cost2, cost3, cost4) = __mjriam(data_frames)

    # Save the results
    print("Saving results...")
    full_file_name = os.path.join(result_folder, "project.h5")
    success = save_variables_to_hdf5_file(full_file_name,
                                          traj_x=traj_x, traj_y=traj_y,
                                          traj_dx=traj_dx, traj_dy=traj_dy,
                                          traj_filt_dx=traj_filt_dx,
                                          traj_filt_dy=traj_filt_dy,
                                          cell_indices=cell_indices,
                                          track_indices=track_indices,
                                          cost=cost,
                                          cost1=cost1,
                                          cost2=cost2,
                                          cost3=cost3,
                                          cost4=cost4)
    print("Done.")

    return success


if __name__ == '__main__':

    # Argument parser
    parser = argparse.ArgumentParser(description="Cell lineage tracer")

    # Folder to process
    parser.add_argument("-f",
                        "--folder",
                        type=str,
                        help="Folder to process")

    # Result folder
    parser.add_argument("-r",
                        "--result-folder",
                        type=str,
                        help="Folder where to store the results")

    # Number of files
    parser.add_argument("-n",
                        "--number-of-files",
                        type=int,
                        default=DEFAULT_NUMBER_OF_FILES,
                        help="Number of files to process (omit to process all)")

    # Quality control images
    parser.add_argument("-q",
                        "--qc",
                        action="store_true",
                        default=False,
                        help="Save quality control figures")

    # Parse the arguments
    args = parser.parse_args()

    # Extract the arguments
    in_folder = args.folder
    in_result_folder = args.result_folder
    in_num_files = args.number_of_files
    in_qc = args.qc

    # Test the folder
    if in_folder is None:
        sys.exit("Please specify the input folder to process.")

    if in_result_folder is None:
        sys.exit("Please specify the output folder for storing the results.")

    # Get the list of files to be analyzed
    sorted_file_list, sorted_indices = retrieve_sorted_file_list(in_folder,
                                                                 in_num_files)

    # Call tracker
    builder(file_list=sorted_file_list,
            result_folder=in_result_folder,
            qc=in_qc)
