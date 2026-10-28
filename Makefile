.PHONY: help gate status md test build dev-login-backend dev-login-frontend up down

help:
	@echo "make gate                 # 6 道门"
	@echo "make status               # 8 工程进度"
	@echo "make md                   # YAML -> readable/*.md + *.zh.html"
	@echo "make test                 # 后端单测（R60Login）"
	@echo "make build                # 前端构建（R60Login）"
	@echo "make dev-login-backend    # 本地起后端 :8080"
	@echo "make dev-login-frontend   # 本地起前端 :5173"
	@echo "make up                   # docker compose 起全部"
	@echo "make down                 # 停掉 docker compose"

gate:
	python -m plat gate

status:
	python -m plat status

md:
	python -m plat md --module R60Login --html

test:
	cd cases/R60/R60Login/src/backend && python -m pytest tests/unit

build:
	cd cases/R60/R60Login/src/frontend && npm run build

dev-login-backend:
	cd cases/R60/R60Login/src/backend && uvicorn app.main:app --reload --port 8080

dev-login-frontend:
	cd cases/R60/R60Login/src/frontend && npm run dev

up:
	docker compose up --build

down:
	docker compose down
