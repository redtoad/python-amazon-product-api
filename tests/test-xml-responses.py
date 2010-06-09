
# import base first because sys.path is changed in order to find amazonproduct!
from base import XMLResponseTestCase, XMLResponseTestLoader
from base import XML_TEST_DIR, TESTABLE_API_VERSIONS

from amazonproduct import API, ResultPaginator, LOCALES
from amazonproduct import AWSError
from amazonproduct import InvalidParameterValue, InvalidListType
from amazonproduct import InvalidSearchIndex, InvalidResponseGroup
from amazonproduct import InvalidParameterCombination 
from amazonproduct import NoSimilarityForASIN
from amazonproduct import NoExactMatchesFound, NotEnoughParameters

from lxml import objectify
import os, os.path
import unittest

class ItemLookupTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for ItemLookup are parsed correctly.
    """
     
    locales = ['de']
    
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
    
    locales = ['de', 'fr', 'uk', 'us']
    
    def test_no_parameters(self):
        try:
            self.assertRaises(InvalidResponseGroup, 
                              self.api.item_search, 'Books')
        except AWSError, e:
            self.assert_(e.code == 'AWS.MinimumParameterRequirement')
        
    def test_invalid_response_group(self):
        self.assertRaises(InvalidResponseGroup, self.api.item_search, 
                          'All', ResponseGroup='???')
        
    def test_invalid_search_index(self):
        self.assertRaises(InvalidSearchIndex, self.api.item_search, 
                          '???', BrowseNode=132)
        
    def test_invalid_parameter_combination(self):
        self.assertRaises(InvalidParameterCombination, self.api.item_search, 
                          'All', BrowseNode=132)
        
    def test_lookup_by_title(self):
        result = self.api.item_search('Books', Title='Hunt for Red October')
        for item in result.Items.Item:
            self.assertEquals(item.ASIN, item.ASIN.pyval, item.ASIN.text) 
        
class SimilarityLookupTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for SimilarityLookup are parsed correctly.
    """
    
    locales = ['de']
    
    def test_similar_items(self):
        # 0451462009 Small Favor: A Novel of the Dresden Files 
        root = self.api.similarity_lookup('0451462009')
        
        self.assertEquals(root.Items.Request.IsValid.text, 'True')
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
    
    locales = ['de']
    
    def test_invalid_list_id(self):
        self.assertRaises(InvalidParameterValue, self.api.list_lookup, '???', 'WishList')
        
    def test_invalid_list_type(self):
        self.assertRaises(InvalidListType, self.api.list_lookup, '???', '???')
        


class ListSearchTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for ListSearch are parsed correctly.
    """
     
    locales = ['de']
    
    def test_fails_for_wrong_list_type(self):
        self.assertRaises(InvalidListType, self.api.list_search, '???')
        
    def test_fails_for_missing_search_parameters(self):
        self.assertRaises(NotEnoughParameters, self.api.list_search, 'WishList')
        self.assertRaises(NotEnoughParameters, self.api.list_search, 'WeddingRegistry')
        
    def test_no_exact_matches(self):
        self.assertRaises(NoExactMatchesFound, self.api.list_search, 
                'WishList', Email='???')


class ResultPaginatorTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for pagination are parsed correctly.
    """
    
    api_versions = ['2009-10-01', '2009-11-01']
    locales = ['de']
    
    def test_review_pagination(self):
        # reviews for "Harry Potter and the Philosopher's Stone"
        ASIN = '0747532745'
        
        # test values for different API versions
        # version : (total_reviews, review_pages)
        VALUES = {
            '2009-10-01' : (2458, 492), 
            '2009-11-01' : (2465, 493),
        }
        
        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews', 
            limit=10)
        
        for page, root in enumerate(paginator(self.api.item_lookup, 
                        ASIN, ResponseGroup='Reviews')):
            
            total_reviews = root.Items.Item.CustomerReviews.TotalReviews.pyval
            review_pages = root.Items.Item.CustomerReviews.TotalReviewPages.pyval
            try:
                current_page = root.Items.Request.ItemLookupRequest.ReviewPage.pyval
            except AttributeError:
                current_page = 1
            
            (reviews, pages) = VALUES[self.current_api_version]
            
            self.assertEquals(total_reviews, reviews)
            self.assertEquals(review_pages, pages)
            self.assertEquals(current_page, page+1)
            
        self.assertEquals(page, 9)
        self.assertEquals(current_page, 10)

    def test_pagination_works_for_missing_reviews(self):
        # "Sherlock Holmes (limitierte Steelbook Edition) [Blu-ray]"
        # had no reviews at time of writing
        ASIN = 'B0039NM7Y2'

        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')

        for page, root in enumerate(paginator(self.api.item_lookup, 
                        ASIN, ResponseGroup='Reviews')):
            self.assertFalse(hasattr(root.Items.Item, 'CustomerReviews'))

        self.assertEquals(page, 0)

    def test_pagination_works_for_xpath_expr_returning_attributes(self):
        # Bug reported by Giacomo Lacava:
        # > I've found an issue with the ResultPaginator: basically your
        # > code assumes that the xpath results are going to be nodes and calls
        # > pyval on it, but they might actually be *attributes* and in that
        # > case you'd get an error (because they don't have pyval). In my 
        # > code, working with WishLists, I don't get a Page node in the 
        # > result, so have to rely on the Argument node (which looks like 
        # > this: <Argument Name="ProductPage" Value="1">).
        LIST_ID = '229RA3LVMR97X'
        paginator = ResultPaginator('ProductPage',
            '//aws:OperationRequest/aws:Arguments/aws:Argument[@Name="ProductPage"]/@Value',
            '//aws:Lists/aws:List/aws:TotalPages',
            '//aws:Lists/aws:List/aws:TotalItems')
            
        for page, root in enumerate(paginator(self.api.list_lookup, 
                LIST_ID, 'WishList', 
                ResponseGroup='ItemAttributes,ListInfo',
                IsOmitPurchasedItems=True)):
            
            total_items = root.Lists.List.TotalItems.pyval
            total_pages = root.Lists.List.TotalPages.pyval
            try:
                current_page = root.Lists.Request.ListLookupRequest.ProductPage.pyval
            except AttributeError:
                current_page = 1
            
            self.assertEquals(total_items, 29)
            self.assertEquals(total_pages, 3)
            self.assertEquals(current_page, page+1)

class HelpTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for Help are parsed correctly.
    """
    
    locales = ['de']
    
    def test_fails_for_wrong_input(self):
        # Wrong help_type and about raise ValueErrors.
        self.assertRaises(ValueError, self.api.help, 'Help', 'Unknown')
        self.assertRaises(ValueError, self.api.help, 'Unknown', 'Operation')
        self.assertRaises(ValueError, self.api.help, 'Unknown', 'Unknown')
    
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
        # Check API call ``Help`` for ``Operation`` ``Help``.
        root = self.api.help('Help', 'Operation')
        self.assertEquals(root.Information.Request.IsValid.text, 'True')
        
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
        # Check API call ``Help`` for ``ResponseGroup`` ``Help``.
        root = self.api.help('Help', 'ResponseGroup')
        self.assertEquals(root.Information.Request.IsValid.text, 'True')
        
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
        
        
class BrowseNodeLookupTestCase (XMLResponseTestCase):
    
    """
    Check that all XML responses for ListLookup are parsed correctly.
    """
    
    #:  BrowseNodeId for 'Books'
    BOOKS_ROOT_NODE = {
        'ca' : 927726, 
        'de' : 541686, 
        'fr' : 468256, 
        'jp' : 465610, 
        'uk' : 1025612, 
        'us' : 1000, 
    }
    
    CHILDREN = {
        'ca' : [933484, 13901671, 934986, 935522, 4142731, 935948, 13932641, 
                939082, 940804, 387057011, 941378, 942318, 942402, 927728, 
                943356, 943958, 927730, 927790, 948300, 948808, 927734, 950152, 
                950640, 950756, 952366, 953420, 955190, 956280, 957368, 959466, 
                959978, 960696, 680096011], 
        'de' : [4185461, 117, 187254, 403434, 120, 287621, 124, 11063821,
                340583031, 288100, 548400, 122, 13690631, 118310011, 280652,
                189528, 287480, 403432, 1199902, 121, 143, 536302, 298002,
                340513031, 142, 298338, 188795], 
        'fr' : [13921201, 463892, 360051011, 257111011, 306966011, 14122841, 401466011, 401465011, 310883011, 735796, 310884011, 301145, 3498561, 381592011, 3023891, 236451011, 401467011, 13464941, 365476011, 310253011, 310880011, 362944011], 
        'jp' : [466284, 466288, 571582, 571584, 492152, 466286, 466282, 492054, 
                466290, 492166, 466298, 466294, 466292, 492228, 466304, 492090, 
                466302, 3148931, 466306, 466280, 500592, 492266, 466296, 
                466300, 13384021, 746102, 255460011, 886928, 13383771, 
                10667101],
        'uk' : [349777011, 91, 267859, 51, 67, 68, 507848, 69, 274081, 71, 72, 
                62, 66, 275835, 74, 65, 64, 63, 89, 275738, 61, 73, 275389, 59, 
                58, 88, 57, 56, 564334, 60, 55, 13384091, 83, 52, 637262],
        'us' : [1, 2, 3, 4, 4366, 5, 6, 86, 301889, 10, 9, 48, 10777, 17, 
                13996, 18, 53, 290060, 20, 173507, 21, 22, 23, 75, 25, 26, 28, 
                27],
    }
    
    ANCESTORS = {
        'ca' : [916520], 
        'de' : [186606], 
        'fr' : [301061], 
        'jp' : [465392],
        'uk' : [266239],
        'us' : [283155],
    }
    
    def test_fails_for_wrong_input(self):
        self.assertRaises(InvalidParameterValue, self.api.browse_node_lookup, '???')
        self.assertRaises(InvalidResponseGroup, self.api.browse_node_lookup, 
                self.BOOKS_ROOT_NODE[self.current_locale], '???')
        
    def test_books_browsenode(self):
        nodes = self.api.browse_node_lookup(self.BOOKS_ROOT_NODE[self.current_locale]).BrowseNodes
        self.assertEquals(nodes.Request.IsValid.text, 'True')
        self.assertEquals(nodes.BrowseNode.BrowseNodeId, self.BOOKS_ROOT_NODE[self.current_locale])
        #self.assertEquals(nodes.BrowseNode.IsCategoryRoot, 1)
        
        children = [n.BrowseNodeId for n in nodes.BrowseNode.Children.BrowseNode]
        ancestors = [n.BrowseNodeId for n in nodes.BrowseNode.Ancestors.BrowseNode]
        self.assertEquals(children, self.CHILDREN[self.current_locale])
        self.assertEquals(ancestors, self.ANCESTORS[self.current_locale])
        

class XMLParsingTestCase (unittest.TestCase):
    
    """
    Checks that all XML responses are parsed correctly, for instance, that all
    <ItemId> elements are ``objectify.StringElement``s. 
    """
    
    ACCESS_KEY = SECRET_KEY = ''
    
    def setUp(self):
        """
        Collect all XML files stored.
        """
        # TODO: Skip tests if no XML files are found?
        self.test_files = [os.path.join(XML_TEST_DIR, dir, f) 
            for dir in TESTABLE_API_VERSIONS
            for f in os.listdir(os.path.join(XML_TEST_DIR, dir))
            if f.lower().endswith('.xml')
        ]
        self.api = API(self.ACCESS_KEY, self.SECRET_KEY, 'us')
        
        # run API parser with fake XML snippet
        # so we can use self.api._parser directly in tests
        from StringIO import StringIO
        self.api._parse(StringIO('<xml xmlns="http://webservices.amazon.com/AWSECommerceService/2009-11-01"/>'))
        
    def test_all_ItemId_elements_are_StringElement(self):
        for file in self.test_files:
            tree = objectify.parse(open(file), self.api._parser)
            nspace = tree.getroot().nsmap.get(None, '')
            for item_id in tree.xpath('//aws:ItemId', 
                                      namespaces={'aws' : nspace}):
                self.assertEquals(item_id.pyval, item_id.text, str(item_id)) 
                
    def test_all_ASIN_elements_are_StringElement(self):
        for file in self.test_files:
            tree = objectify.parse(open(file), self.api._parser)
            nspace = tree.getroot().nsmap.get(None, '')
            for item_id in tree.xpath('//aws:ItemId', 
                                      namespaces={'aws' : nspace}):
                self.assertEquals(item_id.pyval, item_id.text, str(item_id)) 

if __name__ == '__main__':
    import unittest
    unittest.main(testLoader=XMLResponseTestLoader())
