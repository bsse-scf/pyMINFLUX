import cython
import numpy as np
cimport numpy as cnp


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)
cpdef process_raw_data_cython(raw_data, is_3d: bool):

    cdef int n_reps = 5
    if is_3d:
        n_reps = 10

    # Calculate the number of rows in the final dataset
    cdef int n_tot_data_els = len(raw_data)
    cdef int n_rows = n_tot_data_els * n_reps

    # Allocate arrays

    # The list of TIDs to process **must** be a  c-style int[], not a NumPy array
    cdef int[:] iter_tid = np.empty(n_rows, dtype=np.int32) # This must be a c-style int[]

    # These are NumPy arrays
    cdef cnp.ndarray[cnp.int32_t, ndim=1] tid = np.empty(n_rows, dtype=np.int32)
    cdef cnp.ndarray[cnp.int32_t, ndim=1] aid = np.empty(n_rows, dtype=np.int32)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1, cast=True] vld = np.empty(n_rows, dtype=np.bool)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] tim = np.empty(n_rows, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] x = np.empty(n_rows, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] y = np.empty(n_rows, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] z = np.empty(n_rows, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] efo = np.empty(n_rows, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] cfr = np.empty(n_rows, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dcr = np.empty(n_rows, dtype=np.float64)

    # cdef int[:] tid = np.empty(n_rows, dtype=np.int32)
    # cdef int[:] aid = np.empty(n_rows, dtype=np.int32)
    # cdef cnp.uint8_t[:] vld = np.empty(n_rows, dtype=np.bool)
    # cdef double[:] tim = np.empty(n_rows, dtype=np.float64)
    # cdef double[:] x = np.empty(n_rows, dtype=np.float64)
    # cdef double[:] y = np.empty(n_rows, dtype=np.float64)
    # cdef double[:] z = np.empty(n_rows, dtype=np.float64)
    # cdef double[:] efo = np.empty(n_rows, dtype=np.float64)
    # cdef double[:] cfr = np.empty(n_rows, dtype=np.float64)
    # cdef double[:] dcr = np.empty(n_rows, dtype=np.float64)

    # Extract the data that does not need looping
    iter_tid = raw_data["tid"]

    # Get all unique TIDs
    cdef int[:] tids = np.unique(iter_tid)  # This must be a c-style int[]
    cdef int num_tids = len(tids)

    # Keep track of the index at the beginning of each iteration
    cdef int index = 0

    # Initialize some counters that we will reuse a few times
    cdef int counter
    cdef int pm_step = num_tids // 1000
    cdef int pc_step = num_tids // 100
    cdef int step = num_tids // 10
    cdef int n_els = 0
    cdef int internal_index = 0
    cdef int i = 0

    # Initialize some arrays
    cdef int[:] c_aid
    cdef double[:] c_tim
    cdef cnp.uint8_t[:] c_vld
    cdef double[:, :] c_loc
    cdef double[:] c_efo
    cdef double[:] c_cfr
    cdef double[:] c_dcr

    # Process all TIDs
    cdef int c_tid = 0
    for counter in range(num_tids):

        c_tid = tids[counter]

        # Get data for current TID
        data = raw_data[raw_data["tid"] == c_tid]

        # Build the artificial IDs: one for each of the
        # traces that share the same TID
        c_aid = np.repeat(np.arange(len(data)), n_reps)

        # Keep track of the number of elements that will be added
        # to each column in this iteration
        n_els = len(c_aid)

        # Add the artificial IDs
        aid[index: index + n_els] = c_aid

        # Timepoints
        c_tim = np.repeat(data["tim"], n_reps)
        tim[index: index + n_els] = c_tim

        # Extract valid flags
        c_vld = np.repeat(data["vld"], n_reps)
        vld[index: index + n_els] = c_vld

        # Extract the localizations from the iterations
        for i in range(len(data["itr"]["loc"])):
            c_loc = data["itr"]["loc"][i]
            x[internal_index: internal_index + n_reps] = c_loc[:, 0]
            y[internal_index: internal_index + n_reps] = c_loc[:, 1]
            z[internal_index: internal_index + n_reps] = c_loc[:, 2]
            internal_index += n_reps

        # Extract EFO
        internal_index = index
        for i in range(len(data["itr"]["efo"])):
            c_efo = data["itr"]["efo"][i]
            efo[internal_index: internal_index + n_reps] = c_efo
            internal_index += n_reps

        # Extract CFR
        internal_index = index
        for i in range(len(data["itr"]["cfr"])):
            c_cfr = data["itr"]["cfr"][i]
            cfr[internal_index: internal_index + n_reps] = c_cfr
            internal_index += n_reps

        # Extract DCR
        internal_index = index
        for i in range(len(data["itr"]["dcr"])):
            c_dcr = data["itr"]["dcr"][i]
            dcr[internal_index: internal_index + n_reps] = c_dcr
            internal_index += n_reps

        # Add the tid
        tid[index: index + n_els] = c_tid * np.ones(np.shape(c_aid))

        # Update the starting index
        index += n_els

        assert index <= n_rows

        # if counter > 1 and step > 100 and counter % step == 0:
        #     print("|", end="")
        # elif counter > 1 and pc_step > 1000 and counter % pc_step == 0:
        #     print("o", end="")
        # elif counter > 1 and pm_step > 10000 and counter % pm_step == 0:
        #     print(".", end="")
        # else:
        #     pass

    # print("")

    return tid, aid, vld, tim, x, y, z, efo, cfr, dcr