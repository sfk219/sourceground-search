# SourceGround — Source-Cited Knowledge Search

A runnable **SQLite FTS5/BM25 retrieval and FastAPI** project. Index local `.md` and `.txt` documents, search chunks, and return answers with source filename and line ranges. No external LLM is required; this is extractive retrieval, not generative AI.

## Install and use
```bash
pip install -e '.[test]'
python -m sourceground.cli index documents
python -m sourceground.cli search "readiness rollout"
uvicorn sourceground.api:app --reload
pytest -q
```
Then visit `http://localhost:8000/docs` or `/search?q=readiness`. This is an independent portfolio implementation; do not index confidential documents.