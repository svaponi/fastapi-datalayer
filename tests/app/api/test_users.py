import pytest


@pytest.mark.asyncio
async def test_users(aclient):
    res = await aclient.get("/api/users")
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.is_success
