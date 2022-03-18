import pytest

from grader.utils import retry


@pytest.mark.parametrize("n_times", [i + 1 for i in range(9)])
@pytest.mark.parametrize("raise_exc", (Exception, ValueError, IOError))
def test_retry_matching_exception(n_times, raise_exc):
    """
    when exception raised matches exception to handle, exceptions are captured
    until retries exceeded"""

    class C:
        calls = 0

        @retry(n_times, raise_exc)
        def m(self):
            self.calls += 1
            raise raise_exc

    i = C()

    with pytest.raises(
        Exception, match=f"method <(.*)> did not succeed after {n_times} retries"
    ):
        i.m()

    assert i.calls == n_times


@pytest.mark.parametrize("n_times", [i + 1 for i in range(9)])
@pytest.mark.parametrize("raise_exc", (Exception, ValueError, IOError))
def test_retry_mismatched_exception(n_times, raise_exc):
    """When handled exception is narrow, the actual exception will bubble
    up immediately if it's not expected"""

    class MyException(Exception):
        ...

    class C:
        calls = 0

        @retry(n_times, MyException)
        def m(self):
            self.calls += 1
            raise raise_exc

    i = C()

    with pytest.raises(raise_exc):
        i.m()

    # now, it's always 1 call, because the exception bubbles out of the wrapper
    # on the first call
    assert i.calls == 1
