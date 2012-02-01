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
        for er in root.getElementsByTagName('Error'):
            raise AWSError(
                code=er.getElementsByTagName('Code')[0].firstChild.nodeValue,
                msg=er.getElementsByTagName('Message')[0].firstChild.nodeValue,
                xml=root)
        return root

