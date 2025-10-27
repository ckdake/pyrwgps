.PHONY: install lint test format clean

install:
	python -m pip install -e '.[dev]'

lint:
	black --check pyrwgps
	flake8 pyrwgps
	pylint pyrwgps
	mypy --install-types --non-interactive pyrwgps

format:
	black pyrwgps

test:
	python -m pytest --cov=pyrwgps --cov-report=term-missing -v

clean:
	rm -rf .pytest_cache .mypy_cache .coverage
