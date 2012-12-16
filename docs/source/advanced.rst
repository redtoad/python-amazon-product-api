
More advanced uses
==================

.. _adjusting-api-version:

Using a different API version
-----------------------------

Amazon releases a new API version every once in a while in order to add or
change features and operations. Usually, you won't have to worry about this
because with each release of this wrapper the latest API version will be used
by default.

If you do want to change the API version used, however, you can simply specify
which one you like::

    api = API(...)
    api.VERSION = '2010-10-01'

.. warning:: As of Feb 21st, 2012 all API versions prior to 2011-08-01 will
   no longer be supported!


.. _custom-xml-parser:

Use your own XML parsing library
--------------------------------

.. versionadded:: 0.2.3

You don't need to use ``lxml.objectify``. A custom
response processor can be defined using any mechanism you like. For instance,
here is one using ``xml.minidom``::
    
    import xml.dom.minidom
    def minidom_response_parser(fp):
        root = xml.dom.minidom.parse(fp)
        # parse errors
        for error in root.getElementsByTagName('Error'):
            code = error.getElementsByTagName('Code')[0].firstChild.nodeValue
            msg = error.getElementsByTagName('Message')[0].firstChild.nodeValue
                raise AWSError(code, msg)
            return root
    
    # Now let's use this instead of the default one
    api = API(AWS_KEY, SECRET_KEY, 'uk', processor=minidom_response_parser)
    root = api.item_lookup('0718155157')
    print root.toprettyxml()
    # ...

.. note:: 
   Make sure your response parser raises an ``AWSError`` with the appropriate
   error code and message.


Using batch operations
----------------------


Caching responses
-----------------

.. versionadded:: 0.2.5

Sometimes when developing or when it is foreseeable that the very same request
will be sent over and over again, it might be better to cache API responses from
Amazon for a short time in order to avoi going over you request limit.

