
"""
Find similar items to "Small Favor: A Novel of the Dresden Files"
(ASIN 0451462009).
"""

from config import AWS_KEY, SECRET_KEY
from amazonproduct import API, AWSError
from amazonproduct import ResultPaginator

from xml.dom.minidom import parse


def minidom_response_parser(fp):
    """
    Custom response parser using xml.dom.minidom.parse 
    instead of lxml.objectify.
    """
    root = parse(fp)
    
    # parse errors
    for error in root.getElementsByTagName('Error'):
        code = error.getElementsByTagName('Code')[0].firstChild.nodeValue
        msg = error.getElementsByTagName('Message')[0].firstChild.nodeValue
        raise AWSError(code, msg)
    
    return root

if __name__ == '__main__':
    
    api = API(AWS_KEY, SECRET_KEY, 'us',
              processor=minidom_response_parser)
    root = api.item_lookup('0718155157')
    
    print root.toprettyxml()
    
    # ...
    # now do something with it! 
    
    