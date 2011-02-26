
Use your own XML parsing library
--------------------------------

Since version 0.2.3 you no longer need to use ``lxml.objectify``. A custom
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
    api = API(AWS_KEY, SECRET_KEY, processor=minidom_response_parser)
    root = api.item_lookup('0718155157')
    print root.toprettyxml()
    # ...

.. note:: 
   Make sure your response parser raises an ``AWSError`` with the appropriate
   error code and message.

