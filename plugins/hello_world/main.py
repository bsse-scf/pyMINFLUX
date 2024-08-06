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
# Use plugins.<plugin>.<module> to import from other .py files
from plugins.hello_world.other import print_hello_world
from pyminflux.plugin import Plugin, plugin_entry
from pyminflux.processor import MinFluxProcessor


class HelloWorld(Plugin):
    """The Plugin class must inherit from pyminflux.plugin.Plugin."""

    @plugin_entry
    def main(self, processor: MinFluxProcessor):
        """The plugin entry method will be passed a reference to the MinFluxProcessor instance."""
        print_hello_world(processor)
