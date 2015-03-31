=====================
Design considerations
=====================

We've used python 3.4's ``asyncio`` library to handle the creating and
destroying of connections so that we don't have to deal with threads.
We assume that the web server sends requests quickly enough such that
all lines arrive at the same time in our ``data_received`` event. This
assumption works out in practice as clients will buffer what they send.

We first parse the headers and perform some sanity checking. Throughout
our code we raise an exception for error conditions: these exceptions
are convertable to HTTP responses.

We parse the headers into a dictionary and pass this to the ``_handle_request``
method. This method will read this dictionary and return a ``response``
dictionary with the right options and, if applicable, the response body.

This response dictionary is eventually written back out to the transport.
