
import os.path
from server import TestServer
from datetime import datetime, timedelta
import unittest
from urlparse import urlparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

# import base first because sys.path is changed in order to find amazonproduct!
import base

from amazonproduct import API
from amazonproduct import UnknownLocale, TooManyRequests

class LocalesTestCase (unittest.TestCase):

    """
    Testing initialising API with different locales.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def test_fails_for_invalid_locale(self):
        self.assertRaises(UnknownLocale, API, self.ACCESS_KEY,
                self.SECRET_KEY, locale='XX')


class APICallsTestCase (unittest.TestCase):

    """
    Test API calls with ``TestServer`` instance.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def setUp(self):
        self.api = API(self.ACCESS_KEY, self.SECRET_KEY, 'uk')
        self.server = TestServer()
        self.api.host = ('%s:%i' % self.server.server_address, )
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_fails_for_too_many_requests(self):
        xml = os.path.join(base.XML_TEST_DIR,
            'APICalls-fails-for-too-many-requests.xml')
        self.server.serve_file(xml, 503)
        self.assertRaises(TooManyRequests, self.api.item_lookup,
                          '9780747532743', IdType='ISBN', SearchIndex='All',
                          ResponseGroup='???')

    def test_call_throtteling(self):
        url = self.api._build_url(Operation='ItemSearch', SearchIndex='Books')
        self.server.code = 200
        start = datetime.now()
        n = 3
        for i in range(n):
            self.api._fetch(url)
        stop = datetime.now()
        self.assert_((stop-start) >= (n-1)*self.api.throttle)

class APICallsWithOptionalParameters (unittest.TestCase):

    """
    Tests that optional parameters (like AssociateTag) end up in URL.
    """

    ACCESS_KEY = SECRET_KEY = ''

    def test_associate_tag_is_written_to_url(self):
        tag = 'ABC12345'
        api = API(self.ACCESS_KEY, self.SECRET_KEY, 'de', associate_tag=tag)
        url = api._build_url(Operation='ItemSearch', SearchIndex='Books')

        qs = parse_qs(urlparse(url)[4])
        self.assertEquals(qs['AssociateTag'][0], tag)


