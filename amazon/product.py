
"""
Amazon Product Advertising API
==============================

    The Product Advertising API provides programmatic access to Amazon's
    product selection and discovery functionality so that developers like you
    can advertise Amazon products to monetize your website.
    
    The Product Advertising API helps you advertise Amazon products using
    product search and look up capability, product information and features
    such as Customer Reviews, Similar Products, Wish Lists and New and Used
    listings. You can make money using the Product Advertising API to advertise
    Amazon products in conjunction with the Amazon Associates program. Be sure
    to join the Amazon Associates program to earn up to 15% in referral fees
    when the users you refer to Amazon sites buy qualifying products.  

More info can be found at
https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

Requirements
------------

You need an Amazon Webservice account.

Kudos
-----

The ``_build_url()`` function is based on code by Adam Cox (found at 
http://blog.umlungu.co.uk/blog/2009/jul/12/pyaws-adding-request-authentication/)

"""

from base64 import b64encode
from hashlib import sha256
import hmac
from lxml import objectify
import re
from time import strftime, gmtime
from urlparse import urlsplit
from urllib2 import quote, urlopen

__docformat__ = "restructuredtext en"

LOCALES = {
    'ca' : 'http://ecs.amazonaws.ca/onca/xml', 
    'de' : 'http://ecs.amazonaws.de/onca/xml', 
    'fr' : 'http://ecs.amazonaws.fr/onca/xml', 
    'jp' : 'http://ecs.amazonaws.jp/onca/xml', 
    'uk' : 'http://ecs.amazonaws.co.uk/onca/xml', 
    'us' : 'http://ecs.amazonaws.com/onca/xml', 
}

class UnknownLocale (Exception):
    """
    Raised when unknown locale is specified.
    """
    
class AWSError (Exception):
    """
    Generic AWS error message.
    """
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return '%(code)s: %(msg)s' % self.__dict__
    
class InvalidSearchIndex (Exception):
    """
    The value specified for SearchIndex is invalid. Valid values include:

    All, Apparel, Automotive, Baby, Beauty, Blended, Books, Classical, DVD,
    Electronics, ForeignBooks, HealthPersonalCare, HomeGarden, HomeImprovement,
    Jewelry, Kitchen, Magazines, MP3Downloads, Music, MusicTracks,
    OfficeProducts, OutdoorLiving, PCHardware, Photo, Shoes, Software,
    SoftwareVideoGames, SportingGoods, Tools, Toys, VHS, Video, VideoGames,
    Watches
    """
    
class InvalidResponseGroup (Exception):
    """
    The specified ResponseGroup parameter is invalid. Valid response groups for
    ItemLookup requests include:

    Accessories, AlternateVersions, BrowseNodes, Collections, EditorialReview,
    Images, ItemAttributes, ItemIds, Large, ListmaniaLists, Medium,
    MerchantItemAttributes, OfferFull, OfferListings, OfferSummary, Offers,
    PromotionDetails, PromotionSummary, PromotionalTag, RelatedItems, Request,
    Reviews, SalesRank, SearchBins, SearchInside, ShippingCharges,
    Similarities, Small, Subjects, Tags, TagsSummary, Tracks, VariationImages,
    VariationMatrix, VariationMinimum, VariationOffers, VariationSummary,
    Variations.
    """

class InvalidItemId (Exception):
    """
    The specified ItemId parameter is invalid. Please change this value and 
    retry your request.
    """

INVALID_SEARCH_INDEX_REG = re.compile(
    'The value you specified for SearchIndex is invalid.')

INVALID_ITEMID_REG = re.compile('.+? is not a valid value for ItemId. '
    'Please change this value and retry your request.')

