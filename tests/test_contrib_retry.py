import socket
from urllib2 import URLError
import pytest

from amazonproduct.api import API
from amazonproduct.contrib.retry import RetryAPI

@pytest.mark.slowtest
def test_timeout(monkeypatch):
    """
    Check that in case of a timeout API will not give up easily.
    """

    class mock_fetch (object):
        def __init__(self):
            self.calls = 0
        def __call__(self, _, url):
            self.calls += 1
            print 'call %i: %s' % (self.calls, url)
            raise URLError(socket.timeout())

    fetcher = mock_fetch()
    monkeypatch.setattr(API, '_fetch', fetcher)

    api = RetryAPI(locale='de')

    itworked = False
    try:
        api.call(operation='DummyOperation')
        itworked = True
    except URLError, e:
        assert isinstance(e.reason, socket.timeout)

    # timeout WAS raised and fetch was called TRIES times
    assert not itworked
    assert fetcher.calls == api.TRIES