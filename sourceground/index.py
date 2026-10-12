"""SQLite FTS5 / BM25 chunked document retrieval with line citations."""
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Evidence:
    source: str
    line_start: int
    line_end: int
    text: str
    rank: float

def connect(path):
    db=sqlite3.connect(path);db.row_factory=sqlite3.Row
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(source UNINDEXED, line_start UNINDEXED, line_end UNINDEXED, text, tokenize='unicode61')")
    return db

def chunks(text,lines=6):
    if lines<1:raise ValueError("lines must be positive")
    rows=text.splitlines()
    for i in range(0,len(rows),lines):
        snippet="\n".join(rows[i:i+lines]).strip()
        if snippet:yield i+1,min(len(rows),i+lines),snippet

def ingest(db_path,folder):
    base=Path(folder).resolve()
    if not base.is_dir():raise ValueError("expected a directory")
    count=0
    with connect(db_path) as db:
        for filename in sorted(base.rglob("*")):
            if filename.is_symlink() or not filename.is_file() or filename.suffix not in (".md",".txt"):continue
            rel=filename.relative_to(base).as_posix()
            db.execute("DELETE FROM chunks WHERE source=?",(rel,))
            for first,last,text in chunks(filename.read_text(encoding="utf-8")):
                db.execute("INSERT INTO chunks(source,line_start,line_end,text) VALUES(?,?,?,?)",(rel,first,last,text));count+=1
    return count

def search(db_path,query,limit=5):
    if not 1<=limit<=20:raise ValueError("limit outside 1..20")
    tokens=re.findall(r"\w+",query,flags=re.UNICODE)[:12]
    if not tokens:return []
    match=" OR ".join('"'+t+'"' for t in tokens)
    with connect(db_path) as db:
        result=db.execute("SELECT source,line_start,line_end,text,bm25(chunks) AS rank FROM chunks WHERE chunks MATCH ? ORDER BY rank LIMIT ?",(match,limit)).fetchall()
    return [Evidence(row["source"],int(row["line_start"]),int(row["line_end"]),row["text"],float(row["rank"])) for row in result]

def answer(evidence,query):
    if not evidence:return {"answer":"No supporting source found.","citations":[],"grounded":False}
    terms=set(x.casefold() for x in re.findall(r"\w+",query))
    head=evidence[0];lines=[line.strip() for line in head.text.splitlines() if line.strip()]
    selected=next((line for line in lines if any(t in line.casefold() for t in terms)),lines[0])
    return {"answer":selected[:280],"citations":[{"file":head.source,"line_start":head.line_start,"line_end":head.line_end}],"grounded":True}
