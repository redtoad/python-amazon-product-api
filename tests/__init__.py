
import imp
import os.path

from amazonproduct import HOSTS
from amazonproduct.utils import load_config

#: Directory containing XML responses for API versions (one directory for each
#: API version)
XML_TEST_DIR = os.path.abspath(os.path.dirname(__file__))

#: Versions of Amazon API to be tested against 
TESTABLE_API_VERSIONS = [
    '2011-08-01',
    '2010-12-01', '2010-11-01', '2010-10-01', '2010-09-01', '2010-06-01', 
    '2009-11-01', '2009-10-01'
]

#: Locales to test against. 
TESTABLE_LOCALES = HOSTS.keys()

_config = load_config()
AWS_KEY = _config.get('access_key', '')
SECRET_KEY = _config.get('secret_key', '')
