# -*- coding: utf-8 -*-

__author__ = 'Thom Wiggers'
__email__ = 'thom@thomwiggers.nl'
__version__ = '0.1.0'


def run(argv=None):  # pragma: no cover
    """Run the HTTP server

    Usage: httpserver [options]

    Options::

        -v,--verbose        Increase verbosity
        -d,--debug          Add debug commands/utils
    """
    import sys
    import docopt
    import textwrap
    argv = argv or sys.argv[1:]
    args = docopt.docopt(textwrap.dedent(run.__doc__), argv)

    print("Bla")
