
from lxml import objectify
import re

# support Python 2 and Python 3 without conversion
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:  # pragma: no cover
    from urlparse import urlparse, parse_qs


def convert_camel_case(operation):
    """
    Converts ``CamelCaseOperationName`` into ``python_style_method_name``.
    """
    return re.sub('([a-z])([A-Z])', r'\1_\2', operation).lower()


def extract_operations_from_wsdl(path):
    """
    Extracts operations from Amazon's WSDL file.
    """
    root = objectify.parse(open(path)).getroot()
    wsdlns = 'http://schemas.xmlsoap.org/wsdl/'
    return set(root.xpath('//ws:operation/@name', namespaces={'ws' : wsdlns}))


#: list of changeable and/or sensitive (thus ignorable) request arguments
IGNORABLE_ARGUMENTS = ('Signature', 'AWSAccessKeyId', 'Timestamp', 'AssociateTag')

def arguments_from_cached_xml(xml):
    """
    Extracts request arguments from cached response file. (Almost) any request
    sent to the API will be answered with an XML response containing the
    arguments originally used in XML elements ::
    
        <OperationRequest>
          <Arguments>
            <Argument Name="Service" Value="AWSECommerceService"/>
            <Argument Name="Signature" Value="XXXXXXXXXXXXXXX"/>
            <Argument Name="Operation" Value="BrowseNodeLookup"/>
            <Argument Name="BrowseNodeId" Value="927726"/>
            <Argument Name="AWSAccessKeyId" Value="XXXXXXXXXXXXXXX"/>
            <Argument Name="Timestamp" Value="2010-10-15T22:09:00Z"/>
            <Argument Name="Version" Value="2009-10-01"/>
          </Arguments>
        </OperationRequest>
    """
    root = objectify.fromstring(xml).getroottree().getroot()
    return dict((arg.get('Name'), arg.get('Value'))
                for arg in root.OperationRequest.Arguments.Argument
                if arg.get('Name') not in IGNORABLE_ARGUMENTS)


def arguments_from_url(url):
    """
    Extracts request arguments from URL.
    """
    params = parse_qs(urlparse(url).query)
    for key in list(params):

        if key in IGNORABLE_ARGUMENTS:
            del params[key]
            continue

        val = params[key]
        # turn everything into unicode
        if type(val) == list:
            val = list(map(lambda x: x.decode(encoding='utf-8'), val))
        # reduce lists to single value
        if type(val) == list and len(val) == 1:
            params[key] = val[0]

    return params
