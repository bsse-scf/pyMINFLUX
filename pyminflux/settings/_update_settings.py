#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

import os
import platform
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSettings

from pyminflux import __APP_NAME__


class UpdateSettings:
    def __init__(self, min_elapsed_seconds: int = 60 * 60 * 24 * 7):
        """Constructor.

        Parameters
        ----------

        min_elapsed_seconds: int
            Minimum elapsed time in seconds since last check. Default is 60 * 60 * 24 * 7 seconds (1 week).
        """

        # Store the min elapsed time for check
        self._min_elapsed_seconds = min_elapsed_seconds

        # Define the organization and application names
        self.org_name = "ch.ethz"
        self.app_name = __APP_NAME__

        # Construct the file path for the INI file based on the platform
        if platform.system() == "Windows":
            config_folder = Path(os.environ["APPDATA"]) / self.org_name
        else:
            config_folder = Path.home() / ".config" / self.org_name
        config_folder.mkdir(parents=True, exist_ok=True)
        self.config_file_path = config_folder / f"{self.app_name}_update.ini"

        # Create the QSettings object
        self._update_settings = QSettings(
            str(self.config_file_path), QSettings.IniFormat
        )

    def seconds_since_last_check(self):
        """Return the elapsed time in seconds since last check."""

        # Read last
        last_check_time = float(
            self._update_settings.value("last_check_timestamp", -1.0)
        )

        # If no timestamp yet, save it now
        if last_check_time == -1.0:
            last_check_time = self.update_last_check_time()

        # Calculate seconds since last check
        elapsed_time = datetime.now().timestamp() - last_check_time

        return elapsed_time

    def is_elapsed(self):
        """Return True if the elapsed time in seconds since last check is larger than `min_elapsed_seconds`."""
        return self.seconds_since_last_check() >= self._min_elapsed_seconds

    def update_last_check_time(self):
        """Save the new check time in the settings file."""

        # Current time in seconds
        current_time = datetime.now().timestamp()

        # Update the last check time
        self._update_settings.setValue("last_check_timestamp", current_time)

        # Sync the settings with file
        self._update_settings.sync()

        # Return current time
        return current_time
