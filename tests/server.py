# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>
#
# This program is release under the BSD License. You can find the full text of
# the license in the LICENSE file.

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

DEFAULT_ADDRESS = 'localhost'
DEFAULT_PORT = 8080

class TestServer (HTTPServer):
    
    """
    Small test server which can be taught which files to serve with which 
    response code. Try the following snippet for testing API calls::
        
        import threading
        server = TestServer()
        threading.Thread(target=server.serve_forever).start()
        print 'Test server running at http://%s:%i' % server.server_address
        server.serve_file(code=503)
        # any call to http://localhost:8080 will gat a 503 response.
        
    """
    
    def __init__(self, server_address=(DEFAULT_ADDRESS, DEFAULT_PORT)):
        HTTPServer.__init__(self, server_address, RequestHandler)
        
        self.file, self.code = (None, 500)
        self.stopped = False
        
    def serve_file(self, path=None, code=200):
        """
        Serves file (with specified HTTP error code) as response to next 
        request.
        """
        self.file, self.code = (path, code)

class RequestHandler(BaseHTTPRequestHandler):
    
    """
    Handler for HTTP requests serving files specified by server instance.
    """
    
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
    print 'Test server is running at http://%s:%i' % (server.server_address)
    print 'Use <Ctrl-C> to stop'
    server.serve_file('./2009-10-01/Help-fails-for-wrong-input.xml')
    server.serve_forever()
    
