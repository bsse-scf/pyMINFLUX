import argparse
import os

import errno
import numpy as np
import pandas as pd
import scipy.spatial
from skimage.io import imread
import sys
import time

from analysis.filter import filter_vector_field
from analysis.qc import add_qc_columns, build_fingerprint, validate_tracking, qc_columns_names



from tools.fio import retrieve_sorted_file_list, \
    sort_file_list, save_data_frame_list_to_hdf5_file, \
    save_data_frame_list_to_tsv_files, load_data_frame_from_hdf5_file, \
    save_file_list_to_hdf5_file, load_file_list_from_hdf5_file, \
    save_settings_to_hdf5_file, save_variables_to_hdf5_file, \
    load_settings_from_hdf5_file, load_variables_from_hdf5_file
from analysis.defaults import DEFAULT_QC, \
    DEFAULT_NUMBER_OF_FILES, DEFAULT_MAX_PENALTY, DEFAULT_DRIFT,\
    DEFAULT_MAX_JUMP, DEFAULT_GROWTH_PENALTY, DEFAULT_DISPLACEMENT_PENALTY, \
    DEFAULT_FACTOR_ORIENTATION, DEFAULT_FACTOR_AREA, DEFAULT_JUMP_PENALTY, \
    DEFAULT_FILTER_SUPPORT, DEFAULT_EXPORT


__DEBUG_USE_LAPJV2_PYTHON__ = False


