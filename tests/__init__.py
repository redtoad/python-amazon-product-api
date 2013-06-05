
import imp
import os
import re

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
    d for d in os.listdir(_here) 
    if re.match(r'^\d{4}-\d{2}-\d{2}$', d)
]

#: Locales to test against. 
TESTABLE_LOCALES = HOSTS.keys()

#ELEMENTTREE_IMPLEMENTATIONS = [
#    'lxml.etree',
#    'xml.etree.cElementTree',
#    'xml.etree.ElementTree',
#    'cElementTree',
#    'elementtree.ElementTree',
#    'elementtree.ElementTree'
#]

#: Result processors to test with.
TESTABLE_PROCESSORS = {
    'objectify': 'amazonproduct.processors.objectify',
    'etree': 'amazonproduct.processors.etree',
    'elementtree': 'amazonproduct.processors.elementtree',
#    'minidom': 'amazonproduct.processors.minidom',
}

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
