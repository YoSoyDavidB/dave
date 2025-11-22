.PHONY: help install dev test lint build up down

help:
	@echo "Available commands:"
	@echo "  install    - Install all dependencies"
	@echo "  dev        - Start development environment"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run linters"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start production containers"
	@echo "  down       - Stop containers"

install:
	cd backend && poetry install
	cd frontend && npm install

dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Backend running at http://localhost:8000"
	@echo "Run 'cd frontend && npm run dev' for frontend"

test:
	cd backend && poetry run pytest
	cd frontend && npm run test -- --run

lint:
	cd backend && poetry run ruff check src tests
	cd backend && poetry run mypy src
	cd frontend && npm run lint

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down
