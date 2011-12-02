
from lxml import etree, objectify

from amazonproduct.errors import AWSError
from amazonproduct.processors import BaseResultPaginator


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
    def load_paginator(cls, counter):
        return {
            'ItemPage': SearchPaginator,
        }[counter]


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
