
from lxml import etree
import nose.loader
import os.path
import re
from StringIO import StringIO
import unittest
import urllib2

_here = os.path.abspath(os.path.dirname(__file__))

# Prepend parent directory to PYTHONPATH to ensure that this amazonproduct
# module can be imported and will take precedence over an existing one
import sys
sys.path.insert(0, os.path.join(_here, '..'))

from amazonproduct.api import API, HOSTS
from amazonproduct.errors import AWSError

#: Directory containing XML responses for API versions (one directory for each
#: API version)
XML_TEST_DIR = _here

#: Versions of Amazon API to be tested against 
TESTABLE_API_VERSIONS = [
    '2010-12-01', '2010-11-01', '2010-10-01', '2010-09-01', '2010-06-01',
    '2009-11-01', '2009-10-01'
]

#: Locales to test against. 
TESTABLE_LOCALES = HOSTS.keys()

ALL = 'all'

def get_config_value(key, default=None):
    """
    Loads value from config.py or from environment variable or return default
    (in that order).
    """
    try:
        config = __import__('config')
        return getattr(config, key)
    except (ImportError, AttributeError):
        return os.environ.get(key, default)

AWS_KEY = get_config_value('AWS_KEY', '')
SECRET_KEY = get_config_value('SECRET_KEY', '')
OVERWRITE_TESTS = get_config_value('OVERWRITE_TESTS', False)

class CustomAPI (API):
    
    """
    Uses stored XML responses from local files (or retrieves them from Amazon 
    if they are not present yet). The number of calls via a particular API 
    instance is tracked and local files are named accordingly.
    """
    
    def __init__(self, *args, **kwargs):
        super(CustomAPI, self).__init__(*args, **kwargs)
        self.calls = 0
    
    def _fetch(self, url):
        """
        Uses XML response from (or stores in) local file.
        """
        # subsequent calls of this API instance
        # will be stored in different files
        self.calls += 1
        path = self.local_file
        if self.calls > 1:
            head, tail = os.path.splitext(self.local_file)
            path = head + '-%i' % self.calls + tail
        
        # If the XML response has not been previously fetched:
        # retrieve it, obfuscate all sensible data and store it 
        # with the name of the TestCase using it
        if not os.path.exists(path) or OVERWRITE_TESTS:
            try:
                fp = API._fetch(self, url)
            except urllib2.HTTPError, e:
                # HTTP errors 400 (Bad Request) and 410 (Gone) send a more 
                # detailed error message as body which can be parsed, too.
                if e.code in (400, 410):
                    fp = e.fp
                # otherwise re-raise
                else:
                    raise
            try:
                tree = etree.parse(fp)
            except AWSError:
                pass
            root = tree.getroot()
            
            # overwrite sensible data
            nspace = root.nsmap.get(None, '')
            for arg in root.xpath('//aws:Arguments/aws:Argument',
                                  namespaces={'aws' : nspace}):
                if arg.get('Name') in 'AWSAccessKeyId Signature':
                    arg.set('Value', 'X'*15)
                    
            xml = etree.tostring(root, pretty_print=True)
            if AWS_KEY!='' and SECRET_KEY!='':
                xml = xml.replace(AWS_KEY, 'X'*15)
                xml = xml.replace(SECRET_KEY, 'X'*15)
            
            local_dir = os.path.dirname(path)
            if not os.path.exists(local_dir):
                #print 'creating %s...' % local_dir
                os.mkdir(local_dir)
                
            fp = open(path, 'wb')
            #print 'storing response in %s...' % self.local_file 
            fp.write(xml)
            fp.close()
            return StringIO(xml)
            
        return open(path, 'rb')


class XMLResponseTestCase (unittest.TestCase):
    
    """
    Test case which uses local XML files rather than making HTTP calls.
    
    You can specify which API versions this test case should be run against by
    providing a class attribute ``api_versions`` with a list of your choices.
    For all versions, set it to ``ALL`` or leave blank. 
    
    The same works for locales.
    
    Example::
        
        class MySpecialTest (XMLResponseTestCase):
            api_versions = ['2009-10-01']
            locale = ['us']
            def test_something(self):
                ...
                
    """
    
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.current_locale = 'de'
        self.current_api_version = TESTABLE_API_VERSIONS[-1]

        # make TestCase Python2.4 compatible
        if not hasattr(self, '_testMethodName'):
            self._testMethodName = self._TestCase__testMethodName
        
    def setUp(self):
        """
        Method called to prepare the test fixture. This is called immediately 
        before calling the test method. The API version for the current test
        is stored in attribute ``current_api_version``.
        """
#        self.current_api_version = self._versions_to_test.pop(0)
        self.api = CustomAPI(AWS_KEY, SECRET_KEY, self.current_locale)
        self.api.VERSION = self.current_api_version
        self.api.local_file = os.path.join(XML_TEST_DIR,
                self.get_local_response_file(self.current_locale))
        
    def get_local_response_file(self, locale):
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
        return '%s/%s-%s-%s.xml' % (version, klass, locale, method)
    
    def __str__(self):
        cls = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return "%s (%s [API %s locale:%s])" % (self._testMethodName, cls, 
                         self.current_api_version, self.current_locale)
    

class XMLResponseTestLoader (nose.loader.TestLoader):
    
    """
    Custom test loader which adds one separate test case for each API version 
    and each locale.
    """
    
    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained in testCaseClass"""
        if not issubclass(testCaseClass, XMLResponseTestCase):
            return super(XMLResponseTestLoader, self).loadTestsFromTestCase(testCaseClass)
            
        testCaseNames = self.getTestCaseNames(testCaseClass)
        tests = []
        for locale in getattr(testCaseClass, 'locales', TESTABLE_LOCALES):
            for api_version in getattr(testCaseClass, 'api_versions', TESTABLE_API_VERSIONS):
                for testCaseName in testCaseNames:
                    testCase = testCaseClass(testCaseName)
                    testCase.current_locale = locale
                    testCase.current_api_version = api_version
                    tests += [testCase]
        return self.suiteClass(tests)
