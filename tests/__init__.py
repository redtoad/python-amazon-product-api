
from amazonproduct import HOSTS

import os.path
_here = os.path.abspath(os.path.dirname(__file__))

#: Directory containing XML responses for API versions (one directory for each
#: API version)
XML_TEST_DIR = _here

#: Versions of Amazon API to be tested against 
TESTABLE_API_VERSIONS = [
'2010-12-01', '2010-11-01', '2010-10-01', '2010-09-01', '2010-06-01', 
'2009-11-01', '2009-10-01'
]

#: Locales to test against. 
TESTABLE_LOCALES = HOSTS.keys()

def get_config_value(key, default=None):
    """
    Loads value from config.py or from environment variable or return default
    (in that order).
    """
    try:
        config = __import__('config')
        return getattr(config, key)
    except (ImportError, AttributeError):
        return os.environ.get(key, default)

AWS_KEY = get_config_value('AWS_KEY', '')
SECRET_KEY = get_config_value('SECRET_KEY', '')
OVERWRITE_TESTS = get_config_value('OVERWRITE_TESTS', '')
