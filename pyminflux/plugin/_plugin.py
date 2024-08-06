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

from abc import ABC

from pyminflux.processor import MinFluxProcessor


def plugin_entry(func):
    """Decorator to label function 'func' as the Plugin entry point.

    Parameters
    ----------

    func : callable
        Function to be decorated.

    Returns
    -------
    funct: callable
        Decorated function.
    """
    func.is_plugin_entry = True
    return func


class Plugin(ABC):
    def __init__(self):
        """Constructor."""
        self.name = "Unnamed Plugin"
        self.description = "No description provided"
        self.version = "0.0"
        self.author = "Unknown"
        self.license = "Unknown"
        self.email = "Unknown"
        self.url = "Unknown"

    def get_info(self):
        """Return the plugin information (as read from metadata.json)."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "license": self.license,
            "email": self.email,
            "url": self.url,
        }

    def execute(self, processor: MinFluxProcessor, *args, **kwargs):
        """Execute the plugin.

        Parameters
        ----------

        processor: MinFluxProcessor
            Reference to the MinFluxProcessor instance. It can be None if no data has been loaded.

        Returns
        -------

        out: Object
            Output of the plugin.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "is_plugin_entry"):
                """Return the function that has been labeled as entry point for the plugin."""
                return attr(processor, *args, **kwargs)
        raise NotImplementedError("No plugin entry point found in the plugin.")
