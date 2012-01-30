import xml.dom.minidom

from amazonproduct.errors import AWSError
from amazonproduct.processors import BaseProcessor

class Processor(BaseProcessor):

    """
    Alternative result parser using ``xml.dom.minidom` from the standard
    library.
    """

    def parse(self, fp):
        root = xml.dom.minidom.parse(fp)
        # parse errors
        for error in root.getElementsByTagName('Error'):
            code = error.getElementsByTagName('Code')[0].firstChild.nodeValue
            msg = error.getElementsByTagName('Message')[0].firstChild.nodeValue
            raise AWSError(code, msg)
        return root

