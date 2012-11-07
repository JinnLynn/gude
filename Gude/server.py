# -*- coding: utf-8 -*-
import SimpleHTTPServer, BaseHTTPServer
import os

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import sys
import shutil
import mimetypes
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Server(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        print path
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        print words
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        print path
        return path


def start():
    os.chdir('deploy')
    server_address = ('', 8910)
    handler_class = Server
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    pass
