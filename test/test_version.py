import pytest

import pyminflux


def test_version():
    assert pyminflux.__version__ != "", "pyMinFlux version not set."
