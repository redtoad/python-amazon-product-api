# Copyright (C) 2009-2013 Sebastian Rahlf <basti at redtoad dot de>
#
# This program is release under the BSD License. You can find the full text of
# the license in the LICENSE file.

from lxml import etree

from amazonproduct.contrib.cart import Cart, Item
from amazonproduct.errors import AWSError
from amazonproduct.processors import BaseResultPaginator, BaseProcessor
from amazonproduct.processors import ITEMS_PAGINATOR, RELATEDITEMS_PAGINATOR


class XPathPaginator (BaseResultPaginator):

    """
    Result paginator using XPath expressions to extract page and result
    information from XML.
    """

    counter = current_page_xpath = total_pages_xpath = total_results_xpath = None

    def paginator_data(self, root):
        nspace = root.nsmap.get(None, '')
        def fetch_value(xpath, default):
            try:
                import lxml.etree; print lxml.etree.tostring(root, pretty_print=True)
                node = root.xpath(xpath, namespaces={'aws': nspace})[0]
                return int(node.text)
            except AttributeError:
                return int(root)
            except IndexError:
                return default
        return map(lambda a: fetch_value(*a), [
            (self.current_page_xpath, 1),
            (self.total_pages_xpath, 0),
            (self.total_results_xpath, 0)
        ])

    def iterate(self, root):
        nspace = root.nsmap.get(None, '')
        return root.xpath(self.items, namespaces={'aws': nspace})


class SearchPaginator (XPathPaginator):

    counter = 'ItemPage'
    current_page_xpath = '//aws:Items/aws:Request/aws:ItemSearchRequest/aws:ItemPage'
    total_pages_xpath = '//aws:Items/aws:TotalPages'
    total_results_xpath = '//aws:Items/aws:TotalResults'
    items = '//aws:Items/aws:Item'


class RelatedItemsPaginator (XPathPaginator):

    counter = 'RelatedItemPage'
    current_page_xpath = '//aws:RelatedItemPage'
    total_pages_xpath = '//aws:RelatedItems/aws:RelatedItemPageCount'
    total_results_xpath = '//aws:RelatedItems/aws:RelatedItemCount'
    items = '//aws:RelatedItems/aws:RelatedItem/aws:Item'


class Processor (BaseProcessor):

    """
    Result processor using lxml.etree.
    """

    paginators = {
        ITEMS_PAGINATOR: SearchPaginator,
        RELATEDITEMS_PAGINATOR: RelatedItemsPaginator,
    }

    def parse(self, fp):
        root = etree.parse(fp).getroot()
        nspace = {'aws': root.nsmap.get(None, '')}
        errors = root.xpath('//aws:Error', namespaces=nspace)
        for error in errors:
            raise AWSError(
                code=error.findtext('./aws:Code', namespaces=nspace),
                msg=error.findtext('./aws:Message', namespaces=nspace),
                xml=root)
        return root

    def __repr__(self):  # pragma: no cover
        return '<%s using %s at %s>' % (
            self.__class__.__name__, getattr(self.etree, '__name__', '???'), hex(id(self)))

    @classmethod
    def parse_cart(cls, node):
        """
        Returns an instance of :class:`amazonproduct.contrib.Cart` based on
        information extracted from ``node``.
        """
        nspace = {'aws': node.nsmap.get(None, '')}
        root = node.find('.//aws:Cart', namespaces=nspace)
        _extract = lambda node, xpath: node.findtext(xpath, namespaces=nspace)

        cart = Cart()
        cart.cart_id = _extract(root, './aws:CartId')
        cart.hmac = _extract(root, './aws:HMAC')
        cart.url = _extract(root, './aws:PurchaseURL')

        def parse_item(item_node):
            item = Item()
            item.item_id = _extract(item_node, './aws:CartItemId')
            item.asin = _extract(item_node, './aws:ASIN')
            item.seller = _extract(item_node, './aws:SellerNickname')
            item.quantity = int(_extract(item_node, './aws:Quantity'))
            item.title = _extract(item_node, './aws:Title')
            item.product_group = _extract(item_node, './aws:ProductGroup')
            item.price = (
                int(_extract(item_node, './aws:Price/aws:Amount')),
                _extract(item_node, './aws:Price/aws:CurrencyCode'))
            item.total = (
                int(_extract(item_node, './aws:ItemTotal/aws:Amount')),
                _extract(item_node, './aws:ItemTotal/aws:CurrencyCode'))
            return item

        try:
            for item_node in root.findall('./aws:CartItems/aws:CartItem', namespaces=nspace):
                cart.items.append(parse_item(item_node))
            cart.subtotal = (node.SubTotal.Amount, node.SubTotal.CurrencyCode)
        except AttributeError:
            cart.subtotal = (None, None)
        return cart

