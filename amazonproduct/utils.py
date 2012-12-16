from ConfigParser import SafeConfigParser
import os
import sys

REQUIRED_KEYS = [
    'access_key',
    'secret_key',
    'associate_tag',
    'locale',
]

BOTO_FILES = [
    '/etc/boto.cfg',
    '~/.boto',
]
CONFIG_FILES = [
    '/etc/amazon-product-api.cfg',
    '~/.amazon-product-api'
]


def load_boto_config():
    """
    Loads config dict from a boto config file [#]_ found in ``/etc/boto.cfg``
    or ``~/.boto``. A boto config file looks like this::

        [Credentials]
        aws_access_key_id = <your access key>
        aws_secret_access_key = <your secret key>

    Note that the only config section that will be used in ``Credentials``.

    .. _#: http://code.google.com/p/boto/wiki/BotoConfig
    """
    config = SafeConfigParser()
    config.read([os.path.expanduser(path) for path in BOTO_FILES])

    mapper = {
        'access_key': 'aws_access_key_id',
        'secret_key': 'aws_secret_access_key',
    }
    return dict(
        (key, config.get('Credentials', boto))
        for key, boto in mapper.items()
        if config.has_option('Credentials', boto)
    )


def load_file_config():
    """
    Loads dict from config files ``/etc/amazon-product-api.cfg`` or
    ``~/.amazon-product-api``. ::

        [Credentials]
        access_key = <your access key>
        secret_key = <your secret key>
        associate_tag = <your associate tag>
        locale = us

    """
    config = SafeConfigParser()
    config.read([os.path.expanduser(path) for path in CONFIG_FILES])

    if not config.has_section('Credentials'):
        return {}

    return dict(
        (key, val)
        for key, val in config.items('Credentials')
        if key in REQUIRED_KEYS
    )


def load_environment_config():
    """
    Loads config dict from environmental variables (if set):

    * AWS_ACCESS_KEY
    * AWS_SECRET_ACCESS_KEY
    * AWS_ASSOCIATE_TAG
    * AWS_LOCALE
    """
    mapper = {
        'access_key': 'AWS_ACCESS_KEY',
        'secret_key': 'AWS_SECRET_ACCESS_KEY',
        'associate_tag': 'AWS_ASSOCIATE_TAG',
        'locale': 'AWS_LOCALE',
    }
    return dict(
        (key, os.environ.get(val))
        for key, val in mapper.items()
        if os.environ.has_key(val)
    )


def load_config():
    """
    Returns a dict with API credentials which is loaded from (in this order):

    * Environment variables ``AWS_ACCESS_KEY``, ``AWS_SECRET_ACCESS_KEY``,
      ``AWS_ASSOCIATE_TAG`` and ``AWS_LOCALE``
    * Config files ``/etc/amazon-product-api.cfg`` or ``~/.amazon-product-api``
      where the latter may add or replace values of the former.
    * A boto config file [#]_ found in ``/etc/boto.cfg`` or ``~/.boto``.
    
    Whatever is found first counts.

    The returned dictionary may look like this::

        {
            'access_key': '<access key>',
            'secret_key': '<secret key>',
            'associate_tag': 'redtoad-10',
            'locale': 'uk'
        }
    
    .. _#: http://code.google.com/p/boto/wiki/BotoConfig
    """
    config = load_boto_config()
    config.update(load_file_config())
    config.update(load_environment_config())

    # substitute None for all values not found
    for key in REQUIRED_KEYS:
        if key not in config:
            config[key] = None

    return config


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

