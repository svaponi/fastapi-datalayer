import pytest

from tests.testutils.mock_environ import mock_environ


@pytest.mark.asyncio
async def test_not_found(aclient):
    res = await aclient.get("/foobar")
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized(aclient):
    res = await aclient.get("/api/auth/whoami", headers={"authorization": "invalid"})
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_docs_not_found(aclient):
    res = await aclient.get("/api/docs")
    assert res.status_code == 404
    res = await aclient.get("/api/openapi.json")
    assert res.status_code == 404


@pytest.fixture
def env_vars_enable_docs(env_vars):
    with mock_environ(ENABLE_DOCS="1"):
        yield


@pytest.mark.asyncio
@pytest.mark.usefixtures("env_vars_enable_docs")
async def test_docs_found(aclient):
    res = await aclient.get("/api/docs")
    assert res.status_code == 200
    res = await aclient.get("/api/openapi.json")
    assert res.status_code == 200
