import json
from src.handler import app

def test_get_latest_shape(monkeypatch):
    class DummyTable:
        def query(self, **kwargs):
            return {"Items": [{"pk":"metrics","sk":"2025-01-01T00:00:00Z","min":0,"max":1,"avg":0.5,"count":2,"s3_key":"raw/1.json"}]}
    class DummyRes:
        def Table(self, name): return DummyTable()
    monkeypatch.setattr(app, "table", DummyRes().Table("x"))

    event = {"requestContext":{"http":{"method":"GET"}}}
    resp = app.lambda_handler(event, None)
    assert resp["statusCode"] == 200
    body = json.loads(resp["body"])
    assert body["status"] == "ok"
    assert "latest" in body