class Tracker:
    def __init__(self,
                 file_list: list = [],
                 image_file_list: list = [],
                 result_folder: str = '',
                 factor_area: float = DEFAULT_FACTOR_AREA,
                 factor_orientation: float = DEFAULT_FACTOR_ORIENTATION,
                 displacement_penalty: float = DEFAULT_DISPLACEMENT_PENALTY,
                 growth_penalty: float = DEFAULT_GROWTH_PENALTY,
                 jump_penalty: float = DEFAULT_JUMP_PENALTY,
                 max_penalty: float = DEFAULT_MAX_PENALTY,
                 drift: float = DEFAULT_DRIFT,
                 max_jump: int = DEFAULT_MAX_JUMP,
                 filter_support: float = DEFAULT_FILTER_SUPPORT,
                 export: bool = DEFAULT_EXPORT,
                 qc: bool = DEFAULT_QC):
        """
        Cell tracking and lineage reconstruction function.
        :param file_list: list of files to process
        :param image_file_list: list of image files to process
        :param result_folder: folder where to store the results
        :param factor_area: factor for area
        :param factor_orientation: factor for orientation
        :param displacement_penalty: penalty for displacement
        :param growth_penalty: penalty for cell growth
        :param jump_penalty: penalty for a skipped frame (jump)
        :param max_penalty: maximum total penalty
        :param drift: inter-frame drift
        :param max_jump: maximum gap size in a track
        :param filter_support: support radius (in pixel) for vector field
        filtering
        :param export: whether to export tracking results as TSV files as well
        :param qc: whether to perform quality control on the tracking results
        :return: data_frames, sorted_file_names, sorted_indices
        """

        # Data frames
        #
        # Do NOT access the data frames directly; use load_dataframe_for_index()
        # instead!
        self.__data_frames = []

        # Files and folders
        self.__sorted_file_list = []
        self.__sorted_indices = []
        self.__result_folder = ""
        self.__sorted_image_file_list = []

        # Now set the values (via the associated properties)
        self.result_folder = result_folder
        self.file_list = file_list
        self.image_file_list = image_file_list

        # Indicate whether the results are up to date with the input
        self.results_up_to_date = False

        # Settings
        self.__settings = {"factor_area": factor_area,
                           "factor_orientation": factor_orientation,
                           "displacement_penalty": displacement_penalty,
                           "growth_penalty": growth_penalty,
                           "jump_penalty": jump_penalty,
                           "max_penalty": max_penalty,
                           "drift": drift,
                           "max_jump": max_jump,
                           "filter_support": filter_support,
                           "export": export,
                           "qc": qc}

    @property
    def settings(self):
        """
        Return the settings.
        :return:
        """
        return self.__settings

    @settings.setter
    def settings(self, *args, **kwargs):
        """
        Set/update passed __settings.
        :param kwargs: dictionary of key-value pairs for __settings to be updated.
        :return:
        """
        if args is not None and len(args) == 1 and type(args[0]) is dict:
            s = args[0]

            for key, value in s.items():
                if key in self.__settings.keys():
                    self.__settings[key] = value
                else:
                    raise KeyError("Unknown setting %s" % key)

        for key, value in kwargs.items():
            if key in self.__settings.keys():
                self.__settings[key] = value
            else:
                raise KeyError("Unknown setting %s" % key)

        # If the __settings have changed, the results are no longer up-to-date
        self.results_up_to_date = False

    @property
    def data_frames(self):
        raise Exception("You are accessing data_frames directly! Use "
                        "Tracker.load_dataframe_for_index() instead!")

    @data_frames.setter
    def data_frames(self, dataframes):
        raise Exception("You are trying to set data_frames directly! Use "
                        "Tracker.store_dataframe_for_index() instead!")

    @property
    def result_folder(self):
        """
        Return the result folder.
        :return: result folder.
        :rtype: string
        """
        return self.__result_folder

    @result_folder.setter
    def result_folder(self, result_folder):
        """
        Sets the result folder.

        The folder will be created if it does not exist.
        :type result_folder: string
        """
        if result_folder == "":
            self.__result_folder = result_folder
            return

        if not os.path.exists(result_folder):
            try:
                os.makedirs(result_folder)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise e
        self.__result_folder = result_folder

    @property
    def file_list(self):
        return self.__sorted_file_list

    @file_list.setter
    def file_list(self, file_list):
        """
        Set the list of files to be processed.
        :param file_list: list of tiles to be processed.
        """
        self.__sorted_file_list, self.__sorted_indices = \
            sort_file_list(file_list)
        self.__data_frames = [None] * len(self.__sorted_file_list)

        # If the input files have changed, the results are no longer up-to-date
        self.results_up_to_date = False

    @property
    def image_file_list(self):
        return self.__sorted_image_file_list

    @image_file_list.setter
    def image_file_list(self, image_file_list):
        """
        Sort and set the list of image files.
        :param image_file_list: list of image files.
        """
        self.__sorted_image_file_list, _ = sort_file_list(image_file_list)

    def num_data_frames(self):
        """
        Return the number of data frames.
        :return:
        """
        return len(self.__data_frames)

    def load_dataframe_for_index(self, index):
        """
        Get dataframe for given index.

        If the dataframe is loaded, return it.
        If not, try to read it from the result file and return it.
        If there is no dataframe in the result file, read it from the
        original TSV file.

        Please notice that if the dataframe is read from disk, it is also
        stored into memory.

        :param index: index of the dataframe to return.
        :return: Pandas dataframe.
        """
        if index < 0 or index > len(self.__data_frames):
            raise IndexError("Index out of bonds.")

        # If the DataFrame is stored in self__data_frames, we return
        # it from there
        if self.__data_frames[index] is not None:
            # Dataframe is already in memory.
            return self.__data_frames[index]

        # Otherwise, try to read it from the results file (and store it as well)
        filename = os.path.join(self.__result_folder, 'project.h5')
        df = load_data_frame_from_hdf5_file(filename, self.__sorted_indices[index])
        if df is not None:
            print("Dataframe %d loaded from project file." % (index + 1))
            self.__data_frames[index] = df
            return df

        # Finally, try from the original TSV file (and store it)
        try:
            df = pd.read_csv(self.__sorted_file_list[index], sep='\t')
            if df is not None:
                print("Dataframe %d loaded from file %s." %
                      ((index + 1), self.__sorted_file_list[index]))
                self.__data_frames[index] = df
                return df
        except Exception as e:
            print("Could not read file %s: error was: %s" %
                  (self.__sorted_file_list[index], e))

        return None

    def store_dataframe_for_index(self, index, df):
        """
        Set passed dataframe for given index.

        Notice that the function will store a COPY of the dataframe
        to make sure that there are no unintentional changes from outside.

        :param index: index of the dataframe to return.
        :param df: Pandas dataframe.
        """
        if index < 0 or index > len(self.__data_frames):
            raise IndexError("Index out of bonds.")

        self.__data_frames[index] = df.copy()

        # If a dataframe has changed, the results are no longer up-to-date
        self.results_up_to_date = False

    def revert_dataframe_to_file_for_file_name(self, file_name):
        """
        Revert to file for the dataframe of given name.

        :param file_name: file name only or with full path.
        :type string
        :return: loaded dataframe and index in the file list
        :rtype: tuple (pandas.DataFrame, int)
        """

        # Does the file have a full path?
        dir_name = os.path.dirname(file_name)
        if dir_name == '':
            file_path = os.path.dirname(self.file_list[0])
            file_name = os.path.join(file_path, file_name)

        file_name = file_name.replace("\\", "/")

        # Find the index
        index, = np.where(self.file_list == file_name)
        if len(index) != 1:
            print("Could not find file %s in list! This is a bug."
                  "Please report!")
            return None, -1
        index = index[0]

        # Load the original TSV file (and store it)
        try:
            df = pd.read_csv(file_name, sep='\t')
            if df is not None:
                print("Dataframe %d loaded from file %s." %
                      ((index + 1), file_name))
                self.__data_frames[index] = df
        except Exception as e:
            print("Could not read file %s: error was: %s" %
                  (file_name, e))

        # If a dataframe has changed, the results are no longer up-to-date
        self.results_up_to_date = False

        return df, index

    def export(self):
        """
        Export the data frames (only) to result folder as an TSV file.
        :return: True if saving was successful, False otherwise.
        """
        return save_data_frame_list_to_tsv_files(self.__data_frames,
                                                 self.__sorted_file_list,
                                                 self.__result_folder)

    def load(self):
        """
        Load the tracker status stored in the project HDF5 file.
        :return: True if loading was successful, False otherwise.
        """

        # Full file name (prepend the result folder)
        if self.__result_folder == '':
            return
        project_full_name = os.path.join(self.__result_folder, "project.h5")

        # Try loading the file and image file lists
        self.file_list, self.image_file_list = \
            load_file_list_from_hdf5_file(project_full_name)

        # Try loading the settings
        settings = load_settings_from_hdf5_file(project_full_name)
        if len(settings) > 0:
            self.__settings = settings

        # Load the state of the project
        variables = load_variables_from_hdf5_file(project_full_name, 'state')
        if 'up_to_date' in variables:
            self.results_up_to_date = variables['up_to_date']

    def save(self):
        """
        Save the tracker status to result folder as an HDF5 file.
        :return: True if saving was successful, False otherwise.
        """

        # Check that we have a result folder
        if self.__result_folder == "":
            return False

        # Create results folder if it does not exist
        if not os.path.exists(self.__result_folder):
            os.makedirs(self.__result_folder)

        # Full file name (prepend the result folder)
        out_full_name = os.path.join(self.__result_folder, "project.h5")

        # Try saving the file list
        res = save_file_list_to_hdf5_file(self.__sorted_file_list,
                                          self.__sorted_image_file_list,
                                          out_full_name)

        # Try saving the results
        res &= save_data_frame_list_to_hdf5_file(self.__data_frames,
                                                 self.__sorted_indices,
                                                 out_full_name)

        # Try saving the settings
        res &= save_settings_to_hdf5_file(out_full_name, self.__settings)

        # Results are up to date
        res &= save_variables_to_hdf5_file(out_full_name, 'state',
                                           up_to_date=self.results_up_to_date)

        return res

    def __get_costs_for_assignment(self, A, A1, A2, A3, A4, assignment,
                                   num_frame_rows):
        """
        Extracts the costs for the given assignment.
        """

        # Initialize cost arrays: the size depends on the maximum assignment
        # index. At the same time, len_cost might not be less than the number
        # of rows in the cost matrix.
        len_cost = np.max(assignment) + 1
        if len_cost < num_frame_rows:
            len_cost = num_frame_rows
        cost = np.empty(len_cost) * np.nan
        cost1 = cost.copy()
        cost2 = cost.copy()
        cost3 = cost.copy()
        cost4 = cost.copy()

        for i in range(len(assignment)):
            j = assignment[i]
            cost[j] = A[i, j]
            cost1[j] = A1[i, j]
            cost2[j] = A2[i, j]
            cost3[j] = A3[i, j]
            cost4[j] = A4[i, j]

        # Return costs
        return cost, cost1, cost2, cost3, cost4

    def __calculate_cost_matrices(self, new_frame, old_frame):
        """
        Calculate all costs to be used for the linear assignment problem.
        """

        # Since the max penalty is broken into 4 parts, we split it
        penalty = self.__settings["max_penalty"] / 4.0

        #
        # Displacement cost A1
        #

        # Calculate the distance from the propagated old positions to the
        # actual new positions
        dist_old = np.column_stack((
            old_frame["cell.center.x"] + self.__settings["drift"] *
            old_frame["age"] * old_frame["filtered.dif.x"],
            old_frame["cell.center.y"] + self.__settings["drift"] *
            old_frame["age"] * old_frame["filtered.dif.y"]))
        dist_new = np.column_stack((
            new_frame["cell.center.x"].astype(np.float64),
            new_frame["cell.center.y"].astype(np.float64)))

        # The squared distance is multiplied by the 'displacement_penalty'
        A1 = self.__settings["displacement_penalty"] * \
             scipy.spatial.distance.cdist(dist_old, dist_new, 'sqeuclidean')

        # Add columns with constant penalty
        A1 = np.column_stack((A1, penalty * np.ones((A1.shape[0],
                                                     old_frame.shape[0]))))

        #
        # Area cost A2
        #

        new_cell_area = np.kron(np.ones(
            (old_frame.shape[0], 1)),
            new_frame["cell.area"].values.reshape((1, new_frame.shape[0])))
        old_cell_area = np.kron(np.ones(
            (1, new_frame.shape[0])),
            old_frame["cell.area"].values.reshape((old_frame.shape[0], 1)))

        # Relative area
        rel_area = new_cell_area / old_cell_area

        # The cost is a power function of the relative area (numpy.power() is
        # quite slow, so we inline)
        tmp = np.log(rel_area) - self.__settings["growth_penalty"]
        A2 = self.__settings["factor_area"] * tmp * tmp

        # Young cells (as defined of having a summed area smaller than the
        # mean area of the new frame) have a 100-fold lower penalty
        sum_area = new_cell_area + old_cell_area
        mean_area = np.mean(new_frame["cell.area"])
        A2[(sum_area < mean_area).nonzero()] /= 100.0

        # Add columns with constant penalty
        A2 = np.column_stack((A2, penalty * np.ones((A1.shape[0],
                                                     old_frame.shape[0]))))

        #
        # Orientation cost A3
        #

        # Difference in cell orientation
        new_cell_orient = np.kron(
            np.ones((old_frame.shape[0], 1)),
            new_frame["cell.orientation"].values.reshape(
                (1, new_frame.shape[0])))
        old_cell_orient = np.kron(
            np.ones((1, new_frame.shape[0])),
            old_frame["cell.orientation"].values.reshape(
                (old_frame.shape[0], 1)))

        dif_orientation = old_cell_orient - new_cell_orient

        # The cost is a power function of the difference in orientation
        A3 = self.__settings["factor_orientation"] * np.power(
            np.sin(np.pi / 180.0 * dif_orientation), 2)

        # Add columns with constant penalty
        A3 = np.column_stack((A3, penalty * np.ones((A1.shape[0],
                                                     old_frame.shape[0]))))

        #
        # Frame skipping cost A4
        #

        # The cost is a function of the number of skipped frames
        A4 = np.kron(np.ones(
            (1, new_frame.shape[0])),
            self.__settings["jump_penalty"] *
            np.array((old_frame["age"] - 1))
            .reshape((old_frame.shape[0], 1)))

        # Add columns with constant penalty
        A4 = np.column_stack((A4, penalty * np.ones((A1.shape[0],
                                                     old_frame.shape[0]))))

        # Total cost
        A = A1 + A2 + A3 + A4

        # Return combined and individual costs
        return A, A1, A2, A3, A4

    def track(self):
        """
        Actual tracker.
        """
        # Inform
        print("Function called with parameters: \n"
              "\tFile list = %d files\n"
              "\tImage file list = %d files\n"
              "\tResult folder = %s\n"
              "\tFactor area = %f\n"
              "\tFactor orientation = %f\n"
              "\tDisplacement penalty = %f\n"
              "\tGrowth penalty = %f\n"
              "\tJump penalty = %f\n"
              "\tMax penalty = %f\n"
              "\tDrift = %f\n"
              "\tMax jump = %d\n"
              "\tFilter support = %f\n"
              "\tQuality control = %r\n"
              % (len(self.__sorted_file_list),
                 len(self.__sorted_image_file_list),
                 self.__result_folder,
                 self.__settings["factor_area"],
                 self.__settings["factor_orientation"],
                 self.__settings["displacement_penalty"],
                 self.__settings["growth_penalty"],
                 self.__settings["jump_penalty"],
                 self.__settings["max_penalty"],
                 self.__settings["drift"],
                 self.__settings["max_jump"],
                 self.__settings["filter_support"],
                 self.__settings["qc"]))

        # Get the first frame (careful, the source is defined in
        # load_dataframe_for_index())
        first_data_frame = self.load_dataframe_for_index(0)

        # Add new columns to the first data frame
        n_rows = first_data_frame.shape[0]
        first_data_frame["age"] = \
            pd.Series(np.ones(n_rows, np.uint32),
                      index=first_data_frame.index)
        first_data_frame["track.index"] = \
            pd.Series(np.array(range(n_rows), np.uint32),
                      index=first_data_frame.index)
        first_data_frame["dif.x"] =\
            pd.Series(np.zeros(n_rows, np.float64),
                      index=first_data_frame.index)
        first_data_frame["dif.y"] =\
            pd.Series(np.zeros(n_rows, np.float64),
                      index=first_data_frame.index)
        first_data_frame["filtered.dif.x"] = \
            pd.Series(np.zeros(n_rows, np.float64),
                      index=first_data_frame.index)
        first_data_frame["filtered.dif.y"] =\
            pd.Series(np.zeros(n_rows, np.float64),
                      index=first_data_frame.index)

        # Perform quality control?
        if self.__settings['qc']:

            # Add the columns needed for the quality control
            first_data_frame = add_qc_columns(first_data_frame)
            #self.store_dataframe_for_index(0, first_data_frame)

            # Calculate the boolean cell distance matrix and store it as an
            # attribute of the data frame object self.
            # data_frames[0] = build_distance_matrix(self,_data_frames[0], radius=40)

            # Calculate the quality control for the first data frame and the
            # first image and store as a column of the dataframe
            first_data_frame = build_fingerprint(
                imread(self.__sorted_image_file_list[0]),
                first_data_frame, radius=40)

            # The quality control track indices of the first time point
            # are set to 0 : n_cells - 1.
            first_data_frame['qc_track_index'] = \
                pd.Series(np.arange(0, first_data_frame.shape[0]))

        # Columns to copy
        columns_to_copy = ["cell.index", "cell.center.x", "cell.center.y",
                           "cell.area", "cell.orientation", "age",
                           "track.index", "dif.x", "dif.y",
                           "filtered.dif.x", "filtered.dif.y"]

        if self.__settings['qc']:
            columns_to_copy = columns_to_copy + qc_columns_names()

        # Store updated data frame
        self.store_dataframe_for_index(0, first_data_frame)

        # Now extract just the relevant columns for analysis (copy them
        # to a new data frame)
        old_frame = first_data_frame[columns_to_copy].copy()

        # Keep track of the global number of tracks
        global_number_of_tracks = old_frame.shape[0]

        # Now read the successive files
        for i in range(1, len(self.__sorted_file_list)):

            time_for_loop = time.time()

            # Get the ith frame (careful, the source is defined in
            # load_dataframe_for_index())
            new_frame = self.load_dataframe_for_index(i)

            # Perform quality control?
            if self.__settings['qc']:

                # Add the columns needed for the quality control
                new_frame = add_qc_columns(new_frame)

                # Calculate the boolean cell distance matrix and store it
                # as an attribute of the data frame
                # new_frame = build_distance_matrix(new_frame, radius=40)

                time_for_fingerprint = time.time()

                # Calculate the quality control for the first data frame and
                # the first image and store it as an attribute of the data frame
                new_frame = build_fingerprint(
                    imread(self.__sorted_image_file_list[i]), new_frame)

                print("Fingerprint calculation completed in %f seconds." %
                      (time.time() - time_for_fingerprint))

            # Calculate the costs
            costs = self.__calculate_cost_matrices(new_frame, old_frame)

            A = costs[0]
            A1 = costs[1]
            A2 = costs[2]
            A3 = costs[3]
            A4 = costs[4]

            # Solve linear assignment
            start_time = time.time()
            if __DEBUG_USE_LAPJV2_PYTHON__:
                sol = []# lapjv2.lapjv_python(A)  # Python implementation
                assignment = sol[0]
            else:
                sol = [] #lapjv2.lapjv_cython(A)  # Cython implementation
                assignment = sol[0]
            print("Assignment problem solved in %f seconds." %
                  (time.time() - start_time))

            # Update costs
            cost, cost1, cost2, cost3, cost4 = \
                self.__get_costs_for_assignment(A, A1, A2, A3, A4,
                                                assignment,
                                                new_frame.shape[0])

            # Update frames for next iteration
            x = np.in1d(assignment, range(0, new_frame.shape[0]))
            x_x = np.where(x)[0]

            # Preserve unassigned tracks that are not too old (make sure
            # to copy the extracted rows)
            indices = np.setdiff1d(range(old_frame.shape[0]), x_x,
                                   assume_unique=True)
            if len(indices) == 0:
                very_old_frame = pd.DataFrame(columns=old_frame.columns.values)
            else:
                very_old_frame = old_frame.iloc[indices.tolist(), :].copy()

            # Old tracks with are larger than max_jump are discarded
            if not very_old_frame.empty:
                selection = very_old_frame[very_old_frame["age"] >
                                           self.__settings["max_jump"]]
                if not selection.empty:
                    very_old_frame.drop(selection.index, inplace=True)

            # Now update the age of the remaining tracks
            if not very_old_frame.empty:
                # Calculate the distance between this frame and the previous
                # (it is used to properly set the age of tracks in case
                # of skipped files)
                delta_index = self.__sorted_indices[i] - \
                              self.__sorted_indices[i - 1]

                # Add the age difference
                very_old_frame["age"] += delta_index

            # Assign new tracks
            y_y = assignment[x_x]
            new_track_index = -1 * np.ones(new_frame.shape[0])
            new_track_index[y_y] = old_frame["track.index"].values[x_x]
            not_assigned = np.where(new_track_index == -1)
            num_not_assigned = len(not_assigned[0])
            new_indices = range(global_number_of_tracks,
                                global_number_of_tracks + num_not_assigned)
            new_track_index[not_assigned] = new_indices

            # Calculate displacements
            dif_x = np.zeros(new_frame.shape[0])
            dif_y = np.zeros(new_frame.shape[0])
            dif_x[y_y] =\
                (new_frame["cell.center.x"].values[y_y] -
                 old_frame["cell.center.x"].values[x_x]) / \
                old_frame["age"].values[x_x]
            dif_y[y_y] = \
                (new_frame["cell.center.y"].values[y_y] -
                 old_frame["cell.center.y"].values[x_x]) / \
                old_frame["age"].values[x_x]

            # Filter displacements (optional)
            if self.__settings["filter_support"] != 0.0:
                filtered_dif_x = np.zeros(new_frame.shape[0])
                filtered_dif_y = np.zeros(new_frame.shape[0])
                filtered_dif_x[y_y], filtered_dif_y[y_y] = \
                    filter_vector_field(new_frame["cell.center.x"].values[y_y],
                                        new_frame["cell.center.y"].values[y_y],
                                        dif_x[y_y],
                                        dif_y[y_y],
                                        self.__settings["filter_support"],  # X
                                        self.__settings["filter_support"])  # Y
            else:
                filtered_dif_x = dif_x.copy()
                filtered_dif_y = dif_y.copy()

            # Store the results (track indices, displacements and costs)
            new_frame["track.index"] = new_track_index
            new_frame["dif.x"] = dif_x[0:len(new_track_index)]
            new_frame["dif.y"] = dif_y[0:len(new_track_index)]
            new_frame["filtered.dif.x"] = filtered_dif_x[0:len(new_track_index)]
            new_frame["filtered.dif.y"] = filtered_dif_y[0:len(new_track_index)]
            new_frame["cost"] = cost[0:len(new_track_index)]
            new_frame["cost1"] = cost1[0:len(new_track_index)]
            new_frame["cost2"] = cost2[0:len(new_track_index)]
            new_frame["cost3"] = cost3[0:len(new_track_index)]
            new_frame["cost4"] = cost4[0:len(new_track_index)]

            # Tracking verification (based on DCT fingerprinting)
            # Notice: the quality control does not make any change to the
            # original tracking results. Just stores the alternative tracking
            # index and the quality control measures in additional
            # qc_* dataframe columns.
            if self.__settings['qc']:
                new_frame = validate_tracking(old_frame, new_frame, radius=40)

            # Update new frame in list of data frames
            self.store_dataframe_for_index(i, new_frame)

            # Update the global number of tracks
            global_number_of_tracks += num_not_assigned

            # Update old_frame for next iteration
            if very_old_frame.empty:
                very_old_age = []
                very_old_track_index = []
                very_old_dif_x = []
                very_old_dif_y = []
                very_old_filtered_dif_x = []
                very_old_filtered_dif_y = []
                very_old_cell_center_x = []
                very_old_cell_center_y = []
                very_old_cell_area = []
                very_old_cell_orientation = []
                very_old_qc_fingerprint = []
                very_old_qc_track_index = []
            else:
                very_old_age = very_old_frame["age"]
                very_old_track_index = very_old_frame["track.index"]
                very_old_filtered_dif_x = very_old_frame["filtered.dif.x"]
                very_old_filtered_dif_y = very_old_frame["filtered.dif.y"]
                very_old_dif_x = very_old_frame["dif.x"]
                very_old_dif_y = very_old_frame["dif.y"]
                very_old_cell_center_x = very_old_frame["cell.center.x"]
                very_old_cell_center_y = very_old_frame["cell.center.y"]
                very_old_cell_area = very_old_frame["cell.area"]
                very_old_cell_orientation = very_old_frame["cell.orientation"]
                if self.__settings['qc']:
                    very_old_qc_fingerprint = very_old_frame["qc_fingerprint"]
                    very_old_qc_track_index = very_old_frame["qc_track_index"]

            # Prepare old_frame for the next iteration
            old_frame = pd.DataFrame(columns=old_frame.columns)

            old_frame["age"] = np.concatenate(
                [np.ones(new_frame.shape[0]), very_old_age], 0)
            old_frame["track.index"] = np.concatenate(
                [new_track_index, very_old_track_index], 0)
            old_frame["dif.x"] = np.concatenate([dif_x, very_old_dif_x], 0)
            old_frame["dif.y"] = np.concatenate([dif_y, very_old_dif_y], 0)
            old_frame["filtered.dif.x"] = np.concatenate(
                [dif_x, very_old_filtered_dif_x], 0)
            old_frame["filtered.dif.y"] = np.concatenate(
                [dif_y, very_old_filtered_dif_y], 0)
            old_frame["cell.center.x"] = np.concatenate(
                [new_frame["cell.center.x"], very_old_cell_center_x], 0)
            old_frame["cell.center.y"] = np.concatenate(
                [new_frame["cell.center.y"], very_old_cell_center_y], 0)
            old_frame["cell.area"] = np.concatenate(
                [new_frame["cell.area"], very_old_cell_area], 0)
            old_frame["cell.orientation"] = np.concatenate(
                [new_frame["cell.orientation"], very_old_cell_orientation], 0)
            if self.__settings['qc']:
                old_frame["qc_fingerprint"] = np.concatenate(
                    [new_frame["qc_fingerprint"], very_old_qc_fingerprint], 0)
                old_frame["qc_track_index"] = np.concatenate(
                    [new_frame["qc_track_index"], very_old_qc_track_index], 0)

            print("Processed %d of %d files [current iteration:"
                  " %f seconds]..." %
                  (i + 1, len(self.__sorted_file_list),
                   time.time() - time_for_loop))

            # End of loop

        # At the end of the tracking, the results are up-to-date!
        self.results_up_to_date = True

        print("Done.")


