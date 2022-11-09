import re
import os
import numpy as np
import ntpath
import pandas as pd


def natural_key(string_):
    """
    See http://www.codinghorror.com/blog/archives/001018.html

    To sort listToSortInPlace, use:

    sorted(listToSortInPlace, key=natural_key)
    """
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def filename(path):
    """
    Return the base name of a file with full path.

    :param path: file name with full path.
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def sort_file_list(file_list):
    """
    Sort a list of files.

    The list is sorted numerically by the last index before the extension
    before it is returned.

    :param file_list: list of file names (with or without path)
    :return: sorted list of file names
    """

    # Define the regular expression to extract the numeric index
    regex_num = r".*?([0-9]+)\.[a-zA-Z]+$"

    if type(file_list) is not np.ndarray:
        file_list = np.array(file_list)

    # Extract all numerical indices
    indices = np.full(len(file_list), np.nan, dtype=np.uint32)
    for i in range(len(file_list)):
        # Extract the index
        try:
            index = int(re.findall(regex_num, file_list[i])[0])
            indices[i] = index
        except IndexError:
            # We leave a NaN for this file
            pass

    # Now sort the indices numerically and the file names. If there are NaNs
    # they will be sorted to the end of the array.
    s_indices = np.argsort(indices)
    sorted_indices = indices[s_indices]
    sorted_file_list = file_list[s_indices]

    return sorted_file_list, sorted_indices


def retrieve_sorted_file_list(folder, extension='txt', num_files=-1):
    """
    Retrieve the sorted list of files to be processed.

    The list is sorted numerically by the last index before the extension
    before it is returned.

    :param folder: full path to the folder to be scanned
    :param extension: file extension (without '.'): default is 'txt'
    :param num_files: number of files to be processed (-1 to process all)
    :return: sorted list of file names (with full path)
    """

    if not os.path.exists(folder):
        raise OSError("The specified folder does not exist.")

    # Regex to filter for the expected file names
    regex = r".*?([0-9]+)\." + extension + "$"

    # Extract files to be processed
    files_to_process = np.array(
        [os.path.join(folder, f)
         for f in os.listdir(folder)
         if os.path.isfile(os.path.join(folder, f))
         and len(re.findall(regex, f.lower())) == 1])

    # Sort the file list by the last numeric index
    sorted_file_list, sorted_indices = sort_file_list(files_to_process)

    # If it is the case, return only the requested number of files
    if num_files != -1 and num_files < len(sorted_file_list):
        sorted_file_list = sorted_file_list[0: num_files]

    return sorted_file_list, sorted_indices


def save_data_frame_list_to_tsv_files(data_frames, sorted_file_list,
                                      out_folder):
    """
    Export the data frames to the selected folder as a series of TSV file.

    :param data_frames: list of Pandas data frames with appended tracking
    results.
    :param sorted_file_list: input file names.
    :param out_folder: folder where to write the TSV files.
    :return: True if saving was successful, False otherwise.
    """

    if len(data_frames) == 0:
        return False

    # Create results folder if it does not exist
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    for i in range(len(sorted_file_list)):

        if data_frames[i] is None:
            continue

        # Get the folder name without path
        name = filename(sorted_file_list[i])

        # Prepend the result folder
        out_full_name = os.path.join(out_folder, name)

        # Write the file
        data_frames[i].to_csv(out_full_name, sep='\t', encoding='utf-8')

    return True


def load_settings_from_hdf5_file(full_file_name):
    """
    Load settings from HDF5 file.

    :param full_file_name: file name of the HDF5 file with full path
    :return: settings dictionary
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for storing the settings!")
        return False

    # Write the data frame
    try:
        settings = pd.DataFrame.to_dict(store.get("/settings"), 'records')[0]
    except KeyError:
        settings = {}

    # Close file
    store.close()

    return settings


def save_settings_to_hdf5_file(full_file_name, settings):
    """
    Save the current settings to HDF5.

    :param full_file_name: file name of the HDF5 file with full path
    :param settings: settings dictionary
    :return: True if the settings could be stored successfully, False otherwise.
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for storing the settings!")
        return False

    # Write the data frame
    try:
        store.put('/settings', pd.DataFrame.from_dict([settings]),
                  table=True, encoding="utf8")
    except Exception as e:
        print("Could not store the settings. The error was: ", e)

    # Close file
    store.close()

    return True


def load_data_frame_from_hdf5_file(full_file_name, index):
    """
    Loads a Pandas data frame with given index from an HDF5 file.

    # The index is a single integer.

    :param full_file_name: file name of the HDF5 file with full path
    :param index: index of the data frame to be loaded (an integer)
    :return: loaded Pandas data frame or None if it could not be loaded.
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for loading dataframe!")
        return None

    # Group
    grp = '/tracker/t_%05d' % int(index)

    # Try reading the data frame
    try:
        df = store.get(grp)
    except:
        return None

    # Close file
    store.close()

    # Return the loaded dataframe
    return df


