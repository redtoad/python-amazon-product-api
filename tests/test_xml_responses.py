
import os
import pytest

from tests.utils import CustomAPI, convert_camel_case
from tests import XML_TEST_DIR, TESTABLE_API_VERSIONS, TESTABLE_LOCALES
from tests import AWS_KEY, SECRET_KEY

from amazonproduct.api import API, ResultPaginator
from amazonproduct import AWSError
from amazonproduct import InvalidParameterValue, InvalidListType
from amazonproduct import InvalidSearchIndex, InvalidResponseGroup
from amazonproduct import InvalidParameterCombination 
from amazonproduct import NoSimilarityForASIN
from amazonproduct import NoExactMatchesFound, NotEnoughParameters
from amazonproduct import DeprecatedOperation

def pytest_generate_tests(metafunc):
    # called once per each test function
    if 'api' in metafunc.funcargnames:
        api_versions = getattr(metafunc.function, 'api_versions',
            getattr(metafunc.cls, 'api_versions', TESTABLE_API_VERSIONS))
        for version in api_versions:
            locales = getattr(metafunc.function, 'locales',
                getattr(metafunc.cls, 'locales', TESTABLE_LOCALES))
            for locale in locales:
                api = CustomAPI(AWS_KEY, SECRET_KEY, locale)
                api.VERSION = version
                api.local_file = os.path.join(XML_TEST_DIR, version,
                    '%s-%s-%s.xml' % (metafunc.cls.__name__[4:], locale, 
                    metafunc.function.__name__[5:].replace('_', '-')))
                metafunc.addcall(
                    id='%s/%s' % (version, locale), 
                    funcargs={'api' : api})

#def setup_module(module):
#    import _pytest
#    module._monkeypatch = _pytest.monkeypatch.monkeypatch()
#
#def teardown_module(module):
#    module._monkeypatch.undo()

class TestCorrectVersion (object):

    """
    Check that each requested API version is also really used.
    """

    def test_correct_version(self, api):
        # any operation will do here
        root = api.item_lookup('0747532745')
        nspace = root.nsmap.get(None, '')
        assert api.VERSION in nspace


class TestItemLookup (object):

    """
    Check that all XML responses for ItemLookup are parsed correctly.
    """
     
    def test_invalid_item_id(self, api):
        pytest.raises(InvalidParameterValue, api.item_lookup, '1234567890123')
        
    def test_valid_asin(self, api):
        # Harry Potter and the Philosopher's Stone
        api.item_lookup('0747532745')
        
    def test_valid_isbn(self, api):
        # Harry Potter and the Philosopher's Stone
        api.item_lookup('9780747532743', IdType='ISBN', SearchIndex='All')
        
    def test_invalid_search_index(self, api):
        pytest.raises(InvalidSearchIndex, api.item_lookup, '9780747532743', 
            IdType='ISBN', SearchIndex='???')
        
    def test_invalid_response_group(self, api):
        pytest.raises(InvalidResponseGroup, api.item_lookup, '9780747532743', 
            IdType='ISBN', SearchIndex='All', ResponseGroup='???')
        
    def test_valid_isbn_no_searchindex(self, api):
        # Harry Potter and the Philosopher's Stone
        try:
            api.item_lookup('9780747532743', IdType='ISBN')
        except AWSError, e:
            assert e.code == 'AWS.MissingParameterValueCombination'
        
        
class TestItemSearch (object):

    """
    Check that all XML responses for ItemSearch are parsed correctly.
    """
    
    def test_no_parameters(self, api):
        try:
            pytest.raises(InvalidResponseGroup, 
                              api.item_search, 'Books')
        except AWSError, e:
            assert e.code == 'AWS.MinimumParameterRequirement'
        
    def test_unicode_parameter(self, api):
        # Issue 17: UnicodeDecodeError when python's default encoding is not
        # utf-8
        try:
            api.item_search('Books', Author=u'F\xe9lix J. Palma')
        except NoExactMatchesFound:
            # doesn't matter if this author is not found in all locales
            # as long as no UnicodeDecodeError is raised!
            pass

    def test_invalid_response_group(self, api):
        pytest.raises(InvalidResponseGroup, api.item_search, 
                          'All', ResponseGroup='???')
        
    def test_invalid_search_index(self, api):
        pytest.raises(InvalidSearchIndex, api.item_search, 
                          '???', BrowseNode=132)
        
    def test_invalid_parameter_combination(self, api):
        pytest.raises(InvalidParameterCombination, api.item_search, 
                          'All', BrowseNode=132)
        
    #@ignore_locales('jp')
    def test_lookup_by_title(self, api):
        result = api.item_search('Books', Title='Harry Potter')
        for item in result.Items.Item:
            assert item.ASIN == item.ASIN.pyval == item.ASIN.text
        

