
from datetime import datetime, timedelta
import pytest
import os.path

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse
    from cgi import parse_qs

from tests import TESTABLE_API_VERSIONS, XML_TEST_DIR
from tests.utils import convert_camel_case, extract_operations_from_wsdl
from server import TestServer

from amazonproduct import API
from amazonproduct import UnknownLocale, TooManyRequests

class TestAPILocales (object):

    """
    Testing initialising API with different locales.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def test_fails_for_invalid_locale(self):
        pytest.raises(UnknownLocale, API, self.ACCESS_KEY,
                self.SECRET_KEY, locale='XX')


class TestAPICalls (object):

    """
    Test API calls with ``TestServer`` instance.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def setup_class(cls):
        cls.api = API(cls.ACCESS_KEY, cls.SECRET_KEY, 'uk')
        cls.server = TestServer()
        cls.api.host = ('%s:%i' % cls.server.server_address, )
        cls.server.start()

    def teardown_class(cls):
        cls.server.stop()

    def test_fails_for_too_many_requests(self):
        xml = os.path.join(XML_TEST_DIR,
            'APICalls-fails-for-too-many-requests.xml')
        self.server.serve_file(xml, 503)
        pytest.raises(TooManyRequests, self.api.item_lookup, '9780747532743', 
            IdType='ISBN', SearchIndex='All', ResponseGroup='???')

    @pytest.mark.slowtest
    def test_call_throtteling(self):
        url = self.api._build_url(Operation='ItemSearch', SearchIndex='Books')
        self.server.code = 200
        start = datetime.now()
        n = 3
        for i in range(n):
            self.api._fetch(url)
        stop = datetime.now()
        assert (stop-start) >= (n-1)*self.api.throttle

class TestAPICallsWithOptionalParameters (object):

    """
    Tests that optional parameters (like AssociateTag) end up in URL.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def test_associate_tag_is_written_to_url(self):
        tag = 'ABC12345'
        api = API(self.ACCESS_KEY, self.SECRET_KEY, 'de', associate_tag=tag)
        url = api._build_url(Operation='ItemSearch', SearchIndex='Books')

        qs = parse_qs(urlparse(url)[4])
        assert qs['AssociateTag'][0] == tag


def pytest_generate_tests(metafunc):
    # called once per each test function
    if 'api' in metafunc.funcargnames and 'operation' in metafunc.funcargnames:
        for version in TESTABLE_API_VERSIONS:
            wsdl = os.path.join(XML_TEST_DIR, version, 
                'AWSECommerceService.wsdl')
            if not os.path.exists(wsdl):
                continue
            api = API('', '', 'de')
            api.VERSION = version
            for operation in extract_operations_from_wsdl(wsdl):
                metafunc.addcall(
                    id='%s/%s' % (version, operation),
                    funcargs={'api' : api, 'operation' : operation})

def test_API_coverage(api, operation):
    """
    Tests if API class supports all operations which are in the official WSDL
    from Amazon.
    """
    # a few operations are not yet implemented!
    notyetimpltd = 'SellerLookup SellerListingLookup SellerListingSearch'
    if operation in notyetimpltd.split():
        pytest.xfail('Not yet fully implemented!')

    attr = convert_camel_case(operation)
    assert hasattr(api, attr), 'API does not support %s!' % operation

