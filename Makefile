.PHONY: test install clean lint format test-coverage

install:
	pip install -r requirements.txt
	pip install -e .

test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=jensbay_utilities --cov-report=html --cov-report=term

lint:
	flake8 jensbay_utilities/ tests/

format:
	black jensbay_utilities/ tests/

clean:
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

pre-commit-install:
	pip install pre-commit
	pre-commit install

pre-commit-run:
	pre-commit run --all-files