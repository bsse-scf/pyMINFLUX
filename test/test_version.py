#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.

import pytest

import pyminflux


def test_version():
    assert pyminflux.__version__ != "", "pyMinFlux version not set."
