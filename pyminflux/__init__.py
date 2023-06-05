#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
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

import pyqtgraph as pg

__APP_NAME__ = "pyMINFLUX"
__version__ = "0.2.0"

# PyQtGraph settings
pg.setConfigOption("imageAxisOrder", "row-major")  # For best performance

# Documentation
__doc__ = f"""
This is the documentation of the `pyminflux` core command-line API (version {__version__}).

Currently, `pyminflux` is compatible with python 3.10 and 3.11.
"""

# Do not build the documentation for the following modules that are only used by the user interface.
__pdoc__ = {}
__pdoc__["base"] = False
__pdoc__["main"] = False
__pdoc__["resources"] = False
__pdoc__["settings"] = False
__pdoc__["state"] = False
__pdoc__["threads"] = False
__pdoc__["ui"] = False
__pdoc__["utils"] = False
