
import os
import pytest
import re
import urllib2

from tests.utils import convert_camel_case, Cart
from tests import XML_TEST_DIR
from tests import TESTABLE_API_VERSIONS, TESTABLE_LOCALES, TESTABLE_PROCESSORS
from tests import AWS_KEY, SECRET_KEY

from amazonproduct.api import API
from amazonproduct.errors import *

def pytest_generate_tests(metafunc):
    """
    All test methods is called once for each API version and locale. Test
    classes and methods can (optionally) use attributes ``locales`` and
    ``api_versions`` to specify which one are used.
    """
    if 'api' in metafunc.funcargnames:
        processors = getattr(metafunc.function, 'processors',
            getattr(metafunc.cls, 'processors', TESTABLE_PROCESSORS))
        for processor in processors:
            api_versions = getattr(metafunc.function, 'api_versions',
                getattr(metafunc.cls, 'api_versions', TESTABLE_API_VERSIONS))
            for version in api_versions:
                locales = getattr(metafunc.function, 'locales',
                    getattr(metafunc.cls, 'locales', TESTABLE_LOCALES))
                for locale in locales:
                    # file containing previously fetched response
                    local_file = os.path.join(XML_TEST_DIR, version,
                        '%s-%s-%s.xml' % (metafunc.cls.__name__[4:], locale,
                        metafunc.function.__name__[5:].replace('_', '-')))
                    metafunc.addcall(
                        id='%s:%s/%s' % (processor, version, locale),
                        param={
                            'processor': processor,
                            'version': version,
                            'locale': locale,
                            'xml_response': local_file
                        })

def pytest_funcarg__server(request):
    """
    Is the same as funcarg `httpserver` from plugin pytest-localserver with the
    difference that it has a module-wide scope.
    """
    def setup():
        try:
            localserver = request.config.pluginmanager.getplugin('localserver')
        except KeyError:
            raise pytest.skip('This test needs plugin pytest-localserver!')
        server = localserver.http.Server()
        server.start()
        return server
    def teardown(server):
        server.stop()
    return request.cached_setup(setup, teardown, 'module')

def pytest_funcarg__api(request):
    """
    Initialises API for each test call (formerly done with ``setup_method()``).
    """
    server = request.getfuncargvalue('server')
    url_reg = re.compile(r'^http://(?P<host>[\w\-\.]+)(?P<path>/onca/xml.*)$')

    processor = TESTABLE_PROCESSORS[request.param['processor']]()
    api = API(AWS_KEY, SECRET_KEY, request.param['locale'], processor=processor, associate_tag='redtoad-20')
    api.VERSION = request.param['version']
    api.REQUESTS_PER_SECOND = 10000 # just for here!

    def counter(fnc):
        """
        Wrapper function for ``_fetch`` which

        1. keeps track of the times has been called and adjusts the path to the 
           corresponding XML response
        2. Fetches any response that has not been cached from the live servers
        """
        api._count = 0
        def wrapped(url):
            api._count += 1
            path = request.param['xml_response']
            if api._count > 1:
                root, ext = os.path.splitext(path)
                path = '%s-%i%s' % (root, api._count, ext)
            try:
                content = open(path, 'r').read()
            except IOError:
                if not all([AWS_KEY, SECRET_KEY]): 
                    raise pytest.skip('No cached XML response found!')
                content = urllib2.urlopen(url).read()
                if not os.path.exists(os.path.dirname(path)):
                    os.mkdir(os.path.dirname(path))
                open(path, 'wb').write(content)
            # We simply exchange the real host with the local one now!
            # Note: Although strictly speaking it does not matter which URL is
            # called exactly, to appeal to one's sense of correctness, let's
            # keep at least correct path!
            url = url_reg.sub(r'%s\g<path>' % server.url, url)
            server.serve_content(content)
            return fnc(url)
        return wrapped

    api._fetch = counter(api._fetch)
    return api


class runfor (object):

    """
    Can limit any test method/function decorated with this to run only for/with
    the specified API version, locale and/or result processor.
    """

    def __init__(self, api_versions=None, locales=None, processors=None):
        self.api_versions = api_versions
        self.locales = locales
        self.processors = processors

    def __call__(self, fnc):
        if self.api_versions is not None:
            fnc.api_versions = self.api_versions
        if self.locales is not None:
            fnc.locales = self.locales
        if self.processors is not None:
            fnc.processors = self.processors
        return fnc



