import pytest

import time

from inventory_explorer.background_processing import CachedBackgroundCall


class TestCachedBackgroundCall:
    def test_success(self) -> None:
        cbc = CachedBackgroundCall(lambda: [1, 2, 3])

        result = cbc()
        assert result == [1, 2, 3]

        # The original output should be cached
        assert cbc() is result

    def test_failure(self) -> None:
        class MyException(Exception):
            pass

        def fail() -> None:
            raise MyException()

        cbc = CachedBackgroundCall(fail)

        with pytest.raises(MyException) as first_exc_info:
            cbc()

        with pytest.raises(MyException) as second_exc_info:
            cbc()

        # Exception should be cached too!
        assert first_exc_info.value is second_exc_info.value

    def test_blocking(self) -> None:
        cbc = CachedBackgroundCall(lambda: time.sleep(0.3))

        assert not cbc.ready
        time.sleep(0.1)
        assert not cbc.ready

        # Should take the remaining time (to proove we were already running)
        before = time.monotonic()
        cbc()
        after = time.monotonic()
        assert 0.15 < (after - before) < 0.25

        assert cbc.ready

        # Should be instant
        before = time.monotonic()
        cbc()
        after = time.monotonic()
        assert after - before < 0.1
