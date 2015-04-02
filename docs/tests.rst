======================
Testing considerations
======================

We use both unit tests and integration tests with selenium. 

Unit Tests
----------
We mock the transport (socket) in the unit test, so we don't actually start up the 
server, we just test the ``HttpProtocol`` itself.
To forge the request headers, we use fixtures that are appended in the ``tests/``
directory.

We test the following basic scenarios:

- GET for an existing single resource
  [``test_get_index_named``] 
- GET for a single resource that doens't exit
- GET for an existing single resource followed by a GET for that same resource,
  using the ETag and ``If-None-Match`` field
  [``test_get_with_etag``]
- GET for a directory with an existing index.html
  [``test_get_index_root``]
- GET for a directory wit non-existing index.html
  [``test_get_directory_without_index``]
- Testing persistent connections, with the last GET prompting to close the 
  connection
  [``test_get_persistent``]
- Test whether the timeout actually closes the connection
  [``test_timeout``, ``test_timeout_request``]

Additionally to the given scenarios above, we test some basic functionality
[ ``test_invalid_method``, ``test_invalid_http_version``, ``test_get_absoluteURI``, 
``test_get_absoluteURI_404``, ``test_get_has_date_headers``, ``test_send_keepalive``, 
``test_send_keepalive_longer`` ]

Selenium Tests
--------------
To use the selenium tests, ``firefox`` is a required dependency. We use two simple selenium
tests to test the HTTP server with a real browser. Two tests scenarios are implemented:

1. Test whether GET on the root dir (with an ``index.html``) actually returns that index.
   ``index.html`` is a simple web page with two images, to test parallel GET requests and
   basic pipeling. 
2. Test whether a non-existing resource sends a correct 404 response, and that the response
   is displayed to the user.

