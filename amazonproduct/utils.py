from ConfigParser import SafeConfigParser
import os
import re
import sys

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

def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    Taken from Django's importlib module
    https://code.djangoproject.com/browser/django/trunk/django/utils/importlib.py
    """
    def _resolve_name(name, package, level):
        """Return the absolute name of the module to be imported."""
        if not hasattr(package, 'rindex'):
            raise ValueError("'package' not set to a string")
        dot = len(package)
        for x in xrange(level, 1, -1):
            try:
                dot = package.rindex('.', 0, dot)
            except ValueError:
                raise ValueError("attempted relative import beyond top-level "
                                  "package")
        return "%s.%s" % (package[:dot], name)

    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]

def running_on_gae():
    """
    Is this module running on Google App Engine (GAE)?
    """
    return 'Google' in os.environ.get('SERVER_SOFTWARE', '')

