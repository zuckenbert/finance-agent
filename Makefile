# Makefile

# Project structure:
# finance-analyst-agent/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py
# │   ├── config.py
# │   └── tools/
# │       ├── __init__.py
# │       └── sheets.py
# ├── tests/
# │   ├── __init__.py
# │   ├── conftest.py
# │   └── test_sheets.py
# ├── .env
# ├── .env.example
# ├── .gitignore
# ├── Dockerfile
# ├── docker-compose.yml
# ├── Makefile
# └── requirements.txt

.PHONY: venv lint test run docker-build clean

venv:
	python3.12 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

lint:
	ruff check .
	ruff format .

test:
	pytest -q --cov=app tests/

run:
	python -m app.main

docker-build:
	docker build -t finance-analyst-agent .

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 