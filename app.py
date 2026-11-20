import http.client
import ipaddress
import json
import os
import socket
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, build_opener

ROOT = Path(__file__).parent
ARCHIVE = "https://web.archive.org"
DEMO = "https://fieldnotes.example/urban-moths"
MAX_BODY = 1_000_000
MAX_HTML = 2_000_000


def normalize(value):
    if not isinstance(value, str) or len(value) > 2048 or any(ord(c) < 33 for c in value) or "\\" in value:
        raise ValueError("Enter a complete HTTP or HTTPS URL.")
    p = urlsplit(value)
    if (p.scheme not in ("http", "https") or not p.hostname or p.username is not None
            or p.port not in (None, 443 if p.scheme == "https" else 80)):
        raise ValueError("Use an HTTP or HTTPS URL with a standard port and no credentials.")
    host = p.hostname.encode("idna").decode("ascii").rstrip(".")
    if "." not in host or host.endswith((".local", ".localhost", ".internal", ".home.arpa")):
        raise ValueError("Use a public web hostname.")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("Use a hostname instead of an IP address.")
    return urlunsplit((p.scheme, host, p.path or "/", p.query, ""))


def health(url):
    first = url
    for _ in range(4):
        p = urlsplit(url)
        port = 443 if p.scheme == "https" else 80
        conn = None
        try:
            addresses = socket.getaddrinfo(p.hostname, port, type=socket.SOCK_STREAM)
            if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global or
                                    ipaddress.ip_address(a[4][0]).is_multicast for a in addresses):
                return "blocked"
            family, kind, proto, _, address = addresses[0]
            def connect(_address, timeout, _source=None):
                sock = socket.socket(family, kind, proto)
                sock.settimeout(timeout)
                try:
                    sock.connect(address)
                    return sock
                except OSError:
                    sock.close()
                    raise
            connection = http.client.HTTPSConnection if p.scheme == "https" else http.client.HTTPConnection
            conn = connection(p.hostname, port, timeout=3)
            conn._create_connection = connect
            target = p.path + ("?" + p.query if p.query else "")
            conn.request("GET", target, headers={"User-Agent": "Tombstone/1.0", "Range": "bytes=0-0"})
            response = conn.getresponse()
            if response.status in (301, 302, 303, 307, 308) and response.getheader("Location"):
                url = normalize(urljoin(url, response.getheader("Location")))
                continue
            if response.status in (404, 410):
                return "dead"
            if 200 <= response.status < 300:
                return "live" if url == first else "redirected"
            return "inaccessible"
        except (OSError, ValueError, http.client.HTTPException):
            return "inaccessible"
        finally:
            if conn:
                conn.close()
    return "inaccessible"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def archive_fetch(path):
    with build_opener(NoRedirect).open(ARCHIVE + path, timeout=8) as response:
        data = response.read(MAX_HTML + 1)
        if len(data) > MAX_HTML:
            raise ValueError("Archive response exceeded 2 MB.")
        return data.decode(response.headers.get_content_charset() or "utf-8", errors="replace")


class Article(HTMLParser):
    hidden = {"script", "style", "nav", "header", "footer", "aside", "noscript", "template", "svg"}
    blocks = {"p", "blockquote", "li"}
    def __init__(self):
        super().__init__()
        self.skip = []
        self.active = None
        self.parts = []
        self.title = ""
        self.paragraphs = []
        self.author = ""
        self.published = ""

    def handle_starttag(self, tag, attrs):
        if self.skip or tag in self.hidden:
            if tag in self.hidden:
                self.skip.append(tag)
            return
        if tag == "meta":
            attrs = dict(attrs)
            key = attrs.get("property") or attrs.get("name")
            if key == "author":
                self.author = (attrs.get("content") or "")[:160]
            if key in {"article:published_time", "datePublished"}:
                self.published = (attrs.get("content") or "")[:40]
        if tag in self.blocks | {"title"} and self.active is None:
            self.active, self.parts = tag, []

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.pop()
            return
        if tag == self.active:
            value = " ".join("".join(self.parts).split())
            if tag == "title":
                self.title = value[:200]
            elif len(value) >= 45 and value not in self.paragraphs and len(self.paragraphs) < 60:
                self.paragraphs.append(value[:1400])
            self.active = None

    def handle_data(self, data):
        if self.active and not self.skip:
            self.parts.append(data)


