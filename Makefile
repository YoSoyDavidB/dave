.PHONY: help install dev test lint lint-fix format build up down pre-commit-install

help:
	@echo "Available commands:"
	@echo "  install            - Install all dependencies"
	@echo "  dev                - Start development environment"
	@echo "  test               - Run all tests"
	@echo "  lint               - Run linters (check only)"
	@echo "  lint-fix           - Run linters and auto-fix issues"
	@echo "  format             - Format code with ruff"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  build              - Build Docker images"
	@echo "  up                 - Start production containers"
	@echo "  down               - Stop containers"

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

lint-fix:
	cd backend && poetry run ruff check --fix src tests
	cd backend && poetry run ruff format src tests
	cd frontend && npm run lint -- --fix

format:
	cd backend && poetry run ruff format src tests
	cd frontend && npm run format

pre-commit-install:
	cd backend && poetry run pre-commit install
	@echo "Pre-commit hooks installed! They will run automatically on git commit."

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down
