import concurrent.futures
import time


def _task(knp):
    text = "今日はいい天気だった"
    blist = knp.parse(text)
    assert text == "".join(b.midasi for b in blist)


def test_knp(knp):
    _task(knp)


def test_knp_multithread(knp):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_task, knp)
        while future.running():
            time.sleep(0.1)
        future.result()
