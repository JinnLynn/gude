# -*- coding: utf-8 -*-
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import sys, os, posixpath, shutil
import urllib,urlparse
import mimetypes
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ServerRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        result = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(result.query)
        if result.query == 'rebuild':
            self.server.rebuildSite()
            if 'rebuild' in query:
                del query['rebuild']
            parts = list(tuple(result))
            parts[4] = urllib.urlencode(query)
            parts = tuple(parts)
            new_url = urlparse.urlunparse(parts)
            self.redirect(new_url)
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.do_404()
        name, ext = os.path.splitext(path)
        if not ext:
            return self.do_404()
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found: /%s" % self.server.site.getRelativePathWithDeploy(path))
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.server.site.deployPath
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def do_404(self):
        f = None
        site = self.server.site
        content = '<!doctype html><head><title>404</title</head><body>404</body></html>'
        try:
            f = open(os.path.join( site.deployPath, '404.html' ))
            content = f.read()
        except Exception, e:
            pass
        f = StringIO()
        f.write(content)
        length = f.tell()
        f.seek(0)
        self.send_response(404)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def redirect(self, path, temporary=True):
        self.send_response(302 if temporary else 301)
        self.send_header('Location', path)
        self.end_headers()

    def log_request(self, code='-', size='-'):
        if self.server.isSilent:
            return
        SimpleHTTPRequestHandler.log_request(self, code, size)
    
class Server(HTTPServer):
    def __init__(self, core, port, silent):
        self.core = core
        self.site = core.site
        self.isSilent = silent
        HTTPServer.__init__(self, ('', port), ServerRequestHandler)

    def rebuildSite(self):
        self.core.startBuild()