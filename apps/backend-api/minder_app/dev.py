"""Reserved C API 8103 + same-origin static/API web server 9103; local only."""
import mimetypes
import os
from pathlib import Path
import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler
from .runtime import application, ROOT


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass  # no tokens, private content or HTTP parameters in console logs


def web_app(api):
    root = ROOT / "apps/frontend-web"
    allowed = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
    def serve(environ, start_response):
        path = environ["PATH_INFO"]
        if path.startswith("/api/"):
            return api(environ, start_response)
        if path not in allowed or environ["REQUEST_METHOD"] != "GET":
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not found"]
        target = root / allowed[path]
        raw = target.read_bytes()
        start_response("200 OK", [("Content-Type", mimetypes.guess_type(str(target))[0] or "text/plain"),
            ("Content-Length", str(len(raw))), ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; "
             "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")])
        return [raw]
    return serve


def main():
    app = application()
    api = make_server("127.0.0.1", int(os.environ.get("MINDER_API_PORT", "8103")), app, handler_class=QuietHandler)
    web = make_server("127.0.0.1", int(os.environ.get("MINDER_UI_PORT", "9103")), web_app(app), handler_class=QuietHandler)
    thread = threading.Thread(target=api.serve_forever, daemon=True)
    thread.start()
    print("Minder local source services: API 8103, UI 9103. Provisional evidence-fit policy; deployment not activated.", flush=True)
    try:
        web.serve_forever()
    finally:
        api.shutdown()
        api.server_close()
        web.server_close()


if __name__ == "__main__":
    main()