class TestSimilarityLookup (object):
    
    """
    Check that all XML responses for SimilarityLookup are parsed correctly.
    """
    
    locales = ['de']
    
    def test_similar_items(self, api):
        # 0451462009 Small Favor: A Novel of the Dresden Files 
        root = api.similarity_lookup('0451462009')
        
        assert root.Items.Request.IsValid.text == 'True'
        assert len(root.Items.Item) > 0
        
    def test_no_similar_items_for_two_asins(self, api):
        # 0451462009 Small Favor: A Novel of the Dresden Files
        # B0024NL0TG Oral-B toothbrush
        pytest.raises(NoSimilarityForASIN, api.similarity_lookup,
                          '0451462009', 'B0024NL0TG')


class TestResultPaginator (object):

    """
    Check that all XML responses for pagination are parsed correctly.
    """

    api_versions = ['2009-10-01', '2009-11-01']
    locales = ['de']

    def test_itemsearch_pagination(self, api):

        results = 272
        pages = 28

        paginator = ResultPaginator('ItemPage',
            '//aws:Items/aws:Request/aws:ItemSearchRequest/aws:ItemPage',
            '//aws:Items/aws:TotalPages',
            '//aws:Items/aws:TotalResults',
            limit=10)

        for page, root in enumerate(paginator(api.item_search, 'Books', 
                        Publisher='Galileo Press', Sort='salesrank')):
            assert paginator.total_results == results
            assert paginator.total_pages == pages
            assert paginator.current_page == page+1

        assert page == 9
        assert paginator.current_page == 10

    def test_review_pagination(self, api):
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

        for page, root in enumerate(paginator(api.item_lookup,
                        ASIN, ResponseGroup='Reviews')):
            reviews, pages = VALUES[api.VERSION]
            assert paginator.total_results == reviews
            assert paginator.total_pages == pages
            assert paginator.current_page == page+1

        assert page == 9
        assert paginator.current_page == 10

    def test_pagination_works_for_missing_reviews(self, api):
        # "Sherlock Holmes (limitierte Steelbook Edition) [Blu-ray]"
        # had no reviews at time of writing
        ASIN = 'B0039NM7Y2'

        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')

        for page, root in enumerate(paginator(api.item_lookup,
                        ASIN, ResponseGroup='Reviews')):
            assert not hasattr(root.Items.Item, 'CustomerReviews')

        assert page == 0

# FIXME: ListLookup has since been deprecated! Until I find suitable example to
# use instead, I'm disabling this test.
#    def test_pagination_works_for_xpath_expr_returning_attributes(self):
#        # Bug reported by Giacomo Lacava:
#        # > I've found an issue with the ResultPaginator: basically your
#        # > code assumes that the xpath results are going to be nodes and calls
#        # > pyval on it, but they might actually be *attributes* and in that
#        # > case you'd get an error (because they don't have pyval). In my 
#        # > code, working with WishLists, I don't get a Page node in the 
#        # > result, so have to rely on the Argument node (which looks like 
#        # > this: <Argument Name="ProductPage" Value="1">).
#        LIST_ID = '229RA3LVMR97X'
#        paginator = ResultPaginator('ProductPage',
#            '//aws:OperationRequest/aws:Arguments/aws:Argument[@Name="ProductPage"]/@Value',
#            '//aws:Lists/aws:List/aws:TotalPages',
#            '//aws:Lists/aws:List/aws:TotalItems')
#
#        for page, root in enumerate(paginator(self.api.list_lookup,
#                LIST_ID, 'WishList',
#                ResponseGroup='ItemAttributes,ListInfo',
#                IsOmitPurchasedItems=True)):
#
#            self.assertEquals(paginator.total_results, 29)
#            self.assertEquals(paginator.total_pages, 3)
#            self.assertEquals(paginator.current_page, page+1)


