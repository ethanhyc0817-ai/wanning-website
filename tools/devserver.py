#!/usr/bin/env python3
"""Local preview server that honours vercel.json rewrites + redirects.

Opening index.html from disk is not enough any more: the booking panel (/#contact)
loads /book-your-wave in a frame, and /golf.html etc. only exist through Vercel
rewrites to /pages/*.html. This serves the repo root with the same routing.

    python3 tools/devserver.py            # http://127.0.0.1:8765
    python3 tools/devserver.py 3000       # another port

No dependencies beyond Python 3.
"""
import json, re, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
V = json.load(open(os.path.join(ROOT, 'vercel.json')))
def to_re(src):
    pat = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', re.escape(src).replace(r'\:', ':'))
    pat = pat.replace(r'\(\.\*\)', '(.*)')
    return re.compile('^' + pat + '$')
REW = [(to_re(r['source']), r['destination']) for r in V.get('rewrites', [])]
RED = [(to_re(r['source']), r['destination'], r.get('permanent', False), r.get('statusCode')) for r in V.get('redirects', [])]
def sub(dest, m):
    d = dest
    for k, v in m.groupdict().items(): d = d.replace(':' + k, v)
    if m.groups() and not m.groupdict(): d = d.replace('$1', m.group(1))
    return d
class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_GET(self):
        u = urlsplit(self.path); p = u.path
        for rx, dest, perm, code in RED:
            m = rx.match(p)
            if m:
                self.send_response(code or (308 if perm else 307)); self.send_header('Location', sub(dest, m) + (('&' if '?' in dest else '?') + u.query if u.query else '')); self.end_headers(); return
        for rx, dest in REW:
            m = rx.match(p)
            if m and os.path.isfile(os.path.join(ROOT, sub(dest, m).lstrip('/'))):
                self.path = sub(dest, m) + ('?' + u.query if u.query else ''); break
        else:
            if p != '/' and not os.path.exists(os.path.join(ROOT, p.lstrip('/'))) and os.path.isfile(os.path.join(ROOT, p.lstrip('/') + '.html')):
                self.path = p + '.html' + ('?' + u.query if u.query else '')
        super().do_GET()
    def log_message(self, fmt, *a): sys.stderr.write('%s %s\n' % (self.command, self.path))
if __name__ == '__main__':
    print('Serving %s at http://127.0.0.1:%d  (Ctrl-C to stop)' % (ROOT, PORT))
    try: ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
    except KeyboardInterrupt: pass
