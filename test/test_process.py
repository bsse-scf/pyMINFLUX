import numpy as np
from unittest import TestCase
from pyminflux.process import get_colors_for_unique_ids, process_minflux_file


class TestProcess(TestCase):
    def test_get_colors_for_unique_ids(self):
        ids = np.array([0, 1, 2, 0, 1, 3, 2, 2])
        colors = get_colors_for_unique_ids(ids)

        self.assertTrue(colors.shape[0] == len(ids))
        self.assertTrue(np.all(colors[0, :] == colors[3, :]))
        self.assertTrue(np.all(colors[1, :] == colors[4, :]))
        self.assertTrue(np.all(colors[2, :] == colors[6, :]))
        self.assertTrue(np.all(colors[2, :] == colors[7, :]))

    def test_process_minflux_file(self):
        print("TestProcess.test_process_minflux_file(): implement me!")
