# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import os
from urllib.parse import unquote
from http.client import responses

import mimetypes

import asyncio
import logging
import socket

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

        for (header, content) in response['headers'].items():
            self.logger.debug("Sending header: '%s: %s'", header, content)
            self._write_transport('{}: {}\r\n'.format(header, content))

        if 'body' in response and 'Content-Length' not in response['headers']:
            self._write_transport(
                'Content-Length: {}\r\n'.format(len(response['body'])))

        self._write_transport('\r\n')
        if 'body' in response:
            self._write_transport(response['body'])

    def connection_made(self, transport):
        self.logger.info('Connection made at object %s', id(self))
        self.transport = transport
        self.keepalive = True

    def data_received(self, data):
        self.logger.debug('Received data: %s', repr(data))

        try:
            request = self.parse_headers(data)
            self.handle_request(request)
        except InvalidRequestError as e:
            self._write_response(e.get_http_response())
        self.transport.close()

    def parse_headers(self, data):
        self.logger.debug('Parsing headers')

        request_strings = list(map(lambda x: x.decode('utf-8'),
                                   data.split(b'\r\n')))

        request = dict()

        # Parse request method and HTTP version
        request['method'] = request_strings[0].split()[0]
        request['version'] = request_strings[0].split()[2]
        request['target'] = request_strings[0].split()[1]

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
        # Check if we're getting a sane request
        if request['method'] not in ('GET'):
            raise InvalidRequestError(501, 'Method not implemented')

        if request['version'] not in ('HTTP/1.0', 'HTTP/1.1'):
            raise InvalidRequestError(
                505, 'Version not supported. Supported versions are: {}, {}'
                .format('HTTP/1.0', 'HTTP/1.1'))

        if request['version'] == 'HTTP/1.1' and not (
            request.get('Connection') == 'Close'):
          self.keepalive = True
        elif request['version'] == 'HTTP/1.0' and (
            request.get('Connection') == 'Keep-Alive'):
          self.keepalive = True

        host, location = self._get_request_uri(request['target'])

        if host is None:
            host = request.get('Host')

        if host is not None and not host == self.host:
            raise InvalidRequestError(404, 'Not Found')

        filename = os.path.join(self.folder, unquote(location))

        response = _get_response(version=request['version'])

        if os.path.isdir(filename):
            filename = os.path.join(filename, 'index.html')

        if not os.path.isfile(filename):
            raise InvalidRequestError(404, 'Not Found')

        response['headers']['Content-Type'] = mimetypes.guess_type(
            filename)[0] or 'text/plain'

        with open(filename, 'rb') as fp:
            response['body'] = fp.read()

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
