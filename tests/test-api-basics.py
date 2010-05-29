
import os.path
from server import TestServer
import unittest

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
        self.server = TestServer(port=8002)
        self.api.host = '%s:%i' % self.server.server_address
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
        
if __name__ == '__main__':
    unittest.main()
