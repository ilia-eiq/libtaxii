from urllib.error import HTTPError

import libtaxii
import libtaxii.messages


IN_RESPONSE_TO = "test in_response_to value"
TAXII_CONTENT_TYPE = libtaxii.constants.VID_TAXII_XML_11
TEST_MESSAGE_ID = "test message id"
CONTENT_XML = '<taxii_11:Discovery_Request xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" message_id="test message id"/>'


def test_httplib_http_response(httpserver):
    httpserver.expect_request("/poll_service_path/").respond_with_data(
        CONTENT_XML.encode('windows-1252'),
        content_type="application/xml; charset=windows-1252",
        headers={"X-TAXII-Content-Type": TAXII_CONTENT_TYPE}
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)
    message = libtaxii.get_message_from_httplib_http_response(http_response, IN_RESPONSE_TO)

    assert isinstance(message, libtaxii.messages_11.DiscoveryRequest)
    assert message.in_response_to is None
    assert message.message_id == 'test message id'


def test_httplib_http_response_error(httpserver):
    httpserver.expect_request("/poll_service_path/").respond_with_data(
        CONTENT_XML.encode('windows-1252'),
        status=500,
        content_type="application/xml; charset=windows-1252",
        headers={"X-TAXII-Content-Type": TAXII_CONTENT_TYPE}
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)

    assert isinstance(http_response, HTTPError)

    message = libtaxii.get_message_from_httplib_http_response(http_response, IN_RESPONSE_TO)

    assert isinstance(message, libtaxii.messages_11.DiscoveryRequest)
    assert message.in_response_to is None
    assert message.message_id == 'test message id'


def test_httplib_http_response_no_taxii_content_type(httpserver):
    httpserver.expect_request("/poll_service_path/").respond_with_data(
        CONTENT_XML.encode('windows-1252'),
        content_type="application/xml; charset=windows-1252",
    )

    client = libtaxii.clients.HttpClient()
    http_response = client.call_taxii_service2(httpserver.host, '/poll_service_path/', libtaxii.constants.VID_TAXII_XML_10, b"", port=httpserver.port)
    message = libtaxii.get_message_from_httplib_http_response(http_response, IN_RESPONSE_TO)

    assert isinstance(message, libtaxii.messages_11.StatusMessage)
    assert message.in_response_to == IN_RESPONSE_TO
    assert message.message_id == '0'

    server = http_response.headers.get("Server")
    date = http_response.headers.get("Date")
    assert message.message == (
        f'''Server: {server}\r\n'''
        f'''Date: {date}\r\n'''
        '''Content-Type: application/xml; charset=windows-1252\r\n'''
        '''Content-Length: 129\r\n'''
        '''Connection: close\r\n'''
        '''\r\n'''
        '''<taxii_11:Discovery_Request xmlns:taxii_11="http://taxii.mitre.org/messages/taxii_xml_binding-1.1" message_id="test message id"/>'''
    )

