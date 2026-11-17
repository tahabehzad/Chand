"""Bound work-document requests before multipart parsing (ADR-012 security review).

Authority: WORK_PROFILE_PAYROLL upload limit.
Related: work_profile upload route.
Scope: pure ASGI byte bound, including chunked bodies; no file/credential logging.
"""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

MAX_UPLOAD_REQUEST = 5_000_000 + 65_536


class WorkUploadLimit:
    """Buffer only bounded multipart bodies, before FastAPI allocates/spools files."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not (scope["type"] == "http" and scope.get("method") == "POST"
                and scope.get("path", "").endswith("/work-documents")):
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > MAX_UPLOAD_REQUEST:
                response = JSONResponse(status_code=413, content={"error": {
                    "code": "WORK_UPLOAD_TOO_LARGE", "detail": "حجم درخواست بیش از حد مجاز است.",
                }})
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        used = False

        async def replay() -> Message:
            nonlocal used
            if used:
                return await receive()
            used = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self.app(scope, replay, send)
