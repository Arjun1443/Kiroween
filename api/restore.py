import json

from app import MAX_BODY, normalize, restore


def respond(start_response, status, payload):
    body = json.dumps(payload).encode("utf-8")
    start_response(status, [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
    ])
    return [body]


def app(environ, start_response):
    if environ["REQUEST_METHOD"] != "POST":
        return respond(start_response, "405 Method Not Allowed", {"error": "Use POST."})
    if environ.get("CONTENT_TYPE", "").partition(";")[0].strip().lower() != "application/json":
        return respond(start_response, "415 Unsupported Media Type", {"error": "Send JSON."})
    try:
        length = int(environ.get("CONTENT_LENGTH") or "0")
        if not 0 < length <= MAX_BODY:
            return respond(start_response, "413 Content Too Large", {"error": "Invalid request size."})
        payload = json.loads(environ["wsgi.input"].read(length))
        url = normalize(payload["url"])
    except (ValueError, TypeError, KeyError):
        return respond(start_response, "400 Bad Request", {"error": "Enter a complete public HTTP or HTTPS URL."})
    return respond(start_response, "200 OK", restore(url))
