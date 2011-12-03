
from lxml import etree, objectify

from amazonproduct.contrib.cart import Cart, Item
from amazonproduct.errors import AWSError
from amazonproduct.processors import BaseResultPaginator, BaseProcessor
from amazonproduct.processors import ITEMS_PAGINATOR, TAGS_PAGINATOR


class SelectiveClassLookup(etree.CustomElementClassLookup):
    """
    Lookup mechanism for XML elements to ensure that ItemIds (like
    ASINs) are always StringElements and evaluated as such.

    Thanks to Brian Browning for pointing this out.
    """
    # pylint: disable-msg=W0613
    def lookup(self, node_type, document, namespace, name):
        if name in ('ItemId', 'ASIN'):
            return objectify.StringElement


class Processor (BaseProcessor):

    """
    Response processor using ``lxml.objectify``. It uses a custom lookup
    mechanism for XML elements to ensure that ItemIds (such as ASINs) are
    always StringElements and evaluated as such.

    ..warning:: This processors does not run on Google App Engine!
      http://code.google.com/p/googleappengine/issues/detail?id=18
    """

    # pylint: disable-msg=R0903

    def __init__(self):
        self._parser = etree.XMLParser()
        lookup = SelectiveClassLookup()
        lookup.set_fallback(objectify.ObjectifyElementClassLookup())
        self._parser.set_element_class_lookup(lookup)

    def parse(self, fp):
        """
        Parses a file-like object containing the Amazon XML response.
        """
        tree = objectify.parse(fp, self._parser)
        root = tree.getroot()

        #~ from lxml import etree
        #~ print etree.tostring(tree, pretty_print=True)

        try:
            nspace = root.nsmap[None]
            errors = root.xpath('//aws:Error', namespaces={'aws' : nspace})
        except KeyError:
            errors = root.xpath('//Error')

        for error in errors:
            code = error.Code.text
            msg = error.Message.text
            raise AWSError(code, msg)

        return root

    @classmethod
    def parse_cart(cls, node):
        """
        Returns an instance of :class:`amazonproduct.contrib.Cart` based on
        information extracted from ``node``.
        """
        cart = Cart()
        # TODO This is probably not the safest way to get <Cart>
        root = node.Cart
        cart.cart_id = root.CartId.pyval
        cart.hmac = root.HMAC.pyval

        def parse_item(item_node):
            item = Item()
            item.item_id = item_node.CartItemId.pyval
            item.asin = item_node.ASIN.pyval
            item.seller = item_node.SellerNickname.pyval
            item.quantity = item_node.Quantity.pyval
            item.title = item_node.Title.pyval
            item.product_group = item_node.ProductGroup.pyval
            item.price = (
                item_node.Price.Amount.pyval,
                item_node.Price.CurrencyCode.pyval)
            item.total = (
                item_node.ItemTotal.Amount.pyval,
                item_node.ItemTotal.CurrencyCode.pyval)
            return item

        try:
            for item_node in root.CartItems.CartItem:
                cart.items.append(parse_item(item_node))
            cart.url = root.PurchaseURL.pyval
            cart.subtotal = (root.SubTotal.Amount, root.SubTotal.CurrencyCode)
        except AttributeError:
            cart.url = None
            cart.subtotal = None
        return cart

    @classmethod
    def load_paginator(cls, paginator_type):
        try:
            return {
                ITEMS_PAGINATOR: SearchPaginator,
                TAGS_PAGINATOR: TagPaginator,
            }[paginator_type]
        except KeyError:
            return None


class Paginator (BaseResultPaginator):

    """
    Result paginator using lxml and XPath expressions to extract page and
    result information from XML.
    """

    def extract_data(self, root):
        nspace = root.nsmap.get(None, '')
        def fetch_value(xpath, default):
            try:
                return root.xpath(xpath, namespaces={'aws' : nspace})[0]
            except AttributeError:
                # node has no attribute pyval so it better be a number
                return int(node)
            except IndexError:
                return default
        return map(lambda a: fetch_value(*a), [
            (self.current_page_xpath, 1),
            (self.total_pages_xpath, 0),
            (self.total_results_xpath, 0)
        ])


class SearchPaginator (Paginator):

    counter = 'ItemPage'
    current_page_xpath = '//aws:Items/aws:Request/aws:ItemSearchRequest/aws:ItemPage'
    total_pages_xpath = '//aws:Items/aws:TotalPages'
    total_results_xpath = '//aws:Items/aws:TotalResults'