class API (object):
    
    """
    Wrapper class for the Amazon Product Advertising API. You will need both an 
    AWS access key id and the secret counterpart.
    
    Example::
    
        AWS_KEY = '...'
        SECRET_KEY = '...'
        
        api = ProductAdvertisingAPI(AWS_KEY, SECRET_KEY)
        root = api.item_lookup('987311264224', IdType='ISBN', 
                    SearchIndex='Books', ResponseGroup='Reviews', ReviewPage=1)
        
        rating = root.Items.Item.CustomerReviews.AverageRating.pyval
        total_reviews = root.Items.Item.CustomerReviews.TotalReviews.pyval
        review_pages = root.Items.Item.CustomerReviews.TotalReviewPages.pyval

    """
    
    VERSION = '2009-07-01' #: supported Amazon API version
    
    def __init__(self, access_key_id, secret_access_key, locale='de'):
        
        self.access_key = access_key_id
        self.secret_key = secret_access_key
        
        try:
            parts = urlsplit(LOCALES[locale])
            self.scheme = parts.scheme
            self.host = parts.netloc
            self.path = parts.path
        except KeyError:
            raise UnknownLocale(locale)
        
    def _build_url(self, **qargs):
        """
        Builds a signed URL for querying Amazon AWS.
        """
        
        if 'AWSAccessKeyId' not in qargs:
            qargs['AWSAccessKeyId'] = self.access_key
            
        if 'Service' not in qargs:
            qargs['Service'] = 'AWSECommerceService'
            
        # use the version this class was build for by default
        if 'Version' not in qargs:
            qargs['Version'] = self.VERSION
            
        # add timestamp (this is required when using a signature)
        qargs['Timestamp'] = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
        
        # create signature
        keys = sorted(qargs.keys())
        args = '&'.join('%s=%s' % (key, quote(str(qargs[key]))) 
                        for key in keys)
        
        msg = 'GET'
        msg += '\n' + self.host
        msg += '\n' + self.path
        msg += '\n' + args.encode('utf-8')
        
        signature = quote(
            b64encode(hmac.new(self.secret_key, msg, sha256).digest()))
        
        url = '%s://%s%s?%s&Signature=%s' % (self.scheme, self.host, self.path, 
                                             args, signature)
        return url
    
    def _call(self, url):
        """
        Calls the Amazon Product Advertising API and objectifies the response.
        """
        tree = objectify.parse(urlopen(url))
        root = tree.getroot()
        
        #~ from lxml import etree
        #~ print etree.tostring(tree, pretty_print=True)
        
        nspace = root.nsmap.get(None, '')
        errors = root.xpath('//aws:Request/aws:Errors/aws:Error', 
                         namespaces={'aws' : nspace})
        
        for error in errors:
            raise AWSError(error.Code.text, error.Message.text)
        
        #~ from lxml import etree
        #~ print etree.tostring(root, pretty_print=True)
        return root
    
    def item_lookup(self, id, **params):
        """
        Given an Item identifier, the ``ItemLookup`` operation returns some or
        all of the item attributes, depending on the response group specified
        in the request. By default, ``ItemLookup`` returns an item's ``ASIN``,
        ``DetailPageURL``, ``Manufacturer``, ``ProductGroup``, and ``Title`` of
        the item.
        
        ``ItemLookup`` supports many response groups, so you can retrieve many
        different kinds of product information, called item attributes,
        including product reviews, variations, similar products, pricing,
        availability, images of products, accessories, and other information.
        
        To look up more than one item at a time, separate the item identifiers
        by commas. 
        """
        try:
            url = self._build_url(Operation='ItemLookup', ItemId=id, **params)
            return self._call(url)
        except AWSError, e:
            
            if (e.code=='AWS.InvalidEnumeratedParameter' 
            and INVALID_SEARCH_INDEX_REG.search(e.msg)):
                raise InvalidSearchIndex(params.get('SearchIndex'))
            
            if e.code=='AWS.InvalidResponseGroup': 
                raise InvalidResponseGroup(params.get('ResponseGroup'))
            
            if (e.code=='AWS.InvalidParameterValue' 
            and INVALID_ITEMID_REG.search(e.msg)):
                raise InvalidItemId(id)
            
            # otherwise re-raise exception
            raise
        
    def item_search(self, search_index, **params):
        """
        The ``ItemSearch`` operation returns items that satisfy the search
        criteria, including one or more search indices.

        ``ItemSearch`` returns up to ten search results at a time. When
        ``condition`` equals "All," ``ItemSearch`` returns up to three offers
        per condition (if they exist), for example, three new, three used,
        three refurbished, and three collectible items. Or, for example, if
        there are no collectible or refurbished offers, ``ItemSearch`` returns
        three new and three used offers.

        Because there are thousands of items in each search index,
        ``ItemSearch`` requires that you specify the value for at least one
        parameter in addition to a search index. The additional parameter value
        must reference items within the specified search index. For example,
        you might specify a browse node (BrowseNode is an ``ItemSearch``
        parameter), Harry Potter Books, within the Books product category. You
        would not get results, for example, if you specified the search index
        to be Automotive and the browse node to be Harry Potter Books. In this
        case, the parameter value is not associated with the search index
        value.

        The ``ItemPage`` parameter enables you to return a specified page of
        results. The maximum ``ItemPage`` number that can be returned is 400.
        An error is returned if you try to access higher numbered pages. If you
        do not include ``ItemPage`` in your request, the first page will be
        returned by default. There can be up to ten items per page.

        ``ItemSearch`` is the operation that is used most often in requests. In
        general, when trying to find an item for sale, you use this operation.
        """
        try:
            url = self._build_url(Operation='ItemSearch', 
                                  SearchIndex=search_index, **params)
            return self._call(url)
        except AWSError, e:
            
            # check for specific exceptions
            if (e.code=='AWS.InvalidEnumeratedParameter' 
            and e.msg.startswith('The value you specified for SearchIndex '
                                 'is invalid.')):
                raise InvalidSearchIndex(search_index)
            
            if e.code=='AWS.InvalidResponseGroup': 
                raise InvalidResponseGroup(params.get('ResponseGroup'))
            
            # otherwise re-raise exception
            raise
    

