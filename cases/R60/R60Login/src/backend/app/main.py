"""FastAPI アプリ。端点は 3 本のみ。"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.routers import login
from .core.errors import BizError, resolve
from .core.response import err

app = FastAPI(title="R60Login", version="0.1.0")
app.include_router(login.router)


@app.exception_handler(BizError)
async def _biz(_req: Request, exc: BizError) -> JSONResponse:
    r = resolve(exc.error_id)
    return JSONResponse(status_code=200, content=err(r["code"], r["message"]))


@app.exception_handler(Exception)
async def _sys(_req: Request, _exc: Exception) -> JSONResponse:
    r = resolve("E-104")
    return JSONResponse(status_code=500, content=err(r["code"], r["message"]))
