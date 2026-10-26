"""設定。値は環境変数から読む（コードに実値を書かない）。"""
from __future__ import annotations

import os


class Settings:
    """接続情報・URL 組立の材料。**実値はリポジトリに置かない**。"""

    def __init__(self) -> None:
        self.db_user = os.environ.get("R60_DB_USER", "TBL_1")
        self.db_password = os.environ.get("R60_DB_PASSWORD", "PWD_1")
        self.db_dsn = os.environ.get("R60_DB_DSN", "IP_1:PORT_1/SID_1")
        # 遷移 URL の材料（環境ごとに異なる。Q-107 で受渡し方法を確認中）
        self.url_scheme = os.environ.get("R60_URL_SCHEME", "http")
        self.url_host = os.environ.get("R60_URL_HOST", "IP_1")
        self.url_port = os.environ.get("R60_URL_PORT", "PORT_1")
        self.url_context = os.environ.get("R60_URL_CONTEXT", "/R60")
        self.url_route = os.environ.get("R60_URL_ROUTE", "/Pages/index.jsp")


settings = Settings()
