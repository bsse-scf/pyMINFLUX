#  Copyright (c) 2022 - 2025 D-BSSE, ETH Zurich.
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

import ctypes
import importlib.util
import json
import platform
from json import JSONDecodeError
from pathlib import Path
from typing import Union

from pyminflux.plugin import Plugin
from pyminflux.processor import MinFluxProcessor


class PluginManager:
    def __init__(self, plugins_dir: Union[Path, str]):
        """Constructor.

        Parameters
        ----------

        plugins_dir: Union[Path, str]
            Full path to the plugins' directory.
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins = []

    def execute_plugin(self, index: int, processor: MinFluxProcessor, *args, **kwargs):
        """Execute the requested plugin passing a reference to the processor.

        Parameters
        ----------

        index: int
            Index of the plugin in self.plugins.

        processor: MinFluxProcessor
            Reference to the MinFluxProcessor instance.
        """
        return self.plugins[index].execute(processor, *args, **kwargs)

    def get_plugin_info(self):
        """Return the plugin information."""
        return [plugin.get_info() for plugin in self.plugins]

    def load_plugins(self):
        """Load all plugins from plugins_dir."""
        for item in self.plugins_dir.iterdir():
            if item.is_dir():
                try:
                    self._load_plugin(item)
                except (OSError, IOError, JSONDecodeError) as e:
                    print(f"Error loading plugin '{item.name}': {e}")

    def _create_plugin_module(self, plugin_dir: Path):
        """Create and return the plugin module.

        Please mind that the returned module could be called from another plug-in.
        Use _create_sandboxed_plugin_module() instead.

        Parameters
        ----------

        plugin_dir: str
            Full path to current plugin's directory.

        Returns
        -------

        plugin_module: module
            Loaded Python module.
        """

        # Load the module
        package_name = plugin_dir.name
        plugin_module = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(package_name, None)
        )

        # Add all python modules
        for module_path in plugin_dir.glob("*.py"):
            spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name in dir(module):
                if not name.startswith("__"):
                    setattr(plugin_module, name, getattr(module, name))

        # Combine DLL and SO files
        shared_libs = list(plugin_dir.glob("*.dll")) + list(plugin_dir.glob("*.so"))

        # Load shared libraries
        for lib_path in shared_libs:
            lib_name = lib_path.stem
            if platform.system() == "Windows":
                library = ctypes.WinDLL(str(lib_path))
            else:
                library = ctypes.CDLL(str(lib_path))
            setattr(plugin_module, lib_name, library)

        return plugin_module

    def _create_sandboxed_plugin_module(self, plugin_dir: Path):
        """Create and return the plugin module."""

        # Load the module
        package_name = plugin_dir.name
        plugin_module = importlib.util.module_from_spec(
            importlib.util.spec_from_loader(package_name, None)
        )

        # Custom globals for sandboxing
        sandbox_globals = {
            "__builtins__": {
                **__builtins__,
                "__import__": lambda name, globals=None, locals=None, fromlist=(), level=0: self._restricted_import(
                    name, globals, locals, fromlist, level, package_name
                ),
            },
            "__name__": package_name,
            "__file__": str(plugin_dir),
            "__path__": str(plugin_dir),
            "Plugin": Plugin,
            "MinFluxProcessor": MinFluxProcessor,
        }

        # Load python files
        for module_path in plugin_dir.glob("*.py"):
            with open(module_path) as file:
                exec(file.read(), sandbox_globals)

        # Combine DLL and SO files
        shared_libs = list(plugin_dir.glob("*.dll")) + list(plugin_dir.glob("*.so"))

        # Load shared libraries
        for lib_path in shared_libs:
            lib_name = lib_path.stem
            if platform.system() == "Windows":
                library = ctypes.WinDLL(str(lib_path))
            else:
                library = ctypes.CDLL(str(lib_path))
            sandbox_globals[lib_name] = library

        # Add module items
        for name, obj in sandbox_globals.items():
            if not name.startswith("__"):
                setattr(plugin_module, name, obj)

        return plugin_module

    def _find_plugin_class(self, plugin_module):
        """Find and return the Plugin class implementation from the module.

        Parameters
        ----------

        plugin_module: Python module
            Python module subclassing pyminflux.plugin.Plugin.

        Returns
        -------

        item:
            Python module subclassing the pyminflux.plugin.Plugin class.

        """
        for item_name in dir(plugin_module):
            item = getattr(plugin_module, item_name)
            if (
                isinstance(item, type)
                and issubclass(item, Plugin)
                and item is not Plugin
            ):
                return item
        return None

    def _initialize_plugin(self, plugin_class, metadata: dict) -> Plugin:
        """Initialize the plugin class with its metadata.

        Parameters
        ----------

        plugin_class: pyminflux.plugin.Plugin.
            Python module subclassing pyminflux.plugin.Plugin.

        metadata: dict
            Dictionary of plugin metadata.

        Returns
        -------

        item:
            Python module subclassing the pyminflux.plugin.Plugin class.

        """
        plugin = plugin_class()
        plugin.name = metadata.get("name", plugin.name)
        plugin.description = metadata.get("description", plugin.description)
        plugin.version = metadata.get("version", plugin.version)
        plugin.author = metadata.get("author", plugin.author)
        plugin.email = metadata.get("email", plugin.email)
        plugin.license = metadata.get("license", plugin.license)
        plugin.url = metadata.get("url", plugin.url)
        return plugin

    def _load_metadata(self, plugin_dir: Path) -> dict:
        """Load the metadata.json file.

        Parameters
        ----------

        plugin_dir: str
            Full path to current plugin's directory.

        Returns
        -------

        metadata: dict
            Loaded JSON as a Python dictionary.
        """
        metadata_file = plugin_dir / "metadata.json"
        if not metadata_file.is_file():
            raise IOError(f"Could not find metadata.json in {plugin_dir}")

        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
        except OSError as e:
            raise OSError(f"Could not open metadata.json in {plugin_dir}: {e}")
        except JSONDecodeError as e:
            raise JSONDecodeError(
                f"Could not decode metadata.json in {plugin_dir}: {e}",
                doc=e.doc,
                pos=e.pos,
            )

        return metadata

    def _load_plugin(self, plugin_dir: Path):
        """Load the specified plugin.

        Parameters
        ----------
        plugin_dir : Path
            Full path to current plugin's directory.
        """

        # Load metadata (may throw an exception)
        metadata = self._load_metadata(plugin_dir)

        # Create the module for the plugin
        plugin_module = self._create_sandboxed_plugin_module(plugin_dir)

        # Return the Plugin subclass defined in the module
        plugin_class = self._find_plugin_class(plugin_module)

        # If the class was found, initialize the plugin passing the extracted metadata
        if plugin_class:
            plugin = self._initialize_plugin(plugin_class, metadata)
            self.plugins.append(plugin)
        else:
            raise ImportError(
                f"Could not find a valid plugin class in {plugin_dir.name}"
            )

    def _restricted_import(
        self, name, globals=None, locals=None, fromlist=(), level=0, package_name=None
    ):
        """Custom import function to restrict imports within the sandbox.

        The module can import everything, but access to other plug-ins is restricted.
        """
        if name.startswith("plugins.") and not name.startswith(
            f"plugins.{package_name}"
        ):
            raise ImportError(f"Importing module '{name}' is restricted")
        return __import__(name, globals, locals, fromlist, level)
