import re

from amazonproduct.errors import AWSError
from amazonproduct.processors import BaseResultPaginator, BaseProcessor
from amazonproduct.utils import import_module


implementations = [
    'lxml.etree',
    'xml.etree.cElementTree',
    'xml.etree.ElementTree',
    'cElementTree',
    'elementtree.ElementTree',
]

def load_elementtree_module(*modules):
    """
    Returns the first importable ElementTree implementation from a list of
    modules. If ``modules`` is omitted :data:`implementations` is used.
    """
    if not modules:
        modules = implementations
    for mod in modules:
        try:
            return import_module(mod)
        except ImportError:
            pass
    raise ImportError(
        "Couldn't find any of the ElementTree implementations in %s!" % (
            list(modules), ))

etree = load_elementtree_module()


_nsreg = re.compile('^({.+?})')
def extract_nspace(element):
    """
    Extracts namespace from XML element. If no namespace is found, ``''``
    (empty string) is returned.
    """
    m = _nsreg.search(element.tag)
    if m: return m.group(1)
    return ''


class Processor (BaseProcessor):

    def parse(self, fp):
        root = etree.parse(fp).getroot()
        ns = extract_nspace(root)
        errors = root.findall('.//%sError' % ns)
        for error in errors:
            code = error.findtext('./%sCode' % ns)
            msg = error.findtext('./%sMessage' % ns)
            raise AWSError(code, msg)
        return root

    def __repr__(self):
        return '<%s using %s at %s>' % (
            self.__class__.__name__, etree.__name__, hex(id(self)))

    @classmethod
    def load_paginator(cls, type_):
        return {
            'ItemPage': ItemPaginator,
        }[type_]


class XPathPaginator (BaseResultPaginator):

    """
    Result paginator using XPath expressions to extract page and result
    information from XML.
    """

    counter = current_page_xpath = total_pages_xpath = total_results_xpath = None

    def extract_data(self, root):
        nspace = extract_nspace(root)
        def fetch_value(xpath, default):
            try:
                path = xpath.replace('{}', nspace)
                node = root.findtext(path)
                return int(node)
            except (IndexError, TypeError):
                return default
        return map(lambda a: fetch_value(*a), [
            (self.current_page_xpath, 1),
            (self.total_pages_xpath, 0),
            (self.total_results_xpath, 0)
        ])


class ItemPaginator (XPathPaginator):

    counter = 'ItemPage'
    current_page_xpath = './/{}Items/{}Request/{}ItemSearchRequest/{}ItemPage'
    total_pages_xpath = './/{}Items/{}TotalPages'
    total_results_xpath = './/{}Items/{}TotalResults'

