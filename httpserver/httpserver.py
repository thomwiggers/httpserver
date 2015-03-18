# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import os
from urllib.parse import unquote
from http.client import responses

import mimetypes

import asyncio
import logging
import socket
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_response(**kwargs):
    if 'code' not in kwargs:
        kwargs['code'] = 200
    if 'headers' not in kwargs:
        kwargs['headers'] = dict()
    if 'version' not in kwargs:
        kwargs['version'] = 'HTTP/1.1'

    return dict(**kwargs)


class HttpProtocol(asyncio.Protocol):
    """HTTP/1.1 Protocol implementation

    Per connection made, one of these gets instantiated
    """

    def __init__(self, host, folder):
        self.folder = folder
        self.host = host
        self.logger = logger.getChild('HttpProtocol {}'.format(id(self)))
        self.logger.debug('Instantiated HttpProtocol')

    def _write_transport(self, string):
        if isinstance(string, str):
            self.transport.write(string.encode('utf-8'))
        else:
            self.transport.write(string)

    def _write_response(self, response):
        status = '{} {} {}\r\n'.format(response['version'],
                                       response['code'],
                                       responses[response['code']])
        self.logger.debug("Responding status: '%s'", status.strip())
        self._write_transport(status)

        if 'body' in response and 'Content-Length' not in response['headers']:
            response['headers']['Content-Length'] = len(response['body'])

        response['headers']['Date'] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

        for (header, content) in response['headers'].items():
            self.logger.debug("Sending header: '%s: %s'", header, content)
            self._write_transport('{}: {}\r\n'.format(header, content))


        self._write_transport('\r\n')
        if 'body' in response:
            self._write_transport(response['body'])

    def connection_made(self, transport):
        """Called when the connection is made"""
        self.logger.info('Connection made at object %s', id(self))
        self.transport = transport
        self.keepalive = True

    def connection_lost(self, exception):
        """Called when the connection is lost or closed.

        The argument is either an exception object or None. The latter means
        a regular EOF is received, or the connection was aborted or closed by
        this side of the connection.
        """
        if exception:
            self.logger.exception('Connection lost!')
        else:
            self.logger.info('Connection lost')

    def data_received(self, data):
        self.logger.debug('Received data: %s', repr(data))

        try:
            request = self.parse_headers(data)
            self.handle_request(request)
        except InvalidRequestError as e:
            self._write_response(e.get_http_response())

        if not self.keepalive:
            self.transport.close()

    def parse_headers(self, data):
        self.logger.debug('Parsing headers')

        request_strings = list(map(lambda x: x.decode('utf-8'),
                                   data.split(b'\r\n')))

        request = dict()

        # Parse request method and HTTP version
        method_line = request_strings[0].split()

        # The first line has either 3 or 2 arguments
        if not (2 <= len(method_line) <= 3):
            self.keepalive = False  # We don't trust you
            raise InvalidRequestError(400, 'Bad request')
        # HTTP 0.9 isn't supported.
        if len(method_line) == 2:
            self.keepalive = False  # HTTP/0.9 won't support persistence
            raise InvalidRequestError(505, "This server only supports HTTP/1.0"
                                           "and HTTP/1.1")
        else:
            request['version'] = method_line[2]

        # method
        request['method'] = method_line[0]
        request['target'] = method_line[1]

        # Parse the headers
        for line in request_strings[1:]:
            if line == '':
                break
            self.logger.debug("header: '{}'".format(line))
            header, body = line.split(': ', 1)
            request[header] = body

        self.logger.debug('request object: %s', request)
        return request

    def _get_request_uri(self, request_uri):
        """Server MUST accept full URIs (5.1.2)"""
        if request_uri.startswith('/'):
            return (None, request_uri[1:])
        elif '://' in request_uri:
            locator = request_uri.split('://', 1)[1]
            host, path = locator.split('/', 1)
            return (host.split(':')[0], path)

    def handle_request(self, request):

        # Check if this is a persistent connection.
        if request['version'] == 'HTTP/1.1':
            self.keepalive = not request.get('Connection') == 'close'
        elif request['version'] == 'HTTP/1.0':
            self.keepalive = request.get('Connection') == 'Keep-Alive'

        # Check if we're getting a sane request
        if request['method'] not in ('GET'):
            raise InvalidRequestError(501, 'Method not implemented')

        if request['version'] not in ('HTTP/1.0', 'HTTP/1.1'):
            raise InvalidRequestError(
                505, 'Version not supported. Supported versions are: {}, {}'
                .format('HTTP/1.0', 'HTTP/1.1'))

        host, location = self._get_request_uri(request['target'])

        if host is None:
            host = request.get('Host')

        if host is not None and not host == self.host:
            raise InvalidRequestError(404, 'Not Found')

        filename = os.path.join(self.folder, unquote(location))
        self.logger.debug('trying to serve %s', filename)

        response = _get_response(version=request['version'])

        if os.path.isdir(filename):
            filename = os.path.join(filename, 'index.html')

        if not os.path.isfile(filename):
            raise InvalidRequestError(404, 'Not Found')

        response['headers']['Content-Type'] = mimetypes.guess_type(
            filename)[0] or 'text/plain'

        sha1 = hashlib.sha1()

        with open(filename, 'rb') as fp:
            response['body'] = fp.read()
            sha1.update(response['body'])

        etag = sha1.hexdigest()

        # Create 304 response if if-none-match matches etag
        if request.get('If-None-Match') == '"{}"'.format(etag):
            response = _get_response(code=304)

        response['headers']['Etag'] = '"{}"'.format(etag)

        self._write_response(response)


class InvalidRequestError(Exception):
    def __init__(self, code, *args, **kwargs):
        super(InvalidRequestError, self).__init__(*args, **kwargs)
        self.code = code

    def get_http_response(self):
        return _get_response(
            code=self.code,
            body=str(self),
            headers={
                'Content-Type': 'text/plain'
            }
        )
