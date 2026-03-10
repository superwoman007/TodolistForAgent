.PHONY: install run test

install:
	pip install -r requirements.txt

run:
	cd apps/api && uvicorn app.main:app --reload --port 8000

test:
	cd apps/api && pytest tests/ -v
