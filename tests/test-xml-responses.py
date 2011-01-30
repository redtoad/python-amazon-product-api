
# import base first because sys.path is changed in order to find amazonproduct!
from base import XMLResponseTestCase, XMLResponseTestLoader
from base import XML_TEST_DIR, TESTABLE_API_VERSIONS

from amazonproduct.api import API
from amazonproduct.errors import *
from amazonproduct.paginators import LxmlPaginator

from lxml import objectify
import os, os.path
import unittest

from utils import convert_camel_case, Cart

class CorrectVersionTestCase (XMLResponseTestCase):

    """
    Check that each requested API version is also really used.
    """

    def test_correct_version(self):
        # any operation will do here
        root = self.api.item_lookup('0747532745')
        nspace = root.nsmap.get(None, '')
        self.assert_(self.current_api_version in nspace)


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
            results = self.api.item_search('Books')
            self.assertRaises(InvalidResponseGroup, results.next)
        except AWSError, e:
            self.assert_(e.code == 'AWS.MinimumParameterRequirement')

    def test_unicode_parameter(self):
        # Issue 17: UnicodeDecodeError when python's default encoding is not
        # utf-8
        try:
            results = self.api.item_search('Books', Author=u'F\xe9lix J. Palma')
            results.next()
        except NoExactMatchesFound:
            # doesn't matter if this author is not found in all locales
            # as long as no UnicodeDecodeError is raised!
            pass

    def test_invalid_response_group(self):
        results = self.api.item_search('All', ResponseGroup='???')
        self.assertRaises(InvalidResponseGroup, results.next)

    def test_invalid_search_index(self):
        results = self.api.item_search('???', BrowseNode=132)
        self.assertRaises(InvalidSearchIndex, results.next)

    def test_invalid_parameter_combination(self):
        results = self.api.item_search('All', BrowseNode=132)
        self.assertRaises(InvalidParameterCombination, results.next) 

    def test_lookup_by_title(self):
        print self.current_api_version, self.current_locale
        for page in self.api.item_search('Books', Title='Harry Potter', limit=1):
            for item in page.Items.Item:
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


class ResultPaginatorTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for pagination are parsed correctly.
    """

    api_versions = ['2009-10-01', '2009-11-01']
    locales = ['de']

    def test_itemsearch_pagination(self):

        results = 272
        pages = 28

        paginator = self.api.item_search('Books', 
                Publisher='Galileo Press', Sort='salesrank', limit=10)
        for page, root in enumerate(paginator):
            self.assertEquals(results, root.Items.TotalResults.pyval)
            self.assertEquals(pages, root.Items.TotalPages.pyval)
            self.assertEquals(page+1, root.Items.Request.ItemSearchRequest.ItemPage.pyval)
        self.assertEquals(page, 9)

    def test_review_pagination(self):
        # reviews for "Harry Potter and the Philosopher's Stone"
        ASIN = '0747532745'

        # test values for different API versions
        # version : (total_reviews, review_pages)
        VALUES = {
            '2009-10-01' : (2458, 492),
            '2009-11-01' : (2465, 493),
        }

        paginator = LxmlPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews',
            limit=10)

        for page, root in enumerate(paginator(self.api.item_lookup,
                        ASIN, ResponseGroup='Reviews')):
            reviews, pages = VALUES[self.current_api_version]
        self.assertEquals(page, 9)

    def test_pagination_works_for_missing_reviews(self):
        # "Sherlock Holmes (limitierte Steelbook Edition) [Blu-ray]"
        # had no reviews at time of writing
        ASIN = 'B0039NM7Y2'

        paginator = LxmlPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')

        for page, root in enumerate(paginator(self.api.item_lookup,
                        ASIN, ResponseGroup='Reviews')):
            self.assertFalse(hasattr(root.Items.Item, 'CustomerReviews'))

        self.assertEquals(page, 0)

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
        


class CartCreateTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for CartCreate are parsed correctly.
    """

    def test_creating_basket_with_empty_items_fails(self):
        self.assertRaises(ValueError, self.api.cart_create, {})
        self.assertRaises(ValueError, self.api.cart_create, {'0451462009' : 0})

    def test_creating_basket_with_negative_item_quantity_fails(self):
        self.assertRaises(ValueError, self.api.cart_create, {'0201896834' : -1})

    def test_creating_basket_with_quantity_too_high_fails(self):
        self.assertRaises(ValueError, self.api.cart_create, {'0201896834' : 1000})

    def test_creating_basket_with_unknown_item_fails(self):
        self.assertRaises(InvalidCartItem, self.api.cart_create, {'021554' : 1})

    def test_create_cart(self):
        root = self.api.cart_create({
            '0201896834' : 1, # The Art of Computer Programming Vol. 1
            '0201896842' : 1, # The Art of Computer Programming Vol. 2
       })
        cart = Cart.from_xml(root.Cart)
        assert len(cart.items) == 2
        assert cart['0201896834'].quantity == 1
        assert cart['0201896842'].quantity == 1

class CartAddTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for CartAdd are parsed correctly.
    """

    def setUp(self):
        XMLResponseTestCase.setUp(self)
        items = {
            '0201896834' : 1, # The Art of Computer Programming Vol. 1
            '0201896842' : 1, # The Art of Computer Programming Vol. 2
        }
        cart = self.api.cart_create(items).Cart
        self.cart_id = cart.CartId
        self.hmac = cart.HMAC

    def test_adding_with_wrong_cartid_hmac_fails(self):
        self.assertRaises(CartInfoMismatch, self.api.cart_add, '???', self.hmac, {'0201896834' : 1})
        self.assertRaises(CartInfoMismatch, self.api.cart_add, self.cart_id, '???', {'0201896834' : 1})

    def test_adding_empty_items_fails(self):
        self.assertRaises(ValueError, self.api.cart_add, self.cart_id, self.hmac, {})
        self.assertRaises(ValueError, self.api.cart_add, self.cart_id, self.hmac, {'0451462009' : 0})

    def test_adding_negative_item_quantity_fails(self):
        self.assertRaises(ValueError, self.api.cart_add, self.cart_id, self.hmac, {'0201896834' : -1})

    def test_adding_item_quantity_too_high_fails(self):
        self.assertRaises(ValueError, self.api.cart_add, self.cart_id, self.hmac, {'0201896834' : 1000})

    def test_adding_unknown_item_fails(self):
        self.assertRaises(InvalidCartItem, self.api.cart_add, self.cart_id, self.hmac, {'021554' : 1})

    def test_adding_item_already_in_cart_fails(self):
        self.assertRaises(ItemAlreadyInCart, self.api.cart_add, self.cart_id, 
                          self.hmac, {'0201896842' : 2})

    def test_adding_item(self):
        root = self.api.cart_add(self.cart_id, self.hmac, {
            '0201896850' : 1, # The Art of Computer Programming Vol. 3
        })
        cart = Cart.from_xml(root.Cart)
        item = cart['0201896850']
        self.assertEquals(item.quantity, 1)
        self.assertEquals(item.asin, '0201896850')


class CartModifyTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for CartModify are parsed correctly.
    """

    def setUp(self):
        XMLResponseTestCase.setUp(self)
        items = {
            '0201896834' : 1, # The Art of Computer Programming Vol. 1
        }
        cart = self.api.cart_create(items).Cart
        self.cart_id = cart.CartId
        self.hmac = cart.HMAC

    def tearDown(self):
        self.api.cart_clear(self.cart_id, self.hmac)

    def test_modifying_with_wrong_cartid_hmac_fails(self):
        self.assertRaises(CartInfoMismatch, self.api.cart_modify, '???', self.hmac, {'0201896834' : 1})
        self.assertRaises(CartInfoMismatch, self.api.cart_modify, self.cart_id, '???', {'0201896834' : 1})

    def test_modifying_empty_items_fails(self):
        self.assertRaises(ValueError, self.api.cart_modify, self.cart_id, self.hmac, {})

    def test_modifying_negative_item_quantity_fails(self):
        self.assertRaises(ValueError, self.api.cart_modify, self.cart_id, self.hmac, {'0201896834' : -1})

    def test_modifying_item_quantity_too_high_fails(self):
        self.assertRaises(ValueError, self.api.cart_modify, self.cart_id, self.hmac, {'0201896834' : 1000})

    def test_modfying_item(self):
        root = self.api.cart_modify(self.cart_id, self.hmac, {
            '0201896834' : 0, # The Art of Computer Programming Vol. 1
            '0201896842' : 1, # The Art of Computer Programming Vol. 2
        })
        cart = Cart.from_xml(root.Cart)
        from lxml import etree
        print etree.tostring(root.Cart, pretty_print=True)
        self.assertEquals(len(cart.items), 1)
        item = cart['0201896842']
        self.assertEquals(item.quantity, 1)
        self.assertEquals(item.asin, '0201896842')


class CartGetTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for CartGet are parsed correctly.
    """

    def setUp(self):
        XMLResponseTestCase.setUp(self)
        items = {
            '0201896834' : 1, # The Art of Computer Programming Vol. 1
        }
        cart = self.api.cart_create(items).Cart
        self.cart_id = cart.CartId
        self.hmac = cart.HMAC

    def tearDown(self):
        try:
            self.api.cart_clear(self.cart_id, self.hmac)
        except:
            pass

    def test_getting_with_wrong_cartid_hmac_fails(self):
        self.assertRaises(CartInfoMismatch, self.api.cart_get, '???', self.hmac)
        self.assertRaises(CartInfoMismatch, self.api.cart_get, self.cart_id, '???')

    def test_getting_cart(self):
        root = self.api.cart_get(self.cart_id, self.hmac)
        cart = Cart.from_xml(root.Cart)
        self.assertEquals(len(cart.items), 1)


class CartClearTestCase (XMLResponseTestCase):

    """
    Check that all XML responses for CartClear are parsed correctly.
    """

    def setUp(self):
        XMLResponseTestCase.setUp(self)
        items = {
            '0201896834' : 1, # The Art of Computer Programming Vol. 1
        }
        cart = self.api.cart_create(items).Cart
        self.cart_id = cart.CartId
        self.hmac = cart.HMAC

    def tearDown(self):
        try:
            self.api.cart_clear(self.cart_id, self.hmac)
        except:
            pass

    def test_clearing_with_wrong_cartid_hmac_fails(self):
        self.assertRaises(CartInfoMismatch, self.api.cart_clear, '???', self.hmac)
        self.assertRaises(CartInfoMismatch, self.api.cart_clear, self.cart_id, '???')

    def test_clearing_cart(self):
        root = self.api.cart_clear(self.cart_id, self.hmac)
        cart = Cart.from_xml(root.Cart)
        self.assertEquals(len(cart.items), 0)


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

    def test_all_ItemId_elements_are_StringElement(self):
        for file in self.test_files:
            try:
                tree = self.api.response_processor(open(file))
                nspace = tree.nsmap.get(None, '')
                for item_id in tree.xpath('//aws:ItemId',
                                          namespaces={'aws' : nspace}):
                    self.assertEquals(item_id.pyval, item_id.text, str(item_id)) 
            except AWSError:
                pass

    def test_all_ASIN_elements_are_StringElement(self):
        for file in self.test_files:
            try:
                tree = self.api.response_processor(open(file))
                nspace = tree.nsmap.get(None, '')
                for item_id in tree.xpath('//aws:ItemId',
                                          namespaces={'aws' : nspace}):
                    self.assertEquals(item_id.pyval, item_id.text, str(item_id)) 
            except AWSError:
                pass


class DeprecatedOperationsTestCase (XMLResponseTestCase):

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

    DEPRECATED_OPERATIONS = [
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

    def test_calling_deprecated_operations(self):
        for operation in self.DEPRECATED_OPERATIONS:
            self.assertRaises(DeprecatedOperation, 
                              getattr(self.api, convert_camel_case(operation)))

    def test_calling_deprecated_operations_using_call_fails(self):
        for operation in self.DEPRECATED_OPERATIONS:
            self.assertRaises(DeprecatedOperation, self.api.call, 
                              Operation=operation)