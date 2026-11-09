# CVBoost AI — Makefile

.PHONY: install dev test lint security docker-up docker-down clean

# ── Install ───────────────────────────────────────────────────────────────────
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd frontend && pip install -r requirements-frontend.txt
	@echo "Installing pre-commit hooks..."
	pre-commit install

# ── Development servers ───────────────────────────────────────────────────────
dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && streamlit run app/app.py --server.port 8501

dev: # Run both (requires two terminals or use tmux)
	@echo "Start backend: make dev-backend"
	@echo "Start frontend: make dev-frontend"

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	cd backend && pytest app/tests/ -v --cov=app --cov-report=html --cov-report=term-missing

test-fast:
	cd backend && pytest app/tests/ -v -x --no-cov -k "not pdf"

# ── Linting ───────────────────────────────────────────────────────────────────
lint:
	cd backend && ruff check app/ --fix
	cd backend && ruff format app/

lint-check:
	cd backend && ruff check app/
	cd backend && ruff format --check app/

# ── Security ──────────────────────────────────────────────────────────────────
security:
	@echo "Running bandit security scan..."
	cd backend && bandit -r app/ -ll
	@echo "Running pip-audit..."
	cd backend && pip-audit

# ── Docker ────────────────────────────────────────────────────────────────────
docker-up:
	docker-compose up --build -d
	@echo "Backend: http://localhost:8000/api/docs"
	@echo "Frontend: http://localhost:8501"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ── Env setup ─────────────────────────────────────────────────────────────────
env:
	cp .env.example .env
	@echo ".env created! Edit it with your API keys."

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
	find . -name "*.db" -delete

# ── DB migrations (Alembic) ───────────────────────────────────────────────────
migrate:
	cd backend && alembic upgrade head

migration:
	cd backend && alembic revision --autogenerate -m "$(MSG)"
