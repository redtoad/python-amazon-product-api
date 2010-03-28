
from server import TestServer
from threading import Thread
import unittest

# Preprend parent directory to PYTHONPATH to ensure that this amazonproduct
# module can be imported and will take precedence over an existing one
import os.path, sys
_here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_here, '..'))

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
        self.api = API(self.ACCESS_KEY, self.SECRET_KEY)
        self.server = TestServer()
        self.api.scheme = 'http'
        self.api.host = '%s:%i' % self.server.server_address
        
        Thread(target=self.server.serve_forever).start()
        print 'Test server running at http://%s:%i' % self.server.server_address
        
    def test_fails_for_too_many_requests(self):
        self.server.serve_file(code=503)
        self.assertRaises(TooManyRequests, self.api.item_lookup, 
                          '9780747532743', IdType='ISBN', SearchIndex='All', 
                          ResponseGroup='???')
        
if __name__ == '__main__':
    unittest.main()
