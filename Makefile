.PHONY: lint test lint-fix

lint:
	flake8 .

test:
	pytest tests/ -v

lint-fix:
	python scripts/lint_fix_agent.py
