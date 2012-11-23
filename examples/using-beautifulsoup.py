
"""
Find similar items to "Small Favor: A Novel of the Dresden Files"
(ASIN 0451462009).
"""

from amazonproduct.api import API
from amazonproduct.errors import AWSError
from amazonproduct.processors import BaseProcessor

import BeautifulSoup


class SoupProcessor (BaseProcessor):

    """
    Custom response parser using BeautifulSoup to parse the returned XML.
    """

    def parse(self, fp):

        soup = BeautifulSoup.BeautifulSoup(fp.read())

        # parse errors
        for error in soup.findAll('error'):
            code = error.find('code').text
            msg = error.find('message').text
            raise AWSError(code, msg)

        return soup

if __name__ == '__main__':

    # Don't forget to create file ~/.amazon-product-api
    # with your credentials (see docs for details)
    api = API(locale='us', processor=SoupProcessor())
    result = api.item_lookup('0718155157')
    
    print result
    
    # ...
    # now do something with it! 
    
    
