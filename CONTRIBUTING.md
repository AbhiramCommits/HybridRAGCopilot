# Contributing

## Quick Development Loop

1. Clone repository and set up environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start PostgreSQL via Docker or rely on SQLite fallback:
   ```bash
   make db-up
   ```
3. Seed synthetic corpus and structured tables:
   ```bash
   make seed
   ```
4. Run ingestion pipeline to build FAISS index, BM25 store, and chunk parquet store:
   ```bash
   make ingest
   ```
5. Run tests:
   ```bash
   make test
   ```
6. Run linter:
   ```bash
   make lint
   ```
