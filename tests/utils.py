
from lxml import etree, objectify
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
        @staticmethod
        def from_xml(node):
            """
            Takes <CartItem> node as ``lxml.objectify``d element and returns a 
            CartItem instance.
            """
            item = Cart.Item()
            item.item_id = node.CartItemId.pyval
            item.asin = node.ASIN.pyval
            item.merchant_id = node.MerchantId.pyval
            item.seller = (
                node.SellerId.pyval, 
                node.SellerNickname.pyval)
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
            print item.item_id, item.asin
            if key in (item.asin, item.item_id):
                return item
        raise IndexError(key)

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
