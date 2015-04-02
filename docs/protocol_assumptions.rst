======================================
Protocol assumptions and limitations
======================================

We make a general assumptions that the client is a capable HTTP/1.1 client.
We do have some checks, but cannot guarantee that httpserver works correctly 
when the client does not conform to RFC2616. We do support HTTP/1.0 clients,
but we cannot guarantee that every HTTP/1.0 RFC requirement is implemented.

- In contrast to RFC2616-sec8.1.2, we close the connection when the client sends
  a bad request. We don't trust the client if it is not capable to send a valid
  request.
- httpserver only supports requests with the GET method. GET requests to valid
  files will send the file in a 200 response. GET requests to an invlid file
  will send a 404 Not Found response.
- If a directory is requested and ``index.html`` exists in that directory, the index
  is sered with a 200 response. If ``index.html`` does not exist, a 404 Not Found is
  sent to the client.
- Persistent connections are supported for both HTTP/1.0 and HTTP/1.1. We use a 
  default timeout value of 15 seconds.
- ETag is supported (RFC2616-sec14.19), the ETag is calculated with a SHA-1 hash
  of the content. The client may ask for the resource with the same ETag with a
  ``If-None-Match`` field set in the header. If the resource matches with the ETag,
  a 304 Not Modified/ response is sent to the client. ``Last-Modified`` handling
  is ignored.
- ``Content-Length`` field is added to any response with a valid message body.
  (see RFC2616-sec14.13)
- ``Date`` is added to every response (see RFC2616-sec14.18)
