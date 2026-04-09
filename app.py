from pathlib import Path
from typing import Callable, Iterable, Tuple


BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"


def _read_index() -> bytes:
    return INDEX_HTML.read_bytes()


def app(environ: dict, start_response: Callable) -> Iterable[bytes]:
    path = environ.get("PATH_INFO", "/")

    if path == "/" or path == "" or path.endswith(".html"):
        body = _read_index()
        headers: list[Tuple[str, str]] = [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ]
        start_response("200 OK", headers)
        return [body]

    # Single-page style fallback
    body = _read_index()
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
    ]
    start_response("200 OK", headers)
    return [body]
