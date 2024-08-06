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
#  limitations under the License.
from PySide6.QtWidgets import QMessageBox

from pyminflux.processor import MinFluxProcessor


def print_hello_world(processor: MinFluxProcessor):
    """Example of a method imported from a different module in the same plug-in."""

    # Adapt the text depending on whether we have data in memory or not
    if processor is None or len(processor.filtered_dataframe.index) == 0:
        text = "Hello, World!"
    else:
        text = f"Hello, World from '{processor.reader.filename.name}'!"

    # Show a message box
    QMessageBox.information(None, "Plugin", text)