class TestBrowseNodeLookup (object):
    
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
                340583031, 288100, 142, 548400, 122, 13690631, 419943031, 
                118310011, 280652, 189528, 287480, 403432, 1199902, 121, 143, 
                536302, 298002, 188795, 340513031, 298338], 
        'fr' : [13921201, 463892, 360051011, 257111011, 306966011, 14122841, 
                401466011, 401465011, 310883011, 735796, 310884011, 301145, 
                3498561, 381592011, 3023891, 236451011, 401467011, 13464941, 
                365476011, 310253011, 310880011, 362944011], 
        'jp' : [466284, 571582, 571584, 492152, 466286, 466282, 492054, 466290, 
                492166, 466298, 466294, 466292, 492228, 466304, 492090, 466302, 
                3148931, 466306, 466280, 500592, 492266, 466296, 466300, 
                13384021, 746102, 255460011, 886928, 13383771, 10667101],
        'uk' : [349777011, 91, 51, 267859, 67, 68, 507848, 69, 274081, 71, 72, 
                637262, 279254, 62, 66, 275835, 74, 65, 64, 63, 89, 275738, 61, 
                73, 275389, 59, 58, 88, 57, 279292, 564334, 60, 55, 13384091, 
                83],
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
    
    def test_fails_for_wrong_input(self, api):
        pytest.raises(InvalidParameterValue, api.browse_node_lookup, '???')
        pytest.raises(InvalidResponseGroup, api.browse_node_lookup, 
                self.BOOKS_ROOT_NODE[api.locale], '???')
        
    def test_books_browsenode(self, api):
        nodes = api.browse_node_lookup(self.BOOKS_ROOT_NODE[api.locale]).BrowseNodes
        assert nodes.Request.IsValid.text == 'True'
        assert nodes.BrowseNode.BrowseNodeId == self.BOOKS_ROOT_NODE[api.locale]
        #self.assertEquals(nodes.BrowseNode.IsCategoryRoot, 1)
        
        children = [n.BrowseNodeId for n in nodes.BrowseNode.Children.BrowseNode]
        ancestors = [n.BrowseNodeId for n in nodes.BrowseNode.Ancestors.BrowseNode]
        assert children == self.CHILDREN[api.locale]
        assert ancestors == self.ANCESTORS[api.locale]
        

class TestDeprecatedOperations (object):

    """
    Due to low usage, the Product Advertising API operations listed below will
    not be supported after October 15, 2010:

    * CustomerContentLookup
    * CustomerContentSearch
    * Help
    * ListLookup
    * ListSearch
    * TagLookup
    * TransactionLookup
    * VehiclePartLookup
    * VehiclePartSearch
    * VehicleSearch
    """

    DEPRECATED_OPRATIONS = [
        'CustomerContentLookup',
        'CustomerContentSearch',
        'Help',
        'ListLookup',
        'ListSearch',
        'TagLookup',
        'TransactionLookup',
        'VehiclePartLookup',
        'VehiclePartSearch',
        'VehicleSearch', 
    ]

    def test_calling_deprecated_operations(self, api):
        for operation in self.DEPRECATED_OPRATIONS:
            method = getattr(api, convert_camel_case(operation))
            pytest.raises(DeprecatedOperation, method)

    def test_calling_deprecated_operations_using_call_fails(self, api):
        for operation in self.DEPRECATED_OPRATIONS:
            pytest.raises(DeprecatedOperation, api.call, Operation=operation)


class TestXMLParsing (object):
    
    """
    Checks that all XML responses are parsed correctly, for instance, that all
    <ItemId> elements are ``objectify.StringElement``s. 
    """
    
    ACCESS_KEY = SECRET_KEY = ''
    
    def setup_class(cls):
        """
        Collect all XML files stored.
        """
        # TODO: Skip tests if no XML files are found?
        cls.test_files = [os.path.join(XML_TEST_DIR, dir, f)
            for dir in TESTABLE_API_VERSIONS
            for f in os.listdir(os.path.join(XML_TEST_DIR, dir))
            if f.lower().endswith('.xml')
        ]
        cls.api = API(cls.ACCESS_KEY, cls.SECRET_KEY, 'us')

    def test_all_ItemId_elements_are_StringElement(self):
        for file in self.test_files:
            try:
                tree = self.api.response_processor(open(file))
                nspace = tree.nsmap.get(None, '')
                for item_id in tree.xpath('//aws:ItemId',
                                          namespaces={'aws' : nspace}):
                    assert item_id.pyval == item_id.text == str(item_id)
            except AWSError:
                pass

    def test_all_ASIN_elements_are_StringElement(self):
        for file in self.test_files:
            try:
                tree = self.api.response_processor(open(file))
                nspace = tree.nsmap.get(None, '')
                for item_id in tree.xpath('//aws:ItemId',
                                          namespaces={'aws' : nspace}):
                    assert item_id.pyval == item_id.text == str(item_id)
            except AWSError:
                pass


