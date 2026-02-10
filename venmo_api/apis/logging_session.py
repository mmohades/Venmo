import orjson
from devtools import pformat
from requests import PreparedRequest, Response, Session
from rich import print

MAX_BODY_LOG = 1024 * 100  # 100 KB limit to avoid OOM in logs; tweak as needed


def safe_text(b: bytes | None, fallback_repr=True) -> str:
    if b is None:
        return "None"
    try:
        text = b.decode("utf-8")
        if len(text) <= MAX_BODY_LOG:
            return orjson.loads(text)
        else:
            return text[:MAX_BODY_LOG] + "\n...TRUNCATED..."
    except Exception:
        if fallback_repr:
            return repr(b[:MAX_BODY_LOG]) + (
                "...TRUNCATED..." if len(b) > MAX_BODY_LOG else ""
            )
        return "<binary>"


class LoggingSession(Session):
    """
    requests.Session subclass that pretty-logs its requests and responses using
    rich.print
    """

    def send(self, request: PreparedRequest, **kwargs) -> Response:
        print(f"\n→ REQUEST: {request.method} {request.url}")
        print(f"→ Request headers: {pformat(dict(request.headers))}")

        body = request.body
        if isinstance(body, str):
            print(f"→ Request body (str): {pformat(safe_text(body.encode()))}")
        elif isinstance(body, bytes):
            print(f"→ Request body (bytes): {pformat(safe_text(body))}")
        elif body is None:
            print("→ Request body: None")
        else:
            # could be generator/iterable (multipart streaming)
            print(f"→ Request body: (type={type(body).__name__}) {repr(body)}")

        resp = super().send(request, **kwargs)

        print(f"← RESPONSE: {resp.status_code} {resp.reason}")
        print(f"← Response headers: {pformat(dict(resp.headers))}")

        try:
            content = resp.content
            print(f"← Response body: {pformat(safe_text(content))}")
        except Exception as e:
            print(f"← Response body: <unreadable: {e}>")

        return resp
