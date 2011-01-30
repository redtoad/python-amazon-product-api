# Copyright (C) 2009 Sebastian Rahlf <basti at redtoad dot de>
#
# This program is release under the BSD License. You can find the full text of
# the license in the LICENSE file.


__docformat__ = "restructuredtext en"

from base64 import b64encode
from datetime import datetime, timedelta

try: # make it python2.4 compatible!
    from hashlib import sha256
except ImportError: # pragma: no cover
    from Crypto.Hash import SHA256 as sha256

import hmac
import socket
from time import strftime, gmtime, sleep
import urllib2

try: # make it python2.4 compatible!
    from urllib2 import quote
except ImportError: # pragma: no cover
    from urllib import quote

from amazonproduct.version import VERSION
from amazonproduct.errors import *
from amazonproduct.paginators import paginate
from amazonproduct.processors import LxmlObjectifyProcessor

USER_AGENT = ('python-amazon-product-api/%s '
    '+http://pypi.python.org/pypi/python-amazon-product-api/' % VERSION)

#: Hosts used by Amazon for normal/XSLT operations
HOSTS = {
    'ca' : ('ecs.amazonaws.ca', 'xml-ca.amznxslt.com'),
    'de' : ('ecs.amazonaws.de', 'xml-de.amznxslt.com'),
    'fr' : ('ecs.amazonaws.fr', 'xml-fr.amznxslt.com'),
    'jp' : ('ecs.amazonaws.jp', 'xml-jp.amznxslt.com'),
    'uk' : ('ecs.amazonaws.co.uk', 'xml-uk.amznxslt.com'),
    'us' : ('ecs.amazonaws.com', 'xml-us.amznxslt.com'),
}

