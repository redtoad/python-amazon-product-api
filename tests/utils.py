import re

def convert_camel_case(operation):
    """
    Converts ``CamelCaseOperationName`` into ``python_style_method_name``.
    """
    return re.sub('([a-z])([A-Z])', r'\1_\2', operation).lower()


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
