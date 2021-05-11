
import pytest

import pyknp


@pytest.fixture
def knp():
    return pyknp.KNP(multithreading=True)
