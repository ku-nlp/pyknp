
import pytest

import pyknp


@pytest.fixture
def knp():
    return pyknp.KNP()


@pytest.fixture
def knp_multithread():
    return pyknp.KNP(multithreading=True)
