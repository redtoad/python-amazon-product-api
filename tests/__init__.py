
import imp
import os.path

from amazonproduct import HOSTS
from amazonproduct.processors import objectify, etree, minidom
from amazonproduct.utils import load_config

_here = os.path.abspath(os.path.dirname(__file__))


try:
    fp, path, desc = imp.find_module('config', [_here])
    _config = imp.load_module('config', fp, _here, desc)
except ImportError:
    _config = None

#: Directory containing XML responses for API versions (one directory for each
#: API version)
XML_TEST_DIR = _here

#: Versions of Amazon API to be tested against 
TESTABLE_API_VERSIONS = [
    '2011-08-01',
    '2010-12-01', '2010-11-01', '2010-10-01', '2010-09-01', '2010-06-01', 
    '2009-11-01', '2009-10-01'
]

#: Locales to test against. 
TESTABLE_LOCALES = HOSTS.keys()

ELEMENTTREE_IMPLEMENTATIONS = [
    'lxml.etree',
    'xml.etree.cElementTree',
    'xml.etree.ElementTree',
    'cElementTree',
    'elementtree.ElementTree',
    'elementtree.ElementTree'
]

#: Result processors to test with.
TESTABLE_PROCESSORS = {
    'objectify': objectify.Processor,
    #    'minidom': minidom.Processor,
}
# add ElementTree implementations
for mod in ELEMENTTREE_IMPLEMENTATIONS:
    TESTABLE_PROCESSORS[mod] = etree.Processor(module=mod)

def get_config_value(key, default=None):
    """
    Loads value from config.py or from environment variable or return default
    (in that order).
    """
    try:
        return getattr(_config, key)
    except AttributeError:
        return os.environ.get(key, default)

_config = load_config()
AWS_KEY = _config.get('access_key', '')
SECRET_KEY = _config.get('secret_key', '')
