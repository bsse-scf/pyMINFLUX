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

import re

import requests

import pyminflux


def check_for_updates():
    """Check for pyMINFLUX updates.

    Returns
    -------

    code: int
        Success code:
        -1: something went wrong retrieving version information.
         0: there are no new versions.
         1: there is a new version.
    version: str
        Version on the server (in the format x.y.z). Set if code is 0 or 1.
    error: str
        Error message. Only set if code is -1.
    """

    # Initialize outputs
    code = -1
    version = ""
    error = ""

    # Get the redirect from the latest release URL
    response = requests.get(
        "https://github.com/bsse-scf/pyMINFLUX/releases/latest", allow_redirects=False
    )

    # This should redirect (status code 301 or 302)
    if response.status_code in (301, 302):
        redirect_url = response.headers["Location"]
    else:
        error = "Could not check for updates!"
        return code, version, error

    # Try retrieving the version string
    match = re.search(r"\b(\d+)\.(\d+)\.(\d+)$", redirect_url)
    if match:
        x, y, z = match.groups()
    else:
        error = "Could not retrieve version information from server!"
        return code, version, error

    # Set the version
    version = f"{x}.{y}.{z}"

    # Transform new version into an integer
    new_version = 10000 * int(x) + 100 * int(y) + int(z)

    # Current version
    parts = pyminflux.__version__.split(".")

    # Make sure that we have three parts
    if len(parts) != 3:
        error = "Could not retrieve current app information!"
        return code, version, error

    # Transform current version into an integer
    current_version = 10000 * int(parts[0]) + 100 * int(parts[1]) + int(parts[2])

    # Now check
    if new_version > current_version:
        code = 1
    else:
        code = 0

    # Return
    return code, version, error
