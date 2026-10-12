from fastapi.testclient import TestClient
from sourceground.index import ingest,search,answer
from sourceground import api

def test_index_search_and_idempotence(tmp_path):
    docs=tmp_path/"docs";docs.mkdir()
    (docs/"guide.md").write_text("Deploy the new service safely.\nVerify readiness probes.\n")
    db=str(tmp_path/"index.db")
    assert ingest(db,docs)==1
    assert ingest(db,docs)==1
    result=search(db,"readiness")
    assert len(result)==1
    assert result[0].source=="guide.md"
    assert answer(result,"readiness")["grounded"]
    assert search(db,"unfindableword")==[]

def test_api(monkeypatch,tmp_path):
    docs=tmp_path/"docs";docs.mkdir()
    (docs/"incident.txt").write_text("Check deployment errors before rollback.")
    db=str(tmp_path/"api.db");ingest(db,docs)
    monkeypatch.setenv("SOURCEGROUND_DB",db)
    client=TestClient(api.app)
    assert client.get("/health").json()["status"]=="ok"
    result=client.get("/answer",params={"q":"deployment"}).json()
    assert result["grounded"]
    assert result["citations"][0]["file"]=="incident.txt"
    assert client.get("/search",params={"q":"a"}).status_code==422
