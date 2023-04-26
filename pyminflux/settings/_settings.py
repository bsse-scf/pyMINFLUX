#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.

import os
import platform
from pathlib import Path

from PySide6.QtCore import QSettings

from pyminflux import __APP_NAME__
from pyminflux.state import State


class Settings:
    def __init__(self):
        """Constructor."""

        # Initialize the State
        self.state = State()

        # Define the organization and application names
        self.org_name = "ch.ethz"
        self.app_name = __APP_NAME__

        # Construct the file path for the INI file based on the platform
        if platform.system() == "Windows":
            config_folder = Path(os.environ["APPDATA"]) / self.org_name
        else:
            config_folder = Path.home() / ".config" / self.org_name
        config_folder.mkdir(parents=True, exist_ok=True)
        self.config_file_path = config_folder / f"{self.app_name}.ini"

        # Create the QSettings object
        self._settings = QSettings(str(self.config_file_path), QSettings.IniFormat)

    @property
    def instance(self):
        """Give access to the underlying QSettings object."""
        return self._settings