if __name__ == '__main__':

    # Argument parser
    parser = argparse.ArgumentParser(description="Cell lineage tracer")

    # Folder to process
    parser.add_argument("-f",
                        "--folder",
                        type=str,
                        help="Result folder to process")

    # Folder to process
    parser.add_argument("-i",
                        "--image-folder",
                        type=str,
                        help="Image folder to process")

    # Result folder
    parser.add_argument("-r",
                        "--result-folder",
                        type=str,
                        help="Folder where to store the results")

    # Factor area
    parser.add_argument("-a",
                        "--factor-area",
                        type=float,
                        default=DEFAULT_FACTOR_AREA,
                        help="Factor for area")

    # Factor orientation
    parser.add_argument("-o",
                        "--factor-orientation",
                        type=float,
                        default=DEFAULT_FACTOR_ORIENTATION,
                        help="Factor for orientation")

    # Penalty for displacement
    parser.add_argument("-t",
                        "--displacement-penalty",
                        type=float,
                        default=DEFAULT_DISPLACEMENT_PENALTY,
                        help="Penalty for displacement")

    # Penalty for cell growth
    parser.add_argument("-g",
                        "--growth-penalty",
                        type=float,
                        default=DEFAULT_GROWTH_PENALTY,
                        help="Penalty for cell growth")

    # Penalty for a skipped frame (i.e. jump)
    parser.add_argument("-j",
                        "--jump-penalty",
                        type=float,
                        default=DEFAULT_JUMP_PENALTY,
                        help="Penalty for a skipped frame (jump)")

    # Max jump
    parser.add_argument("-m",
                        "--max-jump",
                        type=int,
                        default=DEFAULT_MAX_JUMP,
                        help="Maximum gap size in a track")

    # Max penalty
    parser.add_argument("-p",
                        "--max-penalty",
                        type=float,
                        default=DEFAULT_MAX_PENALTY,
                        help="Max total penalty")

    # Drift
    parser.add_argument("-d",
                        "--drift",
                        type=float,
                        default=DEFAULT_DRIFT,
                        help="Inter-frame drift")

    # Drift
    parser.add_argument("-s",
                        "--filter-support",
                        type=float,
                        default=DEFAULT_FILTER_SUPPORT,
                        help="Filter support (set to zero to disable)")

    # Number of files
    parser.add_argument("-n",
                        "--number-of-files",
                        type=int,
                        default=DEFAULT_NUMBER_OF_FILES,
                        help="Number of files to process (omit to process all)")

    # Export results as TSV files
    parser.add_argument("-e",
                        "--export",
                        action="store_true",
                        default=False,
                        help="Export tracker results as TSV files "
                             "(in addition to HDF5)")

    # Quality control images
    parser.add_argument("-q",
                        "--qc",
                        action="store_true",
                        default=False,
                        help="Perform quality control on the tracking results")

    # Parse the arguments
    args = parser.parse_args()

    # Extract the arguments
    in_folder = args.folder
    in_image_folder = args.image_folder
    in_result_folder = args.result_folder
    in_factor_area = args.factor_area
    in_factor_orientation = args.factor_orientation
    in_displacement_penalty = args.displacement_penalty
    in_growth_penalty = args.growth_penalty
    in_jump_penalty = args.jump_penalty
    in_max_penalty = args.max_penalty
    in_drift = args.drift
    in_max_jump = args.max_jump
    in_num_files = args.number_of_files
    in_filter_support = args.filter_support
    in_export = args.export
    in_qc = args.qc

    # Test the folders
    if in_folder is None:
        sys.exit("Please specify the input folder to process.")

    if in_result_folder is None:
        sys.exit("Please specify the output folder for storing the results.")

    if in_image_folder is None:
        in_image_folder = ''

    # Get the list of files to be processed
    local_sorted_file_list, local_sorted_indices = \
        retrieve_sorted_file_list(in_folder, 'txt', in_num_files)

    # Get the list of images to be processed
    local_sorted_image_file_list = []
    if in_image_folder != '':
        local_sorted_image_file_list, _ = \
            retrieve_sorted_file_list(in_image_folder, 'tif', in_num_files)

    tracker = Tracker(file_list=local_sorted_file_list,
                      image_file_list=local_sorted_image_file_list,
                      result_folder=in_result_folder,
                      factor_area=in_factor_area,
                      factor_orientation=in_factor_orientation,
                      displacement_penalty=in_displacement_penalty,
                      growth_penalty=in_growth_penalty,
                      jump_penalty=in_jump_penalty,
                      max_penalty=in_max_penalty,
                      drift=in_drift,
                      max_jump=in_max_jump,
                      filter_support=in_filter_support,
                      export=in_export,
                      qc=in_qc)

    # Track
    tracker.track()

    # Save the results
    print("Saving results...")
    tracker.save()
    print("Done.")

    # If needed, export the results as well
    if in_export:
        print("Exporting results...")
        tracker.export()
        print("Done.")