def restore(url):
    if url == DEMO:
        article = Article()
        article.feed((ROOT / "docs" / "sample.html").read_text(encoding="utf-8"))
        return card(url, "dead", "20210417090000", article, True)
    status = health(url) if os.getenv("TOMBSTONE_CHECK_ORIGINS", "1") == "1" else "unchecked"
    if status == "blocked":
        return {"url": url, "health": status, "state": "blocked"}
    # Availability API uses a separate fixed host and returns the closest capture.
    try:
        with build_opener(NoRedirect).open("https://archive.org/wayback/available?" + urlencode({"url": url}), timeout=8) as res:
            data = json.loads(res.read(MAX_HTML + 1))
        closest = data.get("archived_snapshots", {}).get("closest", {})
        stamp = closest.get("timestamp", "")
        if not closest.get("available") or str(closest.get("status")) != "200":
            return {"url": url, "health": status, "state": "missing"}
        if not (isinstance(stamp, str) and len(stamp) == 14 and stamp.isascii() and stamp.isdigit()):
            raise ValueError("Invalid archive timestamp")
        datetime.strptime(stamp, "%Y%m%d%H%M%S")
    except (OSError, ValueError, AttributeError, http.client.HTTPException):
        return {"url": url, "health": status, "state": "unavailable"}
    article = Article()
    try:
        article.feed(archive_fetch(f"/web/{stamp}id_/{url}"))
    except (OSError, ValueError, LookupError, http.client.HTTPException):
        pass
    return card(url, status, stamp, article)


def card(url, health_status, stamp, article, demo=False):
    paragraphs = article.paragraphs[:12]
    evidence = [{"id": i + 1, "quote": p} for i, p in enumerate(paragraphs)]
    source = "/sample.html" if demo else f"{ARCHIVE}/web/{stamp}/{url}"
    return {
        "url": url, "health": health_status, "state": "restored" if evidence else "partial",
        "demo": demo, "title": article.title or urlsplit(url).hostname,
        "published": article.published, "author": article.author, "source": source,
        "captured": datetime.strptime(stamp, "%Y%m%d%H%M%S").date().isoformat(),
        "evidence": evidence, "highlights": [e["id"] for e in evidence[:3]],
    }


class Handler(BaseHTTPRequestHandler):
    hits = defaultdict(deque)
    lock = threading.Lock()
    slots = threading.BoundedSemaphore(4)
    files = {"/": ("web/index.html", "text/html"), "/app.js": ("web/app.js", "text/javascript"),
             "/style.css": ("web/style.css", "text/css"), "/sample.html": ("docs/sample.html", "text/html")}

    def log_message(self, *_args):
        pass

    def send(self, status, body, mime="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", mime + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def reply(self, status, obj):
        self.send(status, json.dumps(obj).encode())

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/health":
            self.reply(200, {"ok": True})
        elif path in self.files:
            file, mime = self.files[path]
            self.send(200, (ROOT / file).read_bytes(), mime)
        else:
            self.reply(404, {"error": "Page not found."})

    def do_POST(self):
        if self.path != "/api/restore":
            self.reply(404, {"error": "Endpoint not found."})
            return
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "Send JSON."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                self.reply(413, {"error": "Invalid request size."})
                return
            self.connection.settimeout(5)
            body = json.loads(self.rfile.read(size))
            url = normalize(body["url"])
        except (ValueError, TypeError, KeyError, OSError):
            self.reply(400, {"error": "Enter a complete public HTTP or HTTPS URL."})
            return
        with self.lock:
            now = time.monotonic()
            for ip, queue in list(self.hits.items()):
                while queue and now - queue[0] > 60:
                    queue.popleft()
                if not queue:
                    del self.hits[ip]
            hits = self.hits[self.client_address[0]]
            permitted = len(hits) < 15
            if permitted:
                hits.append(now)
        if not permitted or not self.slots.acquire(blocking=False):
            self.reply(429, {"error": "Archive desk is busy. Try again shortly."})
            return
        try:
            self.reply(200, restore(url))
        finally:
            self.slots.release()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"Tombstone listening on {host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
