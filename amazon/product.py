
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

__docformat__ = "restructuredtext en"

LOCALES = {
    'ca' : 'http://ecs.amazonaws.ca/onca/xml', 
    'de' : 'http://ecs.amazonaws.de/onca/xml', 
    'fr' : 'http://ecs.amazonaws.fr/onca/xml', 
    'jp' : 'http://ecs.amazonaws.jp/onca/xml', 
    'uk' : 'http://ecs.amazonaws.co.uk/onca/xml', 
    'us' : 'http://ecs.amazonaws.com/onca/xml', 
}

from base64 import b64encode
from hashlib import sha256
import hmac
from lxml import objectify
from time import strftime, gmtime
from urlparse import urlsplit
from urllib2 import quote, urlopen

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

class ProductAdvertisingAPI (object):
    
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
        Looks up one specific item.
        """
        try:
            url = self._build_url(Operation='ItemLookup', ItemId=id, **params)
            return self._call(url)
        except AWSError, e:
            if (e.code=='AWS.InvalidEnumeratedParameter' 
            and e.msg.startswith('The value you specified for SearchIndex '
                                 'is invalid.')):
                raise InvalidSearchIndex(params.get('SearchIndex'))
            
            elif e.code=='AWS.InvalidResponseGroup': 
                raise InvalidResponseGroup(params.get('ResponseGroup'))
            
            # otherwise re-raise exception
            raise
        
    def item_search(self, search_index, **params):
        """
        Looks up one specific item.
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
