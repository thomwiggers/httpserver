#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_httpserver
----------------------------------

Tests for `httpserver` module.
"""

import unittest
from unittest import mock
import os

from httpserver.httpserver import HttpProtocol

class TestHttpserver(unittest.TestCase):

    def setUp(self):
        self.fixtures_location = os.path.join(
                os.path.dirname(__file__), 'fixtures')
        self.httpprotocol = HttpProtocol(self.fixtures_location)
        self.transport = mock.MagicMock(spec=['write', 'close'])
        self.transport.write = mock.Mock()
        self.transport.close = mock.Mock()
        self.httpprotocol.transport = self.transport

    def _read_fixture(self, filename):
        filename = os.path.join(self.fixtures_location, filename)
        with open(filename, 'rb') as f:
            content = f.read()
        return content

    def _sent(self):
        values = [tuple(c)[0][0]
                for c in self.httpprotocol.transport.write.call_args_list]
        self.httpprotocol.transport.write.reset_mock()
        return b''.join(values)

    def test_invalid_method(self):
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
        data = self._read_fixture('invalid_version.crlf')
        self.httpprotocol.data_received(data)
        response = self._sent()

        head, body = response.split(b'\r\n\r\n', 1)
        # Do we have the error
        assert head.startswith(b'HTTP/1.1 505 HTTP Version Not Supported')
        assert 'Content-Length' in head  # We SHOULD have an entity (10.5.6)
        assert b'HTTP 1.1' in body  # We should reply what is supported

    def test_get_index_root(self):
        """Test GET /"""
        data = self._read_fixture('get_index_root.crlf')
        index = self._read_fixture('index.html')
        self.httpprotocol.data_received(data)

        response = self._sent()
        assert response.startswith(b'HTTP/1.1 200 OK\r\n')
        head, body = response.split(b'\r\n\r\n', 1)
        assert b'Content-Length: {}'.format(len(body)) in head
        assert body == index

    def test_get_index_named(self):
        """Test GET /index.html"""
        data = self._read_fixture('get_index_named.crlf')
        index = self._read_fixture('index.html')
        self.httpprotocol.data_received(data)
        response = self._sent()
        assert response.startswith(b'HTTP/1.1 200 OK\r\n')
        head, body = response.split(b'\r\n', 1)
        assert b'Content-Length: {}'.format(len(body)) in head
        assert body == index

        # Has the connection been closed (no Keep-Alive)
        assert self.transport.close.called

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
