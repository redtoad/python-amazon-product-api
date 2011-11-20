
from lxml import etree, objectify

from amazonproduct.errors import AWSError
from amazonproduct.paginators import LxmlItemSearchPaginator


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


class Processor (object):

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

    def __call__(self, fp):
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

    item_search_paginator = LxmlItemSearchPaginator
