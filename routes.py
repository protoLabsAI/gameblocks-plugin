"""The public module server — mounted at /plugins/gameblocks (NO gated router: the
vendored blocks are static public source, there is no mutable state to protect).

Game artifacts run in the artifact plugin's nested sandbox (opaque origin), so their
module imports are cross-origin fetches — every response sends
``Access-Control-Allow-Origin: *`` (the same reason the artifact plugin's vendor
route does). Cache is a day, not immutable: the URL doesn't change when the plugin
re-vendors upstream.
"""

from __future__ import annotations


def build_public_router():
    from fastapi import APIRouter
    from fastapi.responses import FileResponse, PlainTextResponse, Response

    from . import blocks

    router = APIRouter()
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=86400",
    }

    @router.get("/modules/{path:path}")
    async def _module(path: str):
        f = blocks.resolve(f"modules/{path}")
        if f is None:
            return Response(status_code=404)
        return FileResponse(f, media_type="text/javascript", headers=headers)

    @router.get("/summary.md")
    async def _summary():
        return PlainTextResponse(blocks.summary_text(), media_type="text/markdown; charset=utf-8", headers=headers)

    return router
