
.. _config:

Configuration
=============

.. versionadded:: 0.2.6

There is a growing list of configuration options for the library, many of which
can be passed directly to the API constructor at initialisation. Some options,
such as credentials, can also be read from environment variables (e.g.
``AWS_ACCESS_KEY`` and ``AWS_SECRET_ACCESS_KEY``).


Using files
-----------

To use a config file, pass its path to the API::

    import amazonproduct
    api = amazonproduct.API(cfg='~/my-config-file')

If no path was specified, the API looks for configuration files in the following
locations and in the following order:

* ``/etc/amazon-product-api.cfg`` for site-wide settings that all users on
  this machine will use
* ``~/.amazon-product-api`` for user-specific settings

The options are merged into a single, in-memory configuration that is available.

The following sections and options are currently recognized within the config
file.

``Credentials``
    The Credentials section is used to specify the AWS credentials used for
    all requests.


    ``access_key``
        Your AWS access key

    ``secret_key``
        Your AWS secret access key

    ``associate_tag``
        Your AWS associate ID

    Example::

        [Credentials]
        access_key = <your access key>
        secret_key = <your secret key>
        associate_tag = <your associate id>

    .. note:: Stating the obvious: Your access key is *not* ``<your access
       key>`` but something like ``10RZZJBK6YBQASX213G2``.


Using config dict
-----------------

If you need to configure the API at runtime you can also pass the config values
as dict::

    import amazonproduct
    config = {
        'access_key': 'ABCDEFG1234X',
        'secret_key': 'Ydjkei78HdkffdklieAHDJWE3134',
        'associate_tag': 'redtoad-10',
        'locale': 'us'
    }
    api = amazonproduct.API(cfg=config)


Environment variables
---------------------

You can also set the following environment variables:

``AWS_ACCESS_KEY``
    Your AWS access key

``AWS_SECRET_ACCESS_KEY``
    Your AWS secret access key

``AWS_ASSOCIATE_TAG``
    Your AWS associate ID

``AWS_LOCALE``
    Your API locale

.. important:: Environment variables will always take precedence over values
   from config files *but not from config dict*!


Order of precedence
-------------------

* Parameters specified by environment variables
* User-specific parameters from ``~/.amazon-product-api``

The following table gives an overview which values can be defined where:

=============  =====================
config file    environment variable
=============  =====================
access_key     AWS_ACCESS_KEY
secret_key     AWS_SECRET_ACCESS_KEY
associate_tag  AWS_ASSOCIATE_TAG
locale         AWS_LOCALE
=============  =====================

