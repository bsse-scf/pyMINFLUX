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
This is the **development** documentation of the `pyminflux` core command-line API (version {__version__}).

Currently, `pyminflux` is compatible with python 3.10 and 3.11.

**Usage**: see [example notebook](https://github.com/bsse-scf/pyMINFLUX/blob/feature/extended_stats/examples/processing.ipynb).

**Project home**: [https://pyminflux.ethz.ch](https://pyminflux.ethz.ch)
"""

# Do not build the documentation for the following modules that are only used by the user interface.
__pdoc__ = {
    "base": False,
    "main": False,
    "resources": False,
    "settings": False,
    "state": False,
    "threads": False,
    "ui": False,
    "utils": False,
}