def save_data_frame_list_to_hdf5_file(data_frames, sorted_indices,
                                      full_file_name):
    """
    Save a list of Pandas data frames to an HDF5 file.

    # @todo Overwrite existing file!

    :param data_frames: list of Pandas data frames
    :param sorted_indices: list of sorted file indices (time points)
    :param full_file_name: file name of the HDF5 file with full path
    :return: True if the data variables could be stored successfully,
    False otherwise.
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name + " for storing results!")
        return False

    # Write tracker results to it
    for i in range(len(data_frames)):

        if data_frames[i] is None:
            continue

        # Group
        grp = '/tracker/t_%05d' % int(sorted_indices[i])

        # Write the data frame
        try:
            store.put(grp, data_frames[i], table=True, encoding="utf8")
        except Exception as e:
            print("Could not store data frame. The error was: ", e)

    # Close file
    store.close()

    return True


def load_file_list_from_hdf5_file(full_file_name):
    """
    Read the file and image lists from an HDF5 file.
    :param full_file_name: file name of the HDF5 file with full path
    :return: tuple with list of files and image files; lists can be empty.
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for retrieving the file lists!")
        return None

    # Read the Pandas column and covert it to a list
    file_list = []
    image_list = []
    try:
        file_list = store.get('/file_list').values
        file_list = file_list.reshape(file_list.shape[0])
        file_list = file_list.tolist()
        image_list = store.get('/image_list').values
        image_list = image_list.reshape(image_list.shape[0])
        image_list = image_list.tolist()
    except:
        pass

    # Close file
    store.close()

    return file_list, image_list


def save_file_list_to_hdf5_file(file_list, image_list, full_file_name):
    """
    Save the file and image lists to an HDF5 file.
    :param full_file_name: file name of the HDF5 file with full path
    :param file_list: list of file names with full path (notice: they should
    be sorted)
    :param image_list: list of image file names with full path (notice: they
    should be sorted)
    :return: True of the file list could be saved successfully, False otherwise.
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for storing file names!")
        return False

    # Write list as Pandas dataframes
    try:
        store.put('/file_list', pd.DataFrame(file_list),
                  table=True, encoding="utf8")
        store.put('/image_list', pd.DataFrame(image_list),
                  table=True, encoding="utf8")
    except Exception as e:
        print("Could not store file lists. The error was: " + str(e))

    # Close file
    store.close()

    return True


def load_variables_from_hdf5_file(full_file_name, group_name):
    """
    Load variables from group from an HDF5 file.

    The function should be called as follows:

        load_variables_from_hdf5_file('/path/to/file.h5', 'group_name')

    :param full_file_name: file name of the HDF5 file with full path
    :param group_name: name of the group under which the variables are stored
    :return: dictionary of variables {variable_name_1: variable_value_1,
     variable_name_2: variable_value_2, ...}
    """
    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for reading the variables!")
        return False

    if not group_name.startswith("/"):
        group_name = "/" + group_name

    # Load variable from group
    try:
        variables = pd.DataFrame.to_dict(store.get(group_name), 'records')[0]
    except KeyError:
        variables = {}

    # Close file
    store.close()

    return variables


def save_variables_to_hdf5_file(full_file_name, group_name='variables',
                                *args, **kwargs):
    """
    Save variables to an HDF5 file.

    The function should be called as follows:

        save_variables_to_hdf5_file('/path/to/file.h5', 'group_name',
         var1=var1, var2=var2, var3=5.0)

    where var1, var2, var3 are the names of the variables as they should be
    written in the HDF5 file followed by their value.

    :param full_file_name: file name of the HDF5 file with full path
    :param group_name: name of the HDF5 group where the variables are saved.
    :param args: ignored
    :param kwargs: standard kwargs python dictionary to pass named arguments to
    a function.
    :return: True if the variables could be stored successfully,
    False otherwise.
    """
    if len(kwargs) == 0:
        raise ValueError("Expected key-value pairs "
                         "variable_name=variable_value")

    if len(args) > 0:
        print("Non-named parameters are ignored.")

    if not group_name.startswith("/"):
        group_name = "/" + group_name

    # Try opening the file
    try:
        store = pd.HDFStore(full_file_name)
    except OSError:
        print("Could not open file " + full_file_name +
              " for storing the variables!")
        return False

    # Write the data frame
    try:
        store.put(group_name, pd.DataFrame.from_dict([kwargs]),
                  table=True, encoding="utf8")
    except Exception as e:
        print("Could not store the settings. The error was: ", e)

    # Close file
    store.close()

    return True
