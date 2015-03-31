# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import logging

__author__ = 'Thom Wiggers, Luuk Scholten'
__email__ = 'thom@thomwiggers.nl, info@luukscholten.com'
__version__ = '1.1.0'


def _start_server(bindaddr, port, hostname, folder):
    """Starts an asyncio server"""
    import asyncio
    from .httpserver import HttpProtocol
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(lambda: HttpProtocol(hostname, folder),
                                   bindaddr,
                                   port)
    server = loop.run_until_complete(coroutine)

    print('Starting server on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


def run(argv=None):  # pragma: no cover
    """Run the HTTP server

    Usage:
        httpserver [options] [<folder>]

    Options::

        -h,--host=<hostname>        What host name to serve (default localhost)
        -a,--bindaddress=<address>  Address to bind to (default 127.0.0.1)
        -p,--port=<port>            Port to listen on (default 8080)
        -v,--verbose                Increase verbosity to INFO messages
        -d,--debug                  Increase verbosity to DEBUG messages
        --help                      Print this help message
        --version                   Print the version

    To serve /path/to/www on all (ipv4) addresses for host myserver
    on port 80::
        httpserver -a 0.0.0.0 -p 80 -h myserver /path/to/www
    """
    import sys
    import os
    import docopt
    import textwrap

    # Check for the version
    if not sys.version_info >= (3, 4):
        print('This python version is not supported. Please use python 3.4')
        exit(1)

    argv = argv or sys.argv[1:]

    # remove some RST formatting
    docblock = run.__doc__.replace('::', ':')
    args = docopt.docopt(textwrap.dedent(docblock), argv)

    if args['--version']:
        print("httpserver version {} by {}".format(
            __version__,
            __author__))
        exit(0)

    # Set up logging
    level = logging.WARNING
    if args['--verbose']:
        level = logging.INFO
    if args['--debug']:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    logger = logging.getLogger('run method')
    logger.debug('CLI args: %s' % args)

    bindaddr = args['--bindaddress'] or '127.0.0.1'
    port = args['--port'] or '8080'
    folder = args['<folder>'] or os.getcwd()
    hostname = args['--host'] or 'localhost'
    _start_server(bindaddr, port, hostname, folder)
