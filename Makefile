.PHONY: setup install dev backend frontend generate-types db-init lint format

setup: install db-init generate-types

install:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
	yarn install

dev:
	yarn dev

backend:
	cd backend && PYTHONPATH=.. .venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && yarn dev

generate-types:
	cd backend && .venv/bin/python ../shared/scripts/generate_types.py
	yarn ts-gen

db-init:
	cd backend && .venv/bin/python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

lint:
	cd backend && .venv/bin/ruff check .
	cd frontend && yarn eslint src

format:
	cd backend && .venv/bin/ruff format .
	cd frontend && yarn prettier --write src