class API (object):

    """
    Wrapper class for the Amazon Product Advertising API. You will need both an
    AWS access key id and the secret counterpart.

    Example::

        AWS_KEY = '...'
        SECRET_KEY = '...'

        api = ProductAdvertisingAPI(AWS_KEY, SECRET_KEY, 'us')
        root = api.item_lookup('9783836214063', IdType='ISBN',
                    SearchIndex='Books', ResponseGroup='Reviews', ReviewPage=1)

        rating = root.Items.Item.CustomerReviews.AverageRating.pyval
        total_reviews = root.Items.Item.CustomerReviews.TotalReviews.pyval
        review_pages = root.Items.Item.CustomerReviews.TotalReviewPages.pyval

    It is possible to use a different module for parsing the XML response. For
    instance, you can use ``xml.minidom`` instead of ``lxml`` by defining a
    custom result processor::

        def minidom_response_parser(fp):
            root = parse(fp)
            # parse errors
            for error in root.getElementsByTagName('Error'):
                code = error.getElementsByTagName('Code')[0].firstChild.nodeValue
                msg = error.getElementsByTagName('Message')[0].firstChild.nodeValue
                raise AWSError(code, msg)
            return root
        api = API(AWS_KEY, SECRET_KEY, processor=minidom_response_parser)
        root = api.item_lookup('0718155157')
        print root.toprettyxml()
        # ...

    Just make sure it raises an ``AWSError`` with the appropriate error code
    and message. For a more complex example, have a look at the default
    LxmlObjectifyResponseProcessor class.
    """

    VERSION = '2010-12-01' #: supported Amazon API version
    REQUESTS_PER_SECOND = 1 #: max requests per second
    TIMEOUT = 5 #: timeout in seconds

    def __init__(self, access_key_id, secret_access_key, locale,
                 associate_tag=None, processor=None):
        """
        :param access_key_id: AWS access key ID.
        :param secret_key_id: AWS secret key.
        :param associate_tag: Amazon Associates tracking id.
        :param locale: localise results by using one value from ``LOCALES``.
        :param processor: result processing function (``None`` if unsure).
        """
        self.access_key = access_key_id
        self.secret_key = secret_access_key
        self.associate_tag = associate_tag

        try:
            self.host = HOSTS[locale]
            self.locale = locale
        except KeyError:
            raise UnknownLocale(locale)

        socket.setdefaulttimeout(self.TIMEOUT)

        self.last_call = datetime(1970, 1, 1)
        self.throttle = timedelta(seconds=1)/self.REQUESTS_PER_SECOND
        self.debug = 0 # set to 1 if you want to see HTTP headers

        self.response_processor = processor or LxmlObjectifyProcessor()

    def _build_url(self, **qargs):
        """
        Builds a signed URL for querying Amazon AWS.  This function is based
        on code by Adam Cox (found at
        http://blog.umlungu.co.uk/blog/2009/jul/12/pyaws-adding-request-authentication/)
        """
        # remove empty (=None) parameters
        for key, val in qargs.items():
            if val is None:
                del qargs[key]

        if 'AWSAccessKeyId' not in qargs:
            qargs['AWSAccessKeyId'] = self.access_key

        if 'Service' not in qargs:
            qargs['Service'] = 'AWSECommerceService'

        # use the version this class was build for by default
        if 'Version' not in qargs:
            qargs['Version'] = self.VERSION

        if 'AssociateTag' not in qargs and self.associate_tag:
            qargs['AssociateTag'] = self.associate_tag

        # add timestamp (this is required when using a signature)
        qargs['Timestamp'] = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())

        # create signature
        keys = sorted(qargs.keys())
        args = '&'.join('%s=%s' % (key, quote(unicode(qargs[key])
                        .encode('utf-8'),safe='~')) for key in keys)

        # Amazon uses a different host for XSLT operations
        host = self.host['Style' in qargs]

        msg = 'GET'
        msg += '\n' + host
        msg += '\n/onca/xml'
        msg += '\n' + args

        signature = quote(
            b64encode(hmac.new(self.secret_key, msg, sha256).digest()))

        url = 'http://%s/onca/xml?%s&Signature=%s' % (host, args, signature)
        return url

    def _fetch(self, url):
        """
        Calls the Amazon Product Advertising API and returns the response.
        """
        request = urllib2.Request(url)
        request.add_header('User-Agent', USER_AGENT)
        request.add_header('Accept-encoding', 'gzip')

        # Be nice and wait for some time
        # before submitting the next request
        delta = datetime.now() - self.last_call
        if delta < self.throttle:
            wait = self.throttle-delta
            sleep(wait.seconds+wait.microseconds/1000000.0) # pragma: no cover
        self.last_call = datetime.now()

        try:
            opener = urllib2.build_opener()
            handler = urllib2.HTTPHandler(debuglevel=self.debug)
            opener = urllib2.build_opener(handler)
            response = opener.open(request)
            # handle compressed data
            # Borrowed from Mark Pilgrim's excellent introduction
            # http://diveintopython.org/http_web_services/gzip_compression.html
            if response.headers.get('Content-Encoding') == 'gzip':
                import StringIO
                import gzip
                stream = StringIO.StringIO(response.read())
                return gzip.GzipFile(fileobj=stream)
            return response
        except urllib2.HTTPError, e:
            if e.code == 503:
                raise TooManyRequests
            # otherwise re-raise
            raise # pragma: no cover

    def _reg(self, key):
        """
        Returns the appropriate regular expression (compiled) to parse an error
        message depending on the current locale.
        """
        if self.locale == 'jp':
            return JAPANESE_ERROR_REGS[key]
        return DEFAULT_ERROR_REGS[key]

    def _parse(self, fp):
        """
        Processes the AWS response (file like object). XML is fed in, some
        usable output comes out. It will use a different result_processor if
        you have defined one.
        """
        try:
            return self.response_processor(fp)
        except AWSError, e:

            if e.code == 'Deprecated':
                raise DeprecatedOperation(e.msg)

            if e.code == 'AWS.ECommerceService.NoExactMatches':
                raise NoExactMatchesFound

            if e.code == 'AWS.ECommerceService.NoExactMatches':
                raise NoExactMatchesFound

            if e.code == 'AWS.InvalidParameterValue':
                m = self._reg('invalid-parameter-value').search(e.msg)
                raise InvalidParameterValue(m.group('parameter'),
                                            m.group('value'))

            if e.code == 'AWS.RestrictedParameterValueCombination':
                m = self._reg('invalid-parameter-combination').search(e.msg)
                raise InvalidParameterCombination(m.group('message'))

            # otherwise simply re-raise
            raise

    def call(self, **qargs):
        """
        Builds a signed URL for the operation, fetches the result from Amazon
        and parses the XML. If you want to customise things at any stage, simply
        override the respective method(s):

        * ``_build_url(**query_parameters)``
        * ``_fetch(url)``
        * ``_parse(fp)``
        """
        url = self._build_url(**qargs)
        try:
            fp = self._fetch(url)
            return self._parse(fp)
        except urllib2.HTTPError, e:
            # HTTP errors 400 (Bad Request) and 410 (Gone) send a more detailed
            # error message as body which can be parsed, too.
            if e.code in (400, 410):
                return self._parse(e.fp)
            raise

    def item_lookup(self, item_id, **params):
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
            return self.call(Operation='ItemLookup', ItemId=item_id, **params)
        except AWSError, e:

            if (e.code == 'AWS.InvalidEnumeratedParameter'
            and self._reg('invalid-value').search(e.msg)
                    .group('parameter') == 'SearchIndex'):
                raise InvalidSearchIndex(params.get('SearchIndex'))

            if e.code == 'AWS.InvalidResponseGroup':
                raise InvalidResponseGroup(params.get('ResponseGroup'))

            # otherwise re-raise exception
            raise # pragma: no cover

    @paginate
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
            return self.call(Operation='ItemSearch',
                                  SearchIndex=search_index, **params)
        except AWSError, e:

            if (e.code == 'AWS.InvalidEnumeratedParameter'
            and self._reg('invalid-value').search(e.msg)):
                raise InvalidSearchIndex(search_index)

            if e.code == 'AWS.InvalidResponseGroup':
                raise InvalidResponseGroup(params.get('ResponseGroup'))

            # otherwise re-raise exception
            raise # pragma: no cover

    def similarity_lookup(self, *ids, **params):
        """
        The ``SimilarityLookup`` operation returns up to ten products per page
        that are similar to one or more items specified in the request. This
        operation is typically used to pique a customer's interest in buying
        something similar to what they've already ordered.

        If you specify more than one item, ``SimilarityLookup`` returns the
        intersection of similar items each item would return separately.
        Alternatively, you can use the ``SimilarityType`` parameter to return
        the union of items that are similar to any of the specified items. A
        maximum of ten similar items are returned; the operation does not
        return additional pages of similar items. If there are more than ten
        similar items, running the same request can result in different answers
        because the ten that are included in the response are picked randomly.
        The results are picked randomly only when you specify multiple items
        and the results include more than ten similar items.
        """
        item_id = ','.join(ids)
        try:
            return self.call(Operation='SimilarityLookup',
                              ItemId=item_id, **params)
        except AWSError, e:

            if e.code == 'AWS.ECommerceService.NoSimilarities':
                asin = self._reg('no-similarities').search(e.msg).group('ASIN')
                raise NoSimilarityForASIN(asin)

    def browse_node_lookup(self, browse_node_id, response_group=None, **params):
        """
        Given a browse node ID, ``BrowseNodeLookup`` returns the specified
        browse node's name, children, and ancestors. The names and browse node
        IDs of the children and ancestor browse nodes are also returned.
        ``BrowseNodeLookup`` enables you to traverse the browse node hierarchy
        to find a browse node.

        As you traverse down the hierarchy, you refine your search and limit
        the number of items returned. For example, you might traverse the
        following hierarchy: ``DVD>Used DVDs>Kids and Family``, to select out
        of all the DVDs offered by Amazon only those that are appropriate for
        family viewing. Returning the items associated with ``Kids and Family``
        produces a much more targeted result than a search based at the level
        of ``Used DVDs``.

        Alternatively, by traversing up the browse node tree, you can
        determine the root category of an item. You might do that, for
        example, to return the top seller of the root product category using
        the ``TopSeller`` response group in an ``ItemSearch`` request.

        You can use ``BrowseNodeLookup`` iteratively to navigate through the
        browse node hierarchy to reach the node that most appropriately suits
        your search. Then you can use the browse node ID in an ItemSearch
        request. This response would be far more targeted than, for example,
        searching through all of the browse nodes in a search index.

        :param browse_node_id: A positive integer assigned by Amazon that
          uniquely identifies a product category.
          Default: None
          Valid Values: A positive integer.
        :type browse_node_id: str
        :param response_group: Specifies the types of values to return. You can
          specify multiple response groups in one request by separating them
          with commas.
          Default: ``BrowseNodeInfo``
          Valid Values: ``MostGifted``, ``NewReleases``, ``MostWishedFor``,
          ``TopSellers``
        """
        try:
            return self.call(Operation='BrowseNodeLookup',
                    BrowseNodeId=browse_node_id, ResponseGroup=response_group,
                    **params)
        except AWSError, e:

            if e.code == 'AWS.InvalidResponseGroup':
                raise InvalidResponseGroup(params.get('ResponseGroup'))

            # otherwise re-raise exception
            raise # pragma: no cover

    def _convert_cart_items(self, items, key='ASIN'):
        """
        Converts items into correct format for cart operations.
        """
        result = {}
        # TODO ListItemId
        if type(items) == dict:
            for no, (item_id, quantity) in enumerate(items.items()):
                result['Item.%i.%s' % (no+1, key)] = item_id
                result['Item.%i.Quantity' % (no+1)] = quantity
        return result

    def cart_create(self, items, **params):
        """
        The ``CartCreate`` operation enables you to create a remote shopping
        cart.  A shopping cart is the metaphor used by most e-commerce
        solutions. It is a temporary data storage structure that resides on
        Amazon servers.  The structure contains the items a customer wants to
        buy. In Product Advertising API, the shopping cart is considered remote
        because it is hosted by Amazon servers. In this way, the cart is remote
        to the vendor's web site where the customer views and selects the items
        they want to purchase.

        Once you add an item to a cart by specifying the item's ListItemId and
        ASIN, or OfferListing ID, the item is assigned a ``CartItemId`` and
        accessible only by that value. That is, in subsequent requests, an item
        in a cart cannot be accessed by its ``ListItemId`` and ``ASIN``, or
        ``OfferListingId``. ``CartItemId`` is returned by ``CartCreate``,
        ``CartGet``, and C``artAdd``.

        Because the contents of a cart can change for different reasons, such
        as item availability, you should not keep a copy of a cart locally.
        Instead, use the other cart operations to modify the cart contents. For
        example, to retrieve contents of the cart, which are represented by
        CartItemIds, use ``CartGet``.

        Available products are added as cart items. Unavailable items, for
        example, items out of stock, discontinued, or future releases, are
        added as SaveForLaterItems. No error is generated. The Amazon database
        changes regularly. You may find a product with an offer listing ID but
        by the time the item is added to the cart the product is no longer
        available. The checkout page in the Order Pipeline clearly lists items
        that are available and those that are SaveForLaterItems.

        It is impossible to create an empty shopping cart. You have to add at
        least one item to a shopping cart using a single ``CartCreate``
        request.  You can add specific quantities (up to 999) of each item.

        ``CartCreate`` can be used only once in the life cycle of a cart. To
        modify the contents of the cart, use one of the other cart operations.

        Carts cannot be deleted. They expire automatically after being unused
        for 7 days. The lifespan of a cart restarts, however, every time a cart
        is modified. In this way, a cart can last for more than 7 days. If, for
        example, on day 6, the customer modifies a cart, the 7 day countdown
        starts over.
        """
        try:
            params.update(self._convert_cart_items(items))
            return self.call(Operation='CartCreate', **params)
        except AWSError, e:

            if e.code == 'AWS.MissingParameters':
                raise ValueError(e.msg)

            if e.code == 'AWS.ParameterOutOfRange':
                raise ValueError(e.msg)

            if e.code == 'AWS.ECommerceService.ItemNotEligibleForCart':
                raise InvalidCartItem(e.msg)

            # otherwise re-raise exception
            raise # pragma: no cover

    def cart_add(self, cart_id, hmac, items, **params):
        """
        The ``CartAdd`` operation enables you to add items to an existing
        remote shopping cart. ``CartAdd`` can only be used to place a new item
        in a shopping cart. It cannot be used to increase the quantity of an
        item already in the cart. If you would like to increase the quantity of
        an item that is already in the cart, you must use the ``CartModify``
        operation.

        You add an item to a cart by specifying the item's ``OfferListingId``,
        or ``ASIN`` and ``ListItemId``. Once in a cart, an item can only be
        identified by its ``CartItemId``. That is, an item in a cart cannot be
        accessed by its ASIN or OfferListingId. CartItemId is returned by
        ``CartCreate``, ``CartGet``, and ``CartAdd``.

        To add items to a cart, you must specify the cart using the ``CartId``
        and ``HMAC`` values, which are returned by the ``CartCreate``
        operation.

        If the associated CartCreate request specified an AssociateTag, all
        ``CartAdd`` requests must also include a value for Associate Tag
        otherwise the request will fail.

        .. note:: Some manufacturers have a minimum advertised price (MAP) that
        can be displayed on Amazon's retail web site. In these cases, when
        performing a Cart operation, the MAP Is returned instead of the actual
        price. The only way to see the actual price is to add the item to a
        remote shopping cart and follow the PurchaseURL. The actual price will
        be the MAP or lower.
        """
        try:
            params.update({
                'CartId' : cart_id,
                'HMAC' : hmac,
            })
            params.update(self._convert_cart_items(items))
            return self.call(Operation='CartAdd', **params)
        except AWSError, e:

            if e.code == 'AWS.ECommerceService.InvalidCartId':
                raise InvalidCartId

            if e.code == 'AWS.ECommerceService.CartInfoMismatch':
                raise CartInfoMismatch

            if e.code == 'AWS.MissingParameters':
                raise ValueError(e.msg)

            if e.code == 'AWS.ParameterOutOfRange':
                raise ValueError(e.msg)

            if e.code == 'AWS.ECommerceService.ItemNotEligibleForCart':
                raise InvalidCartItem(e.msg)

            if e.code == 'AWS.ECommerceService.ItemAlreadyInCart':
                if self.locale == 'jp': print e.msg
                item = self._reg('already-in-cart').search(e.msg).group('item')
                raise ItemAlreadyInCart(item)

            # otherwise re-raise exception
            raise # pragma: no cover

    def cart_modify(self, cart_id, hmac, items, **params):
        """
        The ``CartModify`` operation enables you to change the quantity of
        items that are already in a remote shopping cart and move items from
        the active area of a cart to the SaveForLater area or the reverse.

        To modify the number of items in a cart, you must specify the cart
        using the CartId and HMAC values that are returned in the CartCreate
        operation. A value similar to HMAC, URLEncodedHMAC, is also returned.
        This value is the URL encoded version of the HMAC. This encoding is
        necessary because some characters, such as + and /, cannot be included
        in a URL. Rather than encoding the HMAC yourself, use the
        URLEncodedHMAC value for the HMAC parameter.

        You can use ``CartModify`` to modify the number of items in a remote
        shopping cart by setting the value of the Quantity parameter
        appropriately. You can eliminate an item from a cart by setting the
        value of the Quantity parameter to zero. Or, you can double the number
        of a particular item in the cart by doubling its Quantity . You cannot,
        however, use ``CartModify`` to add new items to a cart.

        If the associated CartCreate request specified an AssociateTag, all
        ``CartModify`` requests must also include a value for Associate Tag
        otherwise the request will fail.
        """
        # TODO Action=SaveForLater
        try:
            params.update({
                'CartId' : cart_id,
                'HMAC' : hmac,
            })
            params.update(self._convert_cart_items(items, key='CartItemId'))
            return self.call(Operation='CartModify', **params)
        except AWSError, e:

            if e.code == 'AWS.ECommerceService.CartInfoMismatch':
                raise CartInfoMismatch

            if e.code == 'AWS.MissingParameters':
                raise ValueError(e.msg)

            if e.code == 'AWS.ParameterOutOfRange':
                raise ValueError(e.msg)

            if e.code == 'AWS.ECommerceService.ItemNotEligibleForCart':
                raise InvalidCartItem(e.msg)

            # otherwise re-raise exception
            raise # pragma: no cover

    def cart_get(self, cart_id, hmac, **params):
        """
        The ``CartGet`` operation enables you to retrieve the IDs, quantities,
        and prices of all of the items, including SavedForLater items in a
        remote shopping cart.

        Because the contents of a cart can change for different reasons, such
        as availability, you should not keep a copy of a cart locally. Instead,
        use ``CartGet`` to retrieve the items in a remote shopping cart.

        To retrieve the items in a cart, you must specify the cart using the
        ``CartId`` and ``HMAC`` values, which are returned in the
        ``CartCreate`` operation.  A value similar to HMAC, ``URLEncodedHMAC``,
        is also returned. This value is the URL encoded version of the
        ``HMAC``. This encoding is necessary because some characters, such as
        ``+`` and ``/``, cannot be included in a URL.  Rather than encoding the
        ``HMAC`` yourself, use the ``URLEncodedHMAC`` value for the HMAC
        parameter.

        ``CartGet`` does not work after the customer has used the
        ``PurchaseURL`` to either purchase the items or merge them with the
        items in their Amazon cart.

        If the associated ``CartCreate`` request specified an ``AssociateTag``,
        all ``CartGet`` requests must also include a value for ``AssociateTag``
        otherwise the request will fail.
        """
        try:
            params.update({
                'CartId' : cart_id,
                'HMAC' : hmac,
            })
            return self.call(Operation='CartGet', **params)
        except AWSError, e:

            if e.code == 'AWS.ECommerceService.CartInfoMismatch':
                raise CartInfoMismatch

            # otherwise re-raise exception
            raise # pragma: no cover

    def cart_clear(self, cart_id, hmac, **params):
        """
        The ``CartClear`` operation enables you to remove all of the items in a
        remote shopping cart, including SavedForLater items. To remove only
        some of the items in a cart or to reduce the quantity of one or more
        items, use ``CartModify``.

        To delete all of the items from a remote shopping cart, you must
        specify the cart using the ``CartId`` and ``HMAC`` values, which are
        returned by the ``CartCreate`` operation. A value similar to the
        ``HMAC``, ``URLEncodedHMAC``, is also returned. This value is the URL
        encoded version of the ``HMAC``. This encoding is necessary because
        some characters, such as ``+`` and ``/``, cannot be included in a URL.
        Rather than encoding the ``HMAC`` yourself, use the U``RLEncodedHMAC``
        value for the HMAC parameter.

        ``CartClear`` does not work after the customer has used the
        ``PurchaseURL`` to either purchase the items or merge them with the
        items in their Amazon cart.

        Carts exist even though they have been emptied. The lifespan of a cart
        is 7 days since the last time it was acted upon. For example, if a cart
        created 6 days ago is modified, the cart lifespan is reset to 7 days.
        """
        try:
            params.update({
                'CartId' : cart_id,
                'HMAC' : hmac,
            })
            return self.call(Operation='CartClear', **params)
        except AWSError, e:

            if e.code == 'AWS.ECommerceService.CartInfoMismatch':
                raise CartInfoMismatch

            # otherwise re-raise exception
            raise # pragma: no cover

    def deprecated_operation(self, *args, **kwargs):
        """
        Some operations are deprecated and will be answered with HTTP 410. To
        avoid unnecessary API calls, a ``DeprecatedOperation`` exception is
        thrown straight-away.
        """
        raise DeprecatedOperation

    # shortcuts for deprecated operations
    customer_content_lookup = customer_content_search = deprecated_operation
    help = deprecated_operation
    list_lookup = list_search = deprecated_operation
    tag_lookup = deprecated_operation
    transaction_lookup = deprecated_operation
    vehicle_part_lookup = vehicle_part_search = deprecated_operation
    vehicle_search = deprecated_operation

    #: MultiOperation is supported outside this API
    multi_operation = None

