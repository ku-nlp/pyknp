import concurrent.futures
import time

import pytest

import pyknp


@pytest.fixture
def knp():
    return pyknp.KNP()


def task(knp):
    text = "今日はいい天気だった"
    blist = knp.parse(text)
    assert text == "".join(b.midasi for b in blist)


def test_knp(knp):
    task(knp)


def test_knp_multithread(knp):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(task, knp)
        while future.running():
            time.sleep(0.1)
        future.result()