class ResultPaginator (object):
    
    """
    Wrapper class for paginated results. This class will call the passed 
    function iteratively until either the specified limit is reached or all 
    result pages are fetched.
    
    A small example fetching reviews for a book::
        
        api = API(AWS_KEY, SECRET_KEY)
        paginator = ResultPaginator('ReviewPage',
            '//aws:Items/aws:Request/aws:ItemLookupRequest/aws:ReviewPage',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviewPages',
            '//aws:Items/aws:Item/aws:CustomerReviews/aws:TotalReviews')
        
        for root in paginator(api.item_lookup, id=isbn, IdType='ISBN', 
                             SearchIndex='Books', ResponseGroup='Reviews'):
            ...
    
    """
    
    def __init__(self, counter, curent_page, total_pages, total_results, 
                 limit=None, nspace=None):
        """
        :param counter: counter variable passed to AWS.
        :param current_page: XPath expression locating current paginator page.
        :param total_pages: XPath expression locating total number of pages.
        :param total_results: XPath expression locating total number of results. 
        :param limit: limit fetched pages to this amount. 
        :param nspace: used XML name space. 
        """
        self.counter = counter
        self.current_page_xpath = curent_page
        self.total_pages_xpath = total_pages
        self.total_results_xpath = total_results
        
        self.limit = limit
        self.nspace = nspace
        
    def __call__(self, fun, **kwargs):
        """
        Iterate over all paginated results of ``fun``.
        """
        current_page = 0
        total_pages = 1
        
        kwargs[self.counter] = kwargs.get(self.counter, 1)
        
        while (current_page < total_pages 
        and (self.limit is None or current_page < self.limit)):
            
            root = fun(**kwargs)
            
            if self.nspace is None:
                self.nspace = root.nsmap.get(None, '')
        
            current_page = self.get_current_page_numer(root)
            total_results = self.get_total_results(root)
            total_pages = self.get_total_page_numer(root)
            
            yield root
            
            kwargs[self.counter] += 1
        
    def get_total_page_numer(self, root):
        """
        Get total number of paginator pages.
        """
        return root.xpath(self.total_pages_xpath, 
                          namespaces={'aws' : self.nspace})[0].pyval
        
    def get_current_page_numer(self, root):
        """
        Get number of current paginator page.
        """
        return root.xpath(self.current_page_xpath, 
                          namespaces={'aws' : self.nspace})[0].pyval
    
    def get_total_results(self, root):
        """
        Get number of current paginator page.
        """
        return root.xpath(self.total_results_xpath, 
                          namespaces={'aws' : self.nspace})[0].pyval
