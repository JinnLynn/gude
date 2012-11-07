# -*- coding: utf-8 -*-
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import sys, os

from setting import DEFAULT_SERVER_PORT

def run(port):
    os.chdir('deploy')
    httpd = HTTPServer(('', port), SimpleHTTPRequestHandler)
    print 'Webserver [http://localhost:%d] starting...' % port
    httpd.serve_forever()
    pass
