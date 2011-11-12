
Developer FAQ
=============

Here is a growing collection of questions that pop up regularly.
 
Which locale should I use and why is this important?
----------------------------------------------------

Amazon is a world-wide venture. Product Advertising API is as well.
Product Advertising API operates in six locales:

* CA (Canada)
* CN (China)
* DE (Germany)
* ES (Spain)
* FR (France)
* IT (Italy)
* JP (Japan)
* UK (United Kingdom)
* US (United States of Amerika)

Each of these locales is serviced by an Amazon web site that uses the local
language, local customs, and local formatting. For example, when you look at
the DE homepage for Amazon, you see the listings in German. If you purchased an
item, you would find the price in Euros, and, if you were to purchase a movie,
you would find that the movie rating would conform to the movie rating system
used in Germany. 

Product Advertising API responses contain the same localized information. The
correct locale is determined by examining the endpoint in the request.


Can I use this wrapper on Google App Engine (GAE)?
--------------------------------------------------

This wrapper relies by default on `lxml.objectify`_ to parse the returned XML
responses from Amazon which is built with libxml, a C library. `And this will
not work on GAE`_.

For the time being there is no solution that will work out of the box.
You can, however, use a different XML parser (see :ref:`custom-xml-parser`)!

.. _lxml.objectify: http://codespeak.net/lxml/objectify.html
.. _And this will not work on GAE: http://code.google.com/p/googleappengine/issues/detail?id=18


I keep getting ``InvalidParameterValue`` errors. What am I doing wrong?
-----------------------------------------------------------------------

The Amazon webservice returns an ``InvalidParameterValue`` error if you enter a
*wrong* ISBN. Wrong, as it seems, can mean the format is wrong (too short) or 
contains invalid characters (e.g. dashes "-"). 

Surprisingly, wrong can even mean that you used the *wrong locale*! For 
instance, you cannot retrieve data for an English book (ISBN 9780596158064) 
from locale ``de`` or for a German book (ISBN 9783836214063) from locale 
``us`` - but using locale ``uk`` works for both!

Try your query again using a valid ISBN and play around with the locale. You 
can set the locale at initialisation::

    from amazonproduct import API
    AWS_KEY = '...'
    SECRET_KEY = '...'
    api = API(AWS_KEY, SECRET_KEY, "uk")
    root = api.item_lookup('9783836214063', IdType='ISBN', SearchIndex='Books')


Why yet another implementation?
-------------------------------

.. index:: pyaws, pyamazon, boto, pyecs, bottlenose

There are a number of alternatives available:

- `PyAmazon <http://www.josephson.org/projects/pyamazon/>`_, originally written
  by Mark Pilgrim, then taken over by Michael Josephson. Development seems to
  have stalled, with the last release in August 2004.
  
- Kung Xi's `pyaws <http://pyaws.sf.net>`_ forked pyamazon to support the then
  most recent Amazon Web Service and give developers more control of the 
  incoming data. Sometime after version 0.2.0, development over at sourceforge
  was dropped without warning and continued at http://trac2.assembla.com/pyaws
  with version 0.3.0, which was released in May 2008.
   
  This module seems to be the most widely used. It hasn't been updated however
  in quite some time. A fork of this project is maintained 
  `here <http://bitbucket.org/johnpaulett/pyaws>`_.

- In October 2008 David Jane started `pyecs <http://code.google.com/p/pyecs/>`_
  after stumbling accross pyamazon. He decided that "a new, more class and
  iterator-oriented approach would be better." However, it only supports a
  subset. Last commit was in November 2008. 
  
- There is a `clever hack <http://jjinux.blogspot.com/2009/06/python-amazon-product-advertising-api.html>`_
  using `boto <http://code.google.com/p/boto/>`_ to create the URL, although
  this library is originally designed to allow communication with Amazon's 
  cloud APIs.

So why write your own then? First and foremost, since August 15, 2009 all calls
to Amazon's Product Advertising API must be authenticated using request 
signatures. The afore mentioned libraries did not support this out of the box at
the time. And yes... writing something from scratch is always more appealing.

More recently I stumbled across another alternative:

- Dan Loewenherz's `bottlenose <http://pypi.python.org/pypi/bottlenose>`_ makes 
  sending requests to Amazon as easy as ::
    
    import bottlenose
    amazon = bottlenose.Amazon("access_key_id", "secret_access_key")
    response = amazon.ItemSearch(ItemId="0596520999", ResponseGroup="Images", 
        SearchIndex="Books", IdType="ISBN")
    
  It has a straight-forward API, is easy to use and supports all operations out
  of the box. You only have to take care of processing the response. I must 
  steal some ideas from this module!


I found a bug! What do I do now?
--------------------------------

You can do two things:

1. File a bug report (but please look at the `list of know issues`_ before)
2. Send an e-mail to the `mailing list`_.

*Any* feedback is welcome!

.. _list of know issues: http://bitbucket.org/basti/python-amazon-product-api/issues/
.. _mailing list: http://groups.google.com/group/python-amazon-product-api-devel