class TestCorrectVersion (object):

    """
    Check that each requested API version is also really used.
    """

    def test_correct_version(self, api):
        # any operation will do here
        root = api.item_lookup('0747532745')
        if not hasattr(root, 'nsmap'):
            raise pytest.skip('This test only works with lxml processors!')
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

    @runfor(processors=['objectify'])
    def test_lookup_by_title(self, api):
        for result in api.item_search('Books', Title='Harry Potter', limit=1):
            for item in result.Items.Item:
                assert item.ASIN == item.ASIN.pyval == item.ASIN.text
        

class TestSimilarityLookup (object):
    
    """
    Check that all XML responses for SimilarityLookup are parsed correctly.
    """
    
    locales = ['de']

    @runfor(processors=['objectify'])
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

        paginator = api.item_search('Books',
                Publisher='Galileo Press', Sort='salesrank', limit=10)
        for page, root in enumerate(paginator):
            assert paginator.results == results
            assert paginator.pages == pages
            assert paginator.current == page+1

        assert page == 9
        assert paginator.current == 10

    def test_itemsearch_over_all_is_limited_to_five(self, api):
        paginator = api.item_search('All', Keywords='Michael Jackson')
        pages = list(paginator)
        assert len(pages) == 5
        assert paginator.current == 5

    def test_itemsearch_over_all_is_limited_to_five_even_for_higher_limits(self, api):
        paginator = api.item_search('All', Keywords='Michael Jackson', limit=20)
        pages = list(paginator)
        assert len(pages) == 5
        assert paginator.current == 5

    def test_itemsearch_over_all_can_be_further_limited(self, api):
        paginator = api.item_search('All', Keywords='Michael Jackson', limit=2)
        pages = list(paginator)
        assert len(pages) == 2
        assert paginator.current == 2

#    def test_review_pagination(self, api):
#        # reviews for "Harry Potter and the Philosopher's Stone"
#        ASIN = '0747532745'
#
#        # test values for different API versions
#        # version : (total_reviews, review_pages)
#        VALUES = {
#            '2009-10-01' : (2458, 492),
#            '2009-11-01' : (2465, 493),
#        }
#
#        paginator = api.item_lookup(ASIN, ResponseGroup='Reviews', paginate='ReviewPage', limit=10)
#
#        for page, root in enumerate(paginator):
#            reviews, pages = VALUES[api.VERSION]
#            assert paginator.results == reviews
#            assert paginator.pages == pages
#            assert paginator.current == page+1
#
#        assert page == 9
#        assert paginator.current == 10
#
#    def test_pagination_works_for_missing_reviews(self, api):
#        # "Sherlock Holmes (limitierte Steelbook Edition) [Blu-ray]"
#        # had no reviews at time of writing
#        ASIN = 'B0039NM7Y2'
#
#        paginator = self.ReviewPaginator(api.item_lookup,
#            ASIN, ResponseGroup='Reviews')
#
#        for page, root in enumerate(paginator):
#            assert not hasattr(root.Items.Item, 'CustomerReviews')
#
#        assert page == 0


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

    @runfor(processors=['objectify'])
    def test_books_browsenode(self, api):
        nodes = api.browse_node_lookup(self.BOOKS_ROOT_NODE[api.locale]).BrowseNodes
        assert nodes.Request.IsValid.text == 'True'
        assert nodes.BrowseNode.BrowseNodeId == self.BOOKS_ROOT_NODE[api.locale]
        #self.assertEquals(nodes.BrowseNode.IsCategoryRoot, 1)
        
        children = [n.BrowseNodeId for n in nodes.BrowseNode.Children.BrowseNode]
        ancestors = [n.BrowseNodeId for n in nodes.BrowseNode.Ancestors.BrowseNode]
        assert children == self.CHILDREN[api.locale]
        assert ancestors == self.ANCESTORS[api.locale]
        
        
