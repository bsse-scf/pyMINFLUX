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
import pytest

from pyminflux.reader.util import version_str_to_int


def test_version_str_to_int():

    # Valid entries
    assert version_str_to_int("1.0") == 10000
    assert version_str_to_int("1.0.1") == 10001
    assert version_str_to_int("2.0") == 20000
    assert version_str_to_int("2.1.0") == 20100

    # Invalid entries
    with pytest.raises(ValueError):
        _ = version_str_to_int("2.")
        _ = version_str_to_int("2.0.0.1")
        _ = version_str_to_int("2.a.1")
        _ = version_str_to_int("-2.0.0")
