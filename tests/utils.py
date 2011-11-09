
from lxml import etree, objectify
import os.path
import re
from StringIO import StringIO
import urllib2

try: # make it python2.4/2.5 compatible!
    from urlparse import urlparse, parse_qs
except ImportError: # pragma: no cover
    from urlparse import urlparse
    from cgi import parse_qs

from amazonproduct.api import API
from amazonproduct.errors import AWSError

from tests import XML_TEST_DIR, TESTABLE_API_VERSIONS, TESTABLE_LOCALES
from tests import AWS_KEY, SECRET_KEY 


def convert_camel_case(operation):
    """
    Converts ``CamelCaseOperationName`` into ``python_style_method_name``.
    """
    return re.sub('([a-z])([A-Z])', r'\1_\2', operation).lower()

def extract_operations_from_wsdl(path):
    """
    Extracts operations from Amazon's WSDL file.
    """
    root = objectify.parse(open(path)).getroot()
    wsdlns = 'http://schemas.xmlsoap.org/wsdl/'
    return set(root.xpath('//ws:operation/@name', namespaces={'ws' : wsdlns}))


class Cart (object):

    """
    Convenience class for testing XML responses of CartXXX operations..
    """

    class Item (object):

        def __repr__(self):
            return '<Item %ix %s (=%s %s)>' % (
                self.quantity, self.asin, self.price[0], self.price[1])

        @staticmethod
        def from_xml(node):
            """
            Takes <CartItem> node as ``lxml.objectify``d element and returns a 
            CartItem instance.
            """
            item = Cart.Item()
            item.item_id = node.CartItemId.pyval
            item.asin = node.ASIN.pyval
            item.seller = node.SellerNickname.pyval
            item.quantity = node.Quantity.pyval
            item.title = node.Title.pyval
            item.product_group = node.ProductGroup.pyval
            item.price = (
                node.Price.Amount.pyval, 
                node.Price.CurrencyCode.pyval)
            item.total = (
                node.ItemTotal.Amount.pyval, 
                node.ItemTotal.CurrencyCode.pyval)
            return item

    def __init__(self):
        self.items = []

    def __getitem__(self, key):
        for item in self.items:
            if key in (item.asin, item.item_id):
                return item
        raise IndexError(key)

    def __len__(self):
        return sum([item.quantity for item in self.items])

    def __repr__(self):
        if self.subtotal is None:
            return '<Cart %s %s>' % (self.cart_id, self.items)
        return '<Cart %s %s %.2f %s>' % (self.cart_id, self.items, 
            self.subtotal[0]/100.0, self.subtotal[1])

    def get_itemid_for_asin(self, asin):
        for item in self.items:
            if asin == item.asin:
                return item.item_id
        return None

    @staticmethod
    def from_xml(node):
        """
        Takes <Cart> node as ``lxml.objectify``d element and returns a Cart
        instance.
        """
        cart = Cart()
        cart.cart_id = node.CartId.pyval
        cart.hmac = node.HMAC.pyval
        try:
            for item_node in node.CartItems.CartItem:
                cart.items.append(Cart.Item.from_xml(item_node))
            cart.url = node.PurchaseURL.pyval
            cart.subtotal = (node.SubTotal.Amount, node.SubTotal.CurrencyCode)
        except AttributeError:
            cart.url = None
            cart.subtotal = None
        return cart

#: list of changeable and/or sensitive (thus ignorable) request arguments
IGNORABLE_ARGUMENTS = ('Signature', 'AWSAccessKeyId', 'Timestamp', 'AssociateTag')

def arguments_from_cached_xml(xml):
    """
    Extracts request arguments from cached response file. (Almost) any request
    sent to the API will be answered with an XML response containing the
    arguments originally used in XML elements ::
    
        <OperationRequest>
          <Arguments>
            <Argument Name="Service" Value="AWSECommerceService"/>
            <Argument Name="Signature" Value="XXXXXXXXXXXXXXX"/>
            <Argument Name="Operation" Value="BrowseNodeLookup"/>
            <Argument Name="BrowseNodeId" Value="927726"/>
            <Argument Name="AWSAccessKeyId" Value="XXXXXXXXXXXXXXX"/>
            <Argument Name="Timestamp" Value="2010-10-15T22:09:00Z"/>
            <Argument Name="Version" Value="2009-10-01"/>
          </Arguments>
        </OperationRequest>
    """
    root = objectify.fromstring(xml).getroottree().getroot()
    return dict((arg.get('Name'), arg.get('Value'))
                for arg in root.OperationRequest.Arguments.Argument
                if arg.get('Name') not in IGNORABLE_ARGUMENTS)

def arguments_from_url(url):
    """
    Extracts request arguments from URL.
    """
    params = parse_qs(urlparse(url).query)
    for key, val in params.items():
        # turn everything into unicode
        if type(val) == list:
            val = map(lambda x: unicode(x, encoding='utf-8'), val)
        # reduce lists to single value
        if type(val) == list and len(val) == 1:
            params[key] = val[0]
        if key in IGNORABLE_ARGUMENTS:
            del params[key]
    return params