class TestCartCreate (object):

    """
    Check that all XML responses for CartCreate are parsed correctly.
    """

    processors = ['objectify']

    def test_creating_basket_with_empty_items_fails(self, api):
        pytest.raises(ValueError, api.cart_create, {})
        pytest.raises(ValueError, api.cart_create, {'0451462009' : 0})

    def test_creating_basket_with_negative_item_quantity_fails(self, api):
        pytest.raises(ValueError, api.cart_create, {'0201896834' : -1})

    def test_creating_basket_with_quantity_too_high_fails(self, api):
        pytest.raises(ValueError, api.cart_create, {'0201896834' : 1000})

    def test_creating_basket_with_unknown_item_fails(self, api):
        pytest.raises(InvalidCartItem, api.cart_create, {'021554' : 1})

    def test_create_cart(self, api):
        root = api.cart_create({
            '0201896834' : 1, # The Art of Computer Programming Vol. 1
            '0201896842' : 1, # The Art of Computer Programming Vol. 2
       })
        cart = Cart.from_xml(root.Cart)
        assert len(cart.items) == 2
        assert cart['0201896834'].quantity == 1
        assert cart['0201896842'].quantity == 1


def pytest_funcarg__cart(request):
    api = request._funcargs['api']
    items = {
        '0201896834' : 1, # The Art of Computer Programming Vol. 1
        '0201896842' : 2, # The Art of Computer Programming Vol. 2
    }
    def create_cart():
        root = api.cart_create(items)
        cart = Cart.from_xml(root.Cart)
        print 'Cart created:', cart
        return cart
    def destroy_cart(cart):
        api.cart_clear(cart.cart_id, cart.hmac)
        print 'Cart cleared.'
    return request.cached_setup(
        setup=create_cart, teardown=destroy_cart, scope='function')


class TestCartAdd (object):

    """
    Check that all XML responses for CartAdd are parsed correctly.
    """

    processors = ['objectify']

    def test_adding_with_wrong_cartid_hmac_fails(self, api, cart):
        pytest.raises(CartInfoMismatch, api.cart_add, '???', cart.hmac, {'0201896834' : 1})
        pytest.raises(CartInfoMismatch, api.cart_add, cart.cart_id, '???', {'0201896834' : 1})

    def test_adding_empty_items_fails(self, api, cart):
        pytest.raises(ValueError, api.cart_add, cart.cart_id, cart.hmac, {})
        pytest.raises(ValueError, api.cart_add, cart.cart_id, cart.hmac, {'0451462009' : 0})

    def test_adding_negative_item_quantity_fails(self, api, cart):
        pytest.raises(ValueError, api.cart_add, cart.cart_id, cart.hmac, {'0201896834' : -1})

    def test_adding_item_quantity_too_high_fails(self, api, cart):
        pytest.raises(ValueError, api.cart_add, cart.cart_id, cart.hmac, {'0201896834' : 1000})

    def test_adding_unknown_item_fails(self, api, cart):
        pytest.raises(InvalidCartItem, api.cart_add, cart.cart_id, cart.hmac, {'021554' : 1})

    def test_adding_item_already_in_cart_fails(self, api, cart):
        pytest.raises(ItemAlreadyInCart, api.cart_add, cart.cart_id, 
                          cart.hmac, {'0201896842' : 2})

    def test_adding_item(self, api, cart):
        root = api.cart_add(cart.cart_id, cart.hmac, {
            '0201896850' : 3, # The Art of Computer Programming Vol. 3
        })
        from lxml import etree
        print etree.tostring(root.Cart, pretty_print=True)

        cart = Cart.from_xml(root.Cart)
        assert len(cart) == 6
        assert len(cart.items) == 3

        item = cart['0201896850']
        assert item.quantity == 3
        assert item.asin == '0201896850'


