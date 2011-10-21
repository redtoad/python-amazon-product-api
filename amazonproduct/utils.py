from ConfigParser import SafeConfigParser
import os
import re

CREDENTIALS = 'Credentials'
CONFIG_FILES = [
    '/etc/boto.cfg', 
    '~/.boto',
    '/etc/amazon-product-api.cfg',
    '~/.amazon-product-api',
]

def load_config():
    """
    Returns a dict with ``AWS_KEY``, ``SECRET_KEY`` and ``ASSOCIATE_TAG`` which
    is loaded from (in thsi order):
    
    * a ``config.py`` file in this directory
    * a boto-like config file [#]_ found in ``/etc/boto.cfg``, ``~/.boto``,
      ``/etc/amazon-product-api.cfg`` or ``~/.amazon-product-api``.
    
    Whatever is found first counts.
    
    .. _#: http://code.google.com/p/boto/wiki/BotoConfig
    """
    config = SafeConfigParser()
    config.read([os.path.expanduser(path) for path in CONFIG_FILES])

    # maps boto config -> amazonproduct key
    mapper = {
        'aws_access_key_id': 'access_key',
        'aws_secret_access_key': 'secret_key',
        'aws_associate_tag': 'associate_tag',
        'aws_product_locale': 'locale'
    }
    options = {}
    for boto, key in mapper.items():
        if config.has_option(CREDENTIALS, boto): 
            options[key] = config.get(CREDENTIALS, boto)

    # substitute None for all values not found
    for key in mapper.values():
        if key not in options:
            options[key] = None
    return options
