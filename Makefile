.PHONY: db-up db-down seed ingest ingest-lora train-lora serve eval test lint clean

db-up:
	docker compose up -d

db-down:
	docker compose down

seed:
	python scripts/make_corpus.py

ingest:
	python -m hybridrag.ingest.pipeline --mode base

ingest-lora:
	python -m hybridrag.ingest.pipeline --mode lora

train-lora:
	python -m hybridrag.finetune.train_lora

serve:
	uvicorn hybridrag.api.app:app --reload --host 0.0.0.0 --port 8000

eval:
	python -m hybridrag.eval.harness --full

regression:
	python -m hybridrag.eval.harness --regression

test:
	pytest -v --cov=hybridrag --cov-report=term-missing

lint:
	ruff check .

clean:
	rm -rf artifacts/* results/* data/corpus/* data/eval/* __pycache__ .pytest_cache .coverage
