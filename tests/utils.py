
from lxml import etree
import os.path
import re
from StringIO import StringIO
import urllib2

from amazonproduct import API, AWSError

from tests import XML_TEST_DIR, TESTABLE_API_VERSIONS, TESTABLE_LOCALES
from tests import AWS_KEY, SECRET_KEY, OVERWRITE_TESTS 

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


def convert_camel_case(operation):
    """
    Converts ``CamelCaseOperationName`` into ``python_style_method_name``.
    """
    return re.sub('([a-z])([A-Z])', r'\1_\2', operation).lower()
