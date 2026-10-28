"""R60Login バックエンド。"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routers.login import router as login_router

app = FastAPI(title="R60Login")

# 開発時は Vite（5173）から、Docker 時は Nginx（8081）から呼ばれる。
# 本番では R60_CORS_ORIGINS を実際のオリジンに絞る。
_origins = [o.strip() for o in os.getenv(
    "R60_CORS_ORIGINS", "http://localhost:5173,http://localhost:8081"
).split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
