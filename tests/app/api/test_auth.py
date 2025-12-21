import pytest


@pytest.mark.asyncio
async def test_signup_login_and_whoami(aclient):
    payload = dict(email="test@example.com", password="secret")
    res = await aclient.post("/api/auth/signup", json=payload)
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.is_success

    payload = dict(email="test@example.com", password="secret")
    res = await aclient.post("/api/auth/login", json=payload)
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.is_success
    access_token = res.json().get("access_token")
    assert access_token

    # get without authorization header should work because authentication is set as cookie
    res = await aclient.get("/api/auth/whoami")
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.is_success

    aclient.cookies.clear()

    # after clearing the cookies, get without authorization header should not work
    res = await aclient.get("/api/auth/whoami")
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 401

    # get with authorization header should work
    headers = {"Authorization": f"bearer {access_token}"}
    res = await aclient.get("/api/auth/whoami", headers=headers)
    print(f"{res.request.method} {res.url} >> {res.status_code} {res.text}")
    assert res.is_success
