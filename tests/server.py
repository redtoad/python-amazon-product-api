# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>
#
# This program is release under the BSD License. You can find the full text of
# the license in the LICENSE file.

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys

DEFAULT_ADDRESS = 'localhost'
DEFAULT_PORT = 0

class TestServer (HTTPServer):
    
    """
    Small test server which can be taught which files to serve with which 
    response code. Try the following snippet for testing API calls::
        
        server = TestServer(port=8080)
        server.start()
        print 'Test server running at http://%s:%i' % server.server_address
        server.serve_file(code=503)
        # any call to http://localhost:8080 will get a 503 response.
        # ...
        
    """
    
    #: timeout for request handling (in seconds?)
    timeout = 1
    
    def __init__(self, host=DEFAULT_ADDRESS, port=DEFAULT_PORT):
        HTTPServer.__init__(self, (host, port), RequestHandler)
        self.file, self.code = (None, 204) # HTTP 204: No Content
        self._thread = None
        self.logging = False

        # Workaround for Python 2.4: using port 0 will bind a free port to the 
        # underlying socket. The server_address, however, is not reflecting 
        # this! So we need to adjust it manually.
        if self.server_address[1] == 0: 
            self.server_address = (self.server_address[0], self.server_port)

    def serve_file(self, path=None, code=200):
        """
        Serves file (with specified HTTP error code) as response to next 
        request.
        """
        self.file, self.code = (path, code)
        
    def serve_forever (self):
        """
        Handles one request at a time until stopped.
        """
        self._running = True
        while self._running:
            self.handle_request()
        
    def start(self):
        """
        Starts test server in own thread.
        """
        try:
            import threading
        except ImportError:
            self.fail("This test needs threading support!")
            
        self._thread = threading.Thread(target=self.serve_forever)
        self._thread.start()
        
    def stop(self):
        """
        Stops test server.
        """
        self._running = False
        self._thread.join()

class RequestHandler(BaseHTTPRequestHandler):
    
    """
    Handler for HTTP requests serving files specified by server instance.
    """
    
    def log_message(self, format, *args):
        """
        Overrides standard logging method.
        """
        if self.server.logging:
            sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), 
                self.log_date_time_string(), format % args))
        
    def do_GET(self):
        """
        Any GET response will be sent ``self.server.file`` as message and 
        ``self.server.code`` as response code.
        """
        self.send_response(self.server.code)
        self.end_headers()
        
        if type(self.server.file) in (str, unicode):
            self.wfile.write(open(self.server.file).read())
        else:
            self.wfile.write(self.server.file)
            
        return


if __name__ == '__main__':
    server = TestServer()
    server.start()
    server.logging = True
    
    print 'Test server is running at http://%s:%i' % (server.server_address)
    print 'Type <Ctrl-C> to stop'
    
    import os.path
    xml = os.path.join(os.path.dirname(__file__), '2009-10-01', 
        'Help-de-fails-for-wrong-input.xml')
    server.serve_file(xml, 302)
    
    try:
        while True: 
            pass
    except KeyboardInterrupt:
        print '\rstopping...'
    server.stop()
    
