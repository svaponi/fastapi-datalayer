import fastapi
from starlette.testclient import TestClient

from app.core.correlation_id import setup_correlation_id


def test_request_context():
    app = fastapi.FastAPI()
    setup_correlation_id(app)

    @app.get("/ok")
    def ok():
        return dict(message="ok")

    with TestClient(app, raise_server_exceptions=False) as client:
        res = client.get("/ok", headers={"x-request-id": "001"})
        print(
            f"{res.request.method} {res.url} >> {res.status_code} {res.text} {res.headers}"
        )
        assert res.status_code == 200
        assert res.headers.get("x-request-id") == "001"