class TestCartModify (object):

    """
    Check that all XML responses for CartModify are parsed correctly.
    """

    processors = ['objectify']

    def test_modifying_with_wrong_cartid_hmac_fails(self, api, cart):
        pytest.raises(CartInfoMismatch, api.cart_modify, '???', cart.hmac, {'0201896834' : 1})
        pytest.raises(CartInfoMismatch, api.cart_modify, cart.cart_id, '???', {'0201896834' : 1})

    def test_modifying_empty_items_fails(self, api, cart):
        pytest.raises(ValueError, api.cart_modify, cart.cart_id, cart.hmac, {})

    def test_modifying_negative_item_quantity_fails(self, api, cart):
        pytest.raises(ValueError, api.cart_modify, cart.cart_id, cart.hmac, {'0201896834' : -1})

    def test_modifying_item_quantity_too_high_fails(self, api, cart):
        pytest.raises(ValueError, api.cart_modify, cart.cart_id, cart.hmac, {'0201896834' : 1000})

    def test_modifying_item(self, api, cart):
        root = api.cart_modify(cart.cart_id, cart.hmac, {
            # The Art of Computer Programming Vol. 2
            cart.get_itemid_for_asin('0201896842'): 0, 
        })
        from lxml import etree
        print etree.tostring(root.Cart, pretty_print=True)

        cart = Cart.from_xml(root.Cart)
        assert len(cart) == 1
        assert len(cart.items) == 1

        # 0201896842 is gone!
        pytest.raises(IndexError, lambda x: cart[x], '0201896842')

        # 0201896834 is still here!
        item = cart['0201896834']
        assert item.quantity == 1
        assert item.asin == '0201896834'

    def test_modifying_does_not_work_with_asin(self, api, cart):
        root = api.cart_modify(cart.cart_id, cart.hmac, {
            # The Art of Computer Programming Vol. 3
            '0201896842': 0, 
        })
        from lxml import etree
        print etree.tostring(root.Cart, pretty_print=True)

        cart = Cart.from_xml(root.Cart)
        assert len(cart) == 3
        assert len(cart.items) == 2


class TestCartGet (object):

    """
    Check that all XML responses for CartGet are parsed correctly.
    """

    processors = ['objectify']

    def test_getting_with_wrong_cartid_hmac_fails(self, api, cart):
        pytest.raises(CartInfoMismatch, api.cart_get, '???', cart.hmac)
        pytest.raises(CartInfoMismatch, api.cart_get, cart.cart_id, '???')

    def test_getting_cart(self, api, cart):
        root = api.cart_get(cart.cart_id, cart.hmac)
        cart = Cart.from_xml(root.Cart)
        assert len(cart) == 3
        assert len(cart.items) == 2


class TestCartClear (object):

    """
    Check that all XML responses for CartClear are parsed correctly.
    """

    processors = ['objectify']

    def test_clearing_with_wrong_cartid_hmac_fails(self, api, cart):
        pytest.raises(CartInfoMismatch, api.cart_clear, '???', cart.hmac)
        pytest.raises(CartInfoMismatch, api.cart_clear, cart.cart_id, '???')

    def test_clearing_cart(self, api, cart):
        root = api.cart_clear(cart.cart_id, cart.hmac)
        cart = Cart.from_xml(root.Cart)
        assert len(cart.items) == 0


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

    def test_calling_deprecated_operations(self, api):
        for operation in self.DEPRECATED_OPERATIONS:
            method = getattr(api, convert_camel_case(operation))
            pytest.raises(DeprecatedOperation, method)

    def test_calling_deprecated_operations_using_call_fails(self, api):
        for operation in self.DEPRECATED_OPERATIONS:
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
                tree = self.api.processor.parse(open(file))
                if not hasattr(tree, 'nsmap'):
                    raise pytest.skip('This test only works with lxml processors!')
                nspace = tree.nsmap.get(None, '')
                for item_id in tree.xpath('//aws:ItemId',
                                          namespaces={'aws' : nspace}):
                    assert item_id.pyval == item_id.text == str(item_id)
            except AWSError:
                pass

    def test_all_ASIN_elements_are_StringElement(self):
        for file in self.test_files:
            try:
                tree = self.api.processor.parse(open(file))
                if not hasattr(tree, 'nsmap'):
                    raise pytest.skip('This test only works with lxml processors!')
                nspace = tree.nsmap.get(None, '')
                for item_id in tree.xpath('//aws:ItemId',
                                          namespaces={'aws' : nspace}):
                    assert item_id.pyval == item_id.text == str(item_id)
            except AWSError:
                pass


