# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import logging

__author__ = 'Thom Wiggers'
__email__ = 'thom@thomwiggers.nl'
__version__ = '0.1.0'


def _start_server(bindaddr, port):
    import asyncio
    from .httpserver import HttpProtocol
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(HttpProtocol, bindaddr, port)
    server = loop.run_until_complete(coroutine)

    print('Starting server on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


def run(argv=None):  # pragma: no cover
    """Run the HTTP server

    Usage: httpserver [options] [<bindaddress>] [<port>]

    Default bind address: 127.0.0.1
    Default port:         8080

    Options::

        -v,--verbose        Increase verbosity
        -d,--debug          Add debug commands/utils
    """
    import sys
    import docopt
    import textwrap
    argv = argv or sys.argv[1:]
    args = docopt.docopt(textwrap.dedent(run.__doc__), argv)

    level = logging.WARNING
    if args['--verbose']:
        level = logging.INFO
    if args['--debug']:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    logger = logging.getLogger('run method')
    logger.debug('CLI args: %s' % args)

    bindaddr = args['<bindaddress>'] or '127.0.0.1'
    port = args['<port>'] or '8080'
    _start_server(bindaddr, port)
