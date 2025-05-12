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

import pyminflux
from pyminflux.utils._utils import check_for_updates


def test_version():
    assert pyminflux.__version__ != "", "pyMINFLUX version not set."
    assert len(pyminflux.__version__.split(".")) == 3, (
        "The version number should be " "in the format " "x.y.z."
    )


def test_retrieve_version_from_server():
    """Try retrieving version information from the server."""
    code, version, error = check_for_updates()

    assert code != -1, "Retrieving the version number should not fail!"
    assert version != "", "The version number should be retrieved!"
    assert len(version.split(".")) == 3, (
        "The version number should be in the format " "x.y.z."
    )
