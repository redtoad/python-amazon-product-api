

try:
    import lxml.objectify
except ImportError:
    import warnings
    warnings.warn("Could not import lxml! Please make sure that you have "
                  "installed lxml!")

from .core import CoreAPI
from .operations import Operation

__all__ = [
    'init',
    'ItemLookup', 'ItemSearch',
    'SimilarityLookup', 'BrowseNodeLookup',
    'CartAdd', 'CartModify', 'CartGet', 'CartClear'
]

_api_singleton = None


class API(CoreAPI):

    def _fetch(self, url):
        resp = CoreAPI._fetch(self, url)
        return lxml.objectify.fromstring(resp.content)


def init(access_key, secret_key, locale, associate_tag):
    """
    Initialise global API instance.

    :param access_key:
    :param secret_key:
    :param locale:
    :param associate_tag:
    :return:
    """
    global _api_singleton
    _api_singleton = API(access_key, secret_key, locale, associate_tag)


def _call_operation(name, **kwargs):
    op = Operation(name, **kwargs)
    if _api_singleton is None:
        raise ValueError("Only works with global API instance!")
    return _api_singleton(Operation=op.name, **op.parameters)


def _operation(name):
    def decorated(**kwargs):
        return _call_operation(name, **kwargs)
    return decorated


ItemLookup = _operation("ItemLookup")
ItemSearch = _operation("ItemSearch")
SimilarityLookup = _operation("SimilarityLookup")
BrowseNodeLookup = _operation("BrowseNodeLookup")
CartAdd = _operation("CartAdd")
CartModify = _operation("CartModify")
CartGet = _operation("CartGet")
CartClear = _operation("CartClear")
