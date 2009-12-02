
"""
"""

import os, os.path
import re
import unittest
import urllib2

from amazonproduct import API, InvalidItemId

try:
    from config import AWS_KEY, SECRET_KEY
except ImportError:
    import os
    AWS_KEY = os.environ.get('AWS_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')


class XMLResponseTestCase (unittest.TestCase):
    
    """
    Test case which uses local XML files rather than making HTTP calls. 
    """
    
    def setUp(self):
        """
        Method called to prepare the test fixture. This is called immediately 
        before calling the test method.
        """
        self.api = API(AWS_KEY, SECRET_KEY)
        self.response = open(self._get_sample_response_file())
        
    def _get_sample_response_file(self):
        """
        Constructs name for local XML file based on API version, TestCase and 
        test method. ``Test``, ``TestCase`` and ``test`` is omitted from names.
        For instance: ``ItemLookupTestCase.test_invalid_item_id`` will have an
        XML response in file ``ItemLookup-invalid-item-id``.
        """
        version = self.api.VERSION
        klass = re.search(r'(\w+?)Test(Case)?', self.__class__.__name__).group(1)
        method = re.search(r'test_?(\w+)', self._testMethodName).group(1)
        method = method.replace('_', '-') 
        return '%s/%s-%s.xml' % (version, klass, method)
    
        
class ItemLookupTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for ItemLookup are parse correctly.
    """
     
    def test_invalid_item_id(self):
        self.assertRaises(InvalidItemId, self.api.item_lookup, '1234567890123')
        
    def test_valid_asin(self):
        # Harry Potter and the Philosopher's Stone
        self.api.item_lookup('0747532745')
        
    def test_valid_isbn(self):
        # Harry Potter and the Philosopher's Stone
        self.api.item_lookup('9780747532743', IdType='ISBN', SearchIndex='All')
        
    def test_valid_isbn_no_searchindex(self):
        # Harry Potter and the Philosopher's Stone
        self.api.item_lookup('9780747532743', IdType='ISBN')
        
        
def collect_sample_files():
    """
    Collects all XML responses from Amazon and stores them in local files.
    """
    module = __import__('__main__')
    suites = unittest.defaultTestLoader.loadTestsFromModule(module)
    for suite in suites:
        for test in suite._tests:
            
            class CustomAPI (API):
                def _call(self, url):
                    "Stores XML response in local file."
                    fp = open(self.local_file, 'wb')
                    print 'storing response in %s...' % self.local_file 
                    fp.write(urllib2.urlopen(url).read())
                    fp.close() 
                    return API._call(self, url)
                
            def custom_testcase_setUp(slf):
                "Replaces the standard setUp method to invoke a custom API."
                slf.api = CustomAPI(AWS_KEY, SECRET_KEY)
                slf.api.local_file = slf._get_sample_response_file()
                local_dir = os.path.dirname(slf.api.local_file)
                if not os.path.exists(local_dir):
                    print 'creating %s...' % local_dir
                    os.mkdir(local_dir)
            
            result = test.defaultTestResult()
            test.setUp = lambda: custom_testcase_setUp(test)
            test.run(result)
            
            for testcase, traceback in result.errors:
                print testcase
                print traceback
    
if __name__ == '__main__':
    collect_sample_files()
