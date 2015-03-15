# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import os
from urllib.parse import unquote
from http.client import responses

import mimetypes

import asyncio
import logging

logger = logging.getLogger(__name__)


def _get_response(**kwargs):
    if 'code' not in kwargs:
        kwargs['code'] = 200
    if 'headers' not in kwargs:
        kwargs['headers'] = dict()
    if 'body' not in kwargs:
        kwargs['body'] = ''
    if 'version' not in kwargs:
        kwargs['version'] = 'HTTP/1.1'

    return dict(**kwargs)


class HttpProtocol(asyncio.Protocol):
    """HTTP/1.1 Protocol implementation

    Per connection made, one of these gets instantiated
    """

    def __init__(self, folder):
        self.folder = folder
        self.logger = logger.getChild('HttpProtocol {}'.format(id(self)))
        self.logger.debug('Instantiated HttpProtocol')

    def _write_transport(self, string):
        self.transport.write(string.encode('utf-8'))

    def _write_response(self, response):
        status = '{} {} {}\r\n'.format(response['version'],
                                       response['code'],
                                       responses[response['code']])
        self._write_transport(status)

        for (header, content) in response['headers'].items():
            self._write_transport('{}: {}\r\n'.format(header, content))

        self._write_transport('\r\n')
        self._write_transport(response['body'])

    def connection_made(self, transport):
        self.logger.info('Connection made at object %s', id(self))
        self.transport = transport

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
            header, body = line.split(':', 1)
            request[header] = body.lstrip()

        self.logger.debug('request object: %s', request)
        return request

    def handle_request(self, request):
        # Check if we're getting a sane request
        if request['method'] not in ('GET'):
            raise InvalidRequestError(501, 'Method not implemented')

        if request['version'] not in ('HTTP/1.0', 'HTTP/1.1'):
            raise InvalidRequestError(505, 'Version not supported')

        filename = os.path.join(self.folder,
                                unquote(request['target'].lstrip('/')))

        response = _get_response(version=request['version'])

        if os.path.isdir(filename):
            filename = os.path.join(filename, 'index.html')

        if not os.path.isfile(filename):
            raise InvalidRequestError(404, 'Not Found')

        response['headers']['Content-Type'] = mimetypes.guess_type(filename)

        with open(filename, 'r') as fp:
            response['body'] = fp.read()

        self._write_response(response)


class InvalidRequestError(Exception):
    def __init__(self, code, *args, **kwargs):
        super(InvalidRequestError, self).__init__(*args, **kwargs)
        self.code = code

    def get_http_response(self):
        return _get_response(
            code=self.code,
            body=str(self)
        )
