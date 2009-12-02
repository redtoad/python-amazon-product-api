from lxml import etree, objectify
import os, os.path
import re
from StringIO import StringIO
import unittest
import urllib2

from amazonproduct import API, InvalidItemId

try:
    from config import AWS_KEY, SECRET_KEY
except ImportError:
    import os
    AWS_KEY = os.environ.get('AWS_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')

class CustomAPI (API):
    
    """
    Uses stored XML responses from local files (or retrieves them from Amazon 
    if they are not present yet).
    """
    
    def _call(self, url):
        """
        Uses XML response from (or stores in) local file.
        """
        
        if not os.path.exists(self.local_file):
            tree = objectify.parse(API._call(self, url))
            root = tree.getroot()
            
            # overwrite sensible data
            nspace = root.nsmap.get(None, '')
            for arg in root.xpath('//aws:Arguments/aws:Argument',
                                  namespaces={'aws' : nspace}):
                if arg.get('Name') in 'AWSAccessKeyId Signature':
                    arg.set('Value', 'X'*15)
            
            data = etree.tostring(root, pretty_print=True)
            local_dir = os.path.dirname(self.local_file)
            if not os.path.exists(local_dir):
                #print 'creating %s...' % local_dir
                os.mkdir(local_dir)
                
            fp = open(self.local_file, 'wb')
            #print 'storing response in %s...' % self.local_file 
            fp.write(data)
            fp.close()
            return StringIO(data)
            
        return open(self.local_file, 'rb')


class XMLResponseTestCase (unittest.TestCase):
    
    """
    Test case which uses local XML files rather than making HTTP calls. 
    """
    
    def setUp(self):
        """
        Method called to prepare the test fixture. This is called immediately 
        before calling the test method.
        """
        self.api = CustomAPI(AWS_KEY, SECRET_KEY)
        self.api.local_file = self.get_local_response_file()
        
    def get_local_response_file(self):
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
        
