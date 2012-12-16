
.. _config:

Configuration
=============

.. versionadded:: 0.2.6

There is a growing list of configuration options for the library, many of which
can be passed directly to the API constructor at initialisation. Some options,
such as credentials, can also be read from environment variables (e.g.
``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``).

The order of precedence for is always:

* Parameters passed into Connection class constructor.
* Parameters specified by environment variables
* Parameters specified as options in the config file.

The following table gives an overview which values can be defined where:

=============  ======================  =====================
config file    boto config             environment variable
=============  ======================  =====================
access_key     aws_access_key_id       AWS_ACCESS_KEY_ID
secret_key     aws_secret_access_key   AWS_SECRET_ACCESS_KEY
associate_tag                          AWS_ASSOCIATE_TAG
locale                                 AWS_LOCALE
=============  ======================  =====================


Config files
------------

Upon initialisation, the API looks for configuration files (similar to the
`boto config`_, where I have borrowed the idea from) in the following
locations and in the following order:

* any `boto config`_ files ``/etc/boto.cfg`` and ``~/.boto``
* ``/etc/amazon-product-api.cfg`` for site-wide settings that all users on
  this machine will use
* ``~/.amazon-product-api`` for user-specific settings

The options are merged into a single, in-memory configuration that is available.
Files from this wrapper will always take precedence over boto config files!

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

.. _boto config: http://code.google.com/p/boto/wiki/BotoConfig


Environment variables
---------------------

You can also set the following environment variables:

``AWS_ACCESS_KEY_ID``
    Your AWS access key

``AWS_SECRET_ACCESS_KEY``
    Your AWS secret access key

``AWS_ASSOCIATE_TAG``
    Your AWS associate ID

``AWS_LOCALE``
    Your API locale


