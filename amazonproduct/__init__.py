
"""
Amazon Product Advertising API
==============================

    The Product Advertising API provides programmatic access to Amazon's
    product selection and discovery functionality so that developers like you
    can advertise Amazon products to monetize your website.

    The Product Advertising API helps you advertise Amazon products using
    product search and look up capability, product information and features
    such as Customer Reviews, Similar Products, Wish Lists and New and Used
    listings. You can make money using the Product Advertising API to advertise
    Amazon products in conjunction with the Amazon Associates program. Be sure
    to join the Amazon Associates program to earn up to 15% in referral fees
    when the users you refer to Amazon sites buy qualifying products.

More info can be found at
https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html

Requirements
------------

You need an Amazon Webservice account which comes with an access key and a
secret key.

If you don't customise the response processing, you'll also need the python
module lxml (>=2.1.5) and, if you're using python 2.4, also pycrypto.

License
-------

This program is release under the BSD License. You can find the full text of
the license in the LICENSE file accompanying the package.

"""

from amazonproduct.version import VERSION
from amazonproduct.api import *

__version__ = VERSION
