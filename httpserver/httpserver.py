# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import asyncio
import logging

logger = logging.getLogger(__name__)


class HttpProtocol(asyncio.Protocol):
    """HTTP/1.1 Protocol implementation

    Per connection made, one of these gets instantiated
    """

    def __init__(self):
        self.logger = logger.getChild('HttpProtocol {}'.format(id(self)))
        self.logger.debug('Instantiated HttpProtocol')

    def connection_made(self, transport):
        self.logger.info("Connection made at object %s", id(self))
        self.transport = transport

    def data_received(self, data):
        self.logger.info("Received data: %s", repr(data))
        self.transport.write("Hi I see your %s", data)
