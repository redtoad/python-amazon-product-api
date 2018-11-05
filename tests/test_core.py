import datetime
import os.path

import pytest

from amazonproduct import core

import requests_mock

adapter = requests_mock.Adapter()
_here = os.path.dirname(os.path.abspath(__file__))


class MockBackend(object):

    """
    Mock object for ``requests.get()``
    """

    def __init__(self, node=None):
        self.paths = []
        self.test_node = node

    def add(self, *paths):
        self.paths.extend(paths)

    def get(self, url, *args, **kwargs):
        path = os.path.join(_here, self.paths.pop(0))
        return open(path, 'rb')


@pytest.fixture(scope='function')
def backend(request, monkeypatch):
    mock = MockBackend(request.node)
    monkeypatch.setattr(core.requests, 'get', mock.get)
    return mock


class MockSigner(object):

    """
    Mocks :meth:`~amazonproduct.core.signed_url` and retains all call arguments as
    fields for later assertions.
    """

    def __init__(self):
        self.host = self.access_key = self.secret_key = self.associate_tag = None
        self.qargs = {}

    def __call__(self, host, access_key, secret_key, associate_tag, **qargs):
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag
        self.qargs = qargs
        return 'https://example.org'


@pytest.fixture
def signer(monkeypatch):
    mock = MockSigner()
    monkeypatch.setattr(core, 'signed_url', mock)
    return mock


# generated signed URL from https://webservices.amazon.de/scratchpad/
TEST_SIGNED_URL = (
    'https://webservices.amazon.de/onca/xml?'
    'AWSAccessKeyId=XXXX&AssociateTag=xxxx-21'
    '&Operation=ItemSearch'
    '&ResponseGroup=Images%2CItemAttributes%2COffers'
    '&SearchIndex=All'
    '&Service=AWSECommerceService'
    '&Timestamp=2018-07-19T09%3A45%3A39.000Z'
    '&Signature=okoD3LeyKG37VNwCvI2%2BGc44RN%2FEKaRgghTjdHfvJe0%3D')


def test_sign_url(monkeypatch):
    now = datetime.datetime(2018, 7, 19, 9, 45, 39, 0)
    class mydatetime:
        @classmethod
        def now(cls):
            return now
    monkeypatch.setattr(datetime, 'datetime', mydatetime)

    assert TEST_SIGNED_URL == core.signed_url(
        'webservices.amazon.de',
        'XXXX', 'XXXX', 'xxxx-21',
        AWSAccessKeyId='XXXX',
        AssociateTag='xxxx-21',
        Operation='ItemSearch',
        Sort=None,
        ResponseGroup='Images,ItemAttributes,Offers',
        SearchIndex='All')


def test_api_fails_for_unsupported_locale():
    with pytest.raises(core.UnknownLocale):
        api = core.CoreAPI('access', 'secret', 'XX', 'tag')
        api(Operation='Something')


def test_api_call(backend, signer):
    backend.add('ItemSearch-test-page-1.xml')
    api = core.CoreAPI('access', 'secret', 'de', 'tag')
    api(Operation='ItemSearch',
        SearchIndex='Books',
        Conditions='All',
        Author='Aaronovitch',
        ResponseGroup='Large')
    assert signer.qargs == dict(
        Operation='ItemSearch',
        SearchIndex='Books',
        Conditions='All',
        Author='Aaronovitch',
        Version=api.DEFAULT_VERSION,
        ResponseGroup='Large'
    )


def test_specify_version(signer):
    api = core.CoreAPI('access', 'secret', 'de', 'tag')
    api.ItemSearch(Version='xxx')
    assert signer.qargs['Version'] == 'xxx'


def test_allow_responsegroup_lists(signer):
    api = core.CoreAPI('access', 'secret', 'de', 'tag')
    api.ItemSearch(ResponseGroup=['Large', 'Reviews'])
    assert signer.qargs['ResponseGroup'] == 'Large,Reviews'


@pytest.mark.parametrize('operation', core.CoreAPI.OPERATIONS)
def test_api_shortcuts(backend, signer, operation):
    backend.add('ItemSearch-test-page-1.xml')
    api = core.CoreAPI('access', 'secret', 'de', 'tag')
    op = getattr(api, operation)
    op(SearchIndex='Books', Conditions='All', Author='Aaronovitch')
    assert signer.qargs == dict(
        Operation=operation,
        SearchIndex='Books',
        Conditions='All',
        Author='Aaronovitch',
        Version=api.DEFAULT_VERSION
    )


def test_api_shortcuts_cause_no_indefinite_recursion():
    with pytest.raises(AttributeError):
        api = core.CoreAPI('access', 'secret', 'de', 'tag')
        api.does_not_exist()


