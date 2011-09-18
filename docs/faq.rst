
Developer FAQ
=============

Here is a growing collection of questions that pop up regularly.
 
Which locale should I use and why is this important?
----------------------------------------------------

Amazon is a world-wide venture. Product Advertising API is as well. 
Product Advertising API operates in six locales:

* CA
* DE
* FR
* JP
* UK
* US

Each of these locales is serviced by an Amazon web site that uses the local 
language, local customs, and local formatting. For example, when you look at 
the DE homepage for Amazon, you see the listings in German. If you purchased an 
item, you would find the price in Euros, and, if you were to purchase a movie, 
you would find that the movie rating would conform to the movie rating system 
used in Germany. 

Product Advertising API responses contain the same localized information. 
Product Advertising API determines the correct locale by examining the endpoint 
in the request.


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


I found a bug! What do I do now?
--------------------------------

You can do two things:

1. File a bug report (but please look at the `list of know issues`_ before)
2. Send an e-mail to the `mailing list`_.

*Any* feedback is welcome!

.. _list of know issues: http://bitbucket.org/basti/python-amazon-product-api/issues/
.. _mailing list: http://groups.google.com/group/python-amazon-product-api-devel