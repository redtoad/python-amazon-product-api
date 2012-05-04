
.. _parsers:

Result processing
=================

By default this module uses `lxml.objectify`_ to parse all XML responses it receives from Amazon.
However, this will only work if ``lxml`` is actually installed.

On some systems like Google App Engine lxml cannot be installed. Therefore there are a number of fallbacks which will be tried in the following order:

* :class:`amazonproduct.processors.objectify.Processor`
* :class:`amazonproduct.processors.etree.Processor`

There is also a processor using ``minidom``.

* :class:`amazonproduct.processors.minidom.Processor`


.. note:: If you want to use your own parser have a look at :class:`amazonproduct.processors.BaseProcessor` and :class:`amazonproduct.processors.BaseResultPaginator`


.. _lxml.objectify: http://lxml.de/objectify.html
