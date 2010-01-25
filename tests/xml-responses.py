from lxml import etree
import os, os.path
import re
from StringIO import StringIO
import unittest
import urllib2

from amazonproduct import API, ResultPaginator
from amazonproduct import AWSError
from amazonproduct import InvalidParameterValue, InvalidListType
from amazonproduct import InvalidSearchIndex, InvalidResponseGroup
from amazonproduct import NoSimilarityForASIN

def get_config_value(key, default=None):
    """
    Loads value from config.py or from environment variable or return default
    (in that order).
    """
    try:
        config = __import__('config')
        return getattr(config, key)
    except (ImportError, AttributeError):
        import os
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
    
    def _call(self, url):
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
        
        if not os.path.exists(path) or OVERWRITE_TESTS:
            tree = etree.parse(API._call(self, url))
            root = tree.getroot()
            
            # overwrite sensible data
            nspace = root.nsmap.get(None, '')
            for arg in root.xpath('//aws:Arguments/aws:Argument',
                                  namespaces={'aws' : nspace}):
                if arg.get('Name') in 'AWSAccessKeyId Signature':
                    arg.set('Value', 'X'*15)
                    
            xml = etree.tostring(root, pretty_print=True)
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
    Check that all XML responses for ItemLookup are parsed correctly.
    """
     
    def test_invalid_item_id(self):
        self.assertRaises(InvalidParameterValue, self.api.item_lookup, '1234567890123')
        
    def test_valid_asin(self):
        # Harry Potter and the Philosopher's Stone
        self.api.item_lookup('0747532745')
        
    def test_valid_isbn(self):
        # Harry Potter and the Philosopher's Stone
        self.api.item_lookup('9780747532743', IdType='ISBN', SearchIndex='All')
        
    def test_invalid_search_index(self):
        self.assertRaises(InvalidSearchIndex, self.api.item_lookup, 
                          '9780747532743', IdType='ISBN', SearchIndex='???')
        
    def test_invalid_response_group(self):
        self.assertRaises(InvalidResponseGroup, self.api.item_lookup, 
                          '9780747532743', IdType='ISBN', SearchIndex='All', 
                          ResponseGroup='???')
        
    def test_valid_isbn_no_searchindex(self):
        # Harry Potter and the Philosopher's Stone
        try:
            self.api.item_lookup('9780747532743', IdType='ISBN')
        except AWSError, e:
            self.assert_(e.code == 'AWS.MissingParameterValueCombination')
        
        
class ItemSearchTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for ItemSearch are parsed correctly.
    """
    
    def test_no_parameters(self):
        try:
            self.assertRaises(InvalidResponseGroup, 
                              self.api.item_search, 'Books')
        except AWSError, e:
            self.assert_(e.code == 'AWS.MinimumParameterRequirement')
        
    def test_invalid_response_group(self):
        self.assertRaises(InvalidResponseGroup, self.api.item_search, 
                          'All', ResponseGroup='???')
        
        
class SimilarityLookupTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for SimilarityLookup are parsed correctly.
    """
    
    def test_similar_items(self):
        # 0451462009 Small Favor: A Novel of the Dresden Files 
        root = self.api.similarity_lookup('0451462009')
        
        self.assert_(root.Items.Request.IsValid.pyval is True)
        self.assert_(len(root.Items.Item) > 0)
        
    def test_no_similar_items_for_two_asins(self):
        # 0451462009 Small Favor: A Novel of the Dresden Files
        # B0024NL0TG Oral-B toothbrush
        self.assertRaises(NoSimilarityForASIN, self.api.similarity_lookup,
                          '0451462009', 'B0024NL0TG')
        
        
class ListLookupTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for ListLookup are parsed correctly.
    """
     
    def test_invalid_list_id(self):
        self.assertRaises(InvalidParameterValue, self.api.list_lookup, '???', 'WishList')
        
    def test_invalid_list_type(self):
        self.assertRaises(InvalidListType, self.api.list_lookup, '???', '???')
        

class ResultPaginatorTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for pagination are parsed correctly.
    """
    
    def test_review_pagination(self):
        # reviews for 
        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews', 
            limit=10)
        
        for page, root in enumerate(paginator(self.api.item_lookup, 
                        '0747532745', ResponseGroup='Reviews')):
            
            total_reviews = root.Items.Item.CustomerReviews.TotalReviews.pyval
            review_pages = root.Items.Item.CustomerReviews.TotalReviewPages.pyval
            try:
                current_page = root.Items.Request.ItemLookupRequest.ReviewPage.pyval
            except AttributeError:
                current_page = 1
            
            self.assert_(total_reviews==2458)
            self.assert_(review_pages==492)
            self.assert_(current_page==page+1)
            
        self.assert_(page==9)

class HelpTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for Help are parsed correctly.
    """
    
    def _check_parameters(self, node, list):
        """
        Checks that all required parameters are contained in XML node.
        """
        self.assertEquals(node.countchildren(), len(list))
        for e in node.iterchildren():
            self.assertTrue(e.text in list)
            
    def _check_elements(self, node, list):
        """
        Checks that all required elements are contained in XML node.
        """
        self.assertEquals(len(node.Elements.Element), len(list))
        for e in node.Elements.Element:
            self.assertTrue(e.text in list)
        
    def test_help_operation(self):
        """
        Check API call ``Help`` for ``Operation`` ``Help``.
        """
        root = self.api.help('Help', 'Operation')
        self.assert_(root.Information.Request.IsValid.pyval is True)
        
        # check that all information is correct
        info = root.Information.OperationInformation
        self.assertEquals(info.Name.text, 'Help')
        
        self._check_parameters(info.RequiredParameters, 
                'About HelpType'.split())
        self._check_parameters(info.AvailableParameters, 
                'AssociateTag ContentType Marketplace MarketplaceDomain Style '
                'Validate Version XMLEscaping'.split())
        self._check_parameters(info.DefaultResponseGroups, 
                'Request Help'.split())
        self._check_parameters(info.AvailableResponseGroups, 
                'Request Help'.split())
        
    def test_help_responsegroup(self):
        """
        Check API call ``Help`` for ``ResponseGroup`` ``Help``.
        """
        root = self.api.help('Help', 'ResponseGroup')
        self.assert_(root.Information.Request.IsValid.pyval is True)
        
        # check that all information is correct
        info = root.Information.ResponseGroupInformation
        self.assertEquals(info.Name.text, 'Help')
        self.assertEquals(info.CreationDate.pyval, '2004-01-28')
        self.assertEquals(len(info.ValidOperations.Operation), 1)
        self.assertEquals(info.ValidOperations.Operation.pyval, 'Help')
        
        # check that all required elements are contained in XML
        elements = map(lambda x: x.strip(), '''Arguments/Argument/Name
        Arguments/Argument/Value
        Errors/Error/Code
        Errors/Error/Message
        OperationInformation/AvailableParameters/Parameter
        OperationInformation/AvailableResponseGroups/ResponseGroup
        OperationInformation/DefaultResponseGroups/ResponseGroup
        OperationInformation/Description
        OperationInformation/Name
        OperationInformation/RequiredParameters/Parameter
        OperationRequest/RequestId
        OperationRequest/UserAgent
        Request/IsValid
        ResponseGroupInformation/AvailableVersions/Version
        ResponseGroupInformation/CreationDate
        ResponseGroupInformation/Elements/Element
        ResponseGroupInformation/Name
        ResponseGroupInformation/ValidOperations/Operation'''.splitlines())
        self._check_elements(info, elements)
        
        
if __name__ == '__main__':
    unittest.main()
