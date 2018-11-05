import os.path

import xml.etree.ElementTree as ET
import pytest

import amazonproduct.simple

pytest_plugin = "pytest-localserver"
_here = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def api(request, monkeypatch, httpserver):
    """
    Starts a test server instance serving a previously cached XML file. ::

        @pytest.mark.mockresponse("test.xml", skip=False)
        def test_response_is_parsed_correctly(api):
            assert ItemLookup().Items.Request.isValid == true

    As an added safety measure, a test is skipped if request arguments
    do not matched the ones from the cached response -- unless you use
    ``skip=False`` (default: ``True``).
    """
    ignored_args = ["AWSAccessKeyId", "AssociateTag", "Service", "Timestamp", "Signature"]
    args_cached = None
    skip_if_mismatching_args = True

    def extract_ns(e):
        """Extracts XML namespace of element"""
        return e.tag[1:].split("}")[0]

    def extract_request_args(xml):
        """Extracts request arguments from cached XML response."""
        root = ET.fromstring(xml)
        nsmap = {"aws": extract_ns(root)}
        arguments = root.findall(".//aws:OperationRequest/aws:Arguments/aws:Argument", nsmap)
        return {arg.get("Name"): arg.get("Value") for arg in arguments if arg.get("Name") not in ignored_args}

    marker = request.node.get_closest_marker('mockresponse')
    if marker:
        fname = marker.args[0]
        skip_if_mismatching_args = marker.kwargs.get('skip', True)
        path = os.path.join(_here, fname)
        cached = open(path).read()
        args_cached = extract_request_args(cached)
        httpserver.serve_content(cached)

    def mock_signed_url(*args, **qargs):
        """Replacement for singed_url which always returns the URL of out test server."""
        if skip_if_mismatching_args and args_cached != qargs:
            pytest.skip("Cached and queried arguments do not match!\n"
                        "cached  : %r\nqueried : %r" % (args_cached, qargs))
        return httpserver.url

    monkeypatch.setattr(amazonproduct.core, "signed_url", mock_signed_url)
    amazonproduct.simple.init("access", "secret", "de", "tag")
    return amazonproduct.simple._api_singleton


@pytest.mark.mockresponse("ItemLookup-B01M7SI4AE.xml", skip=False)
def test_response_is_parsed_correctly(api):
    assert amazonproduct.simple.ItemSearch().Items.Request.IsValid == "True"


@pytest.mark.mockresponse("ItemLookup-B01M7SI4AE.xml")
def test_parsing_with_objectify(api):
    resp = amazonproduct.simple.ItemLookup(ItemId="B01M7SI4AE", ResponseGroup="Large")
    assert resp.OperationRequest.RequestId == "97cfc75e-196b-44b4-aa93-fa6996586c4a"
