#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_httpserver
----------------------------------

Tests for `httpserver` module.
"""
import os
import unittest
from unittest import mock
from freezegun import freeze_time

from httpserver.httpserver import HttpProtocol


class TestHttpserver(unittest.TestCase):

    def setUp(self):
        """Set up an HttpProtocol instance with a fake transport"""
        self.fixtures_location = os.path.join(
            os.path.dirname(__file__), 'fixtures')
        self.httpprotocol = HttpProtocol('localhost', self.fixtures_location)
        self.transport = mock.MagicMock(spec=['write', 'close'])
        self.transport.write = mock.Mock()
        self.transport.close = mock.Mock()
        self.httpprotocol.connection_made(self.transport)

    def _read_fixture(self, filename):
        """Convenient function to read one of our fixtures"""
        filename = os.path.join(self.fixtures_location, filename)
        with open(filename, 'rb') as f:
            content = f.read()
        return content

    def _sent(self):
        """Gets the data that was written to the transport"""
        values = [tuple(c)[0][0]
                  for c in self.transport.write.call_args_list]
        self.transport.write.reset_mock()
        return b''.join(values)

    def test_invalid_method(self):
        """Test if the server rejects methods it does not recognise"""
        data = self._read_fixture('invalid_method.crlf')
        self.httpprotocol.data_received(data)

        response = self._sent()
        # Do we have the error?
        assert response.startswith(b'HTTP/1.1 501 Not Implemented\r\n')
        head, body = response.split(b'\r\n\r\n', 1)
        assert b'Content-Length' in head

        # Has the connection been closed?
        assert self.transport.close.called

    def test_invalid_http_version(self):
        """Test if the server rejects invalid HTTP headers"""
        data = self._read_fixture('invalid_version.crlf')
        self.httpprotocol.data_received(data)
        response = self._sent()

        head, body = response.split(b'\r\n\r\n', 1)
        # Do we have the error
        assert head.startswith(b'HTTP/1.1 505 HTTP Version Not Supported')
        assert b'Content-Length' in head  # We SHOULD have an entity (10.5.6)
        assert b'HTTP/1.1' in body  # We SHOULD reply what is supported

    def test_get_index_root(self):
        """Test GET /"""
        data = self._read_fixture('get_index_root.crlf')
        index = self._read_fixture('index.html')
        self.httpprotocol.data_received(data)

        response = self._sent()
        assert response.startswith(b'HTTP/1.1 200 OK\r\n')
        head, body = response.split(b'\r\n\r\n', 1)
        assert 'Content-Length: {}'.format(len(body)).encode('utf-8') in head
        assert body == index

    def test_get_index_named(self):
        """Test GET /index.html"""
        data = self._read_fixture('get_index_named.crlf')
        index = self._read_fixture('index.html')
        self.httpprotocol.data_received(data)
        response = self._sent()
        assert response.startswith(b'HTTP/1.1 200 OK\r\n')
        head, body = response.split(b'\r\n\r\n', 1)
        assert 'Content-Length: {}'.format(len(body)).encode('utf-8') in head
        assert body == index

        # Has the connection been closed (no Keep-Alive)
        assert self.transport.close.called

    def test_get_directory_without_index(self):
        """Test GET /emptydir"""
        data = self._read_fixture('no_index_dir/get_directory_without_index.crlf')
        self.httpprotocol.data_received(data)
        response = self._sent()

        head, body = response.split(b'\r\n\r\n', 1)
        # Do we have the 404 error
        assert head.startswith(b'HTTP/1.1 404 Not Found\r\n')
        # TODO more tests here

    def test_get_absoluteURI(self):
        """HTTP 1.1 servers MUST accept absoluteURI form Request-URIs

        RFC 2616 section 5.1.2
        """
        data = self._read_fixture('absolute_uri_request.crlf')
        self.httpprotocol.data_received(data)
        head, body = self._sent().split(b'\r\n\r\n', 1)

        assert head.startswith(b'HTTP/1.1 200 OK\r\n')

    def test_get_absoluteURI_404(self):
        """We don't want to serve our index.html on GET nu.nl"""
        data = self._read_fixture('absolute_uri_wrong_host.crlf')
        self.httpprotocol.data_received(data)
        head, body = self._sent().split(b'\r\n\r\n', 1)

        assert head.startswith(b'HTTP/1.1 404 Not Found\r\n')

    def test_get_persistent(self):
        """Try and get index.html over the same connection"""
        data = self._read_fixture('get_index_persistent.crlf')
        index = self._read_fixture('index.html')

        for i in range(2):
            self.httpprotocol.data_received(data)
            head, body = self._sent().split(b'\r\n\r\n', 1)
            assert head.startswith(b'HTTP/1.1 200 OK')
            assert body == index
            assert not self.transport.close.called

        data = self._read_fixture('get_index_named.crlf')
        self.httpprotocol.data_received(data)
        head, body = self._sent().split(b'\r\n\r\n', 1)
        assert head.startswith(b'HTTP/1.1 200 OK')
        assert body == index
        assert self.transport.close.called

    @freeze_time("2015-03-14 09:26:53", tz_offset=0)
    def test_get_has_date_headers(self):
        """Test for date headers"""
        requests = [
                self._read_fixture('get_index_named.crlf'), #200
                self._read_fixture('no_index_dir/get_directory_without_index.crlf'), #404
                self._read_fixture('invalid_version.crlf'), #505
                ]

        for request in requests:
            self.httpprotocol.data_received(request)
            response = self._sent()

            head, body = response.split(b'\r\n\r\n', 1)

            assert b'Date: ' in head
            assert b'Date: Sat, 14 Mar 2015 09:26:53 +0000' in head

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
