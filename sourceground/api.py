import os
from fastapi import FastAPI,Query
from dataclasses import asdict
from .index import search,answer
app=FastAPI(title="SourceGround: Traceable Retrieval")
def db():return os.environ.get("SOURCEGROUND_DB","sourceground.db")
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/search")
def find(q:str=Query(min_length=2,max_length=300),limit:int=Query(5,ge=1,le=20)):
    return {"query":q,"results":[asdict(x) for x in search(db(),q,limit)]}
@app.get("/answer")
def extract(q:str=Query(min_length=2,max_length=300)):
    return answer(search(db(),q,3),q)
