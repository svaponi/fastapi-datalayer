import asyncio

import pytest

from tests.testutils.mock_environ import mock_environ


# See https://docs.sqlalchemy.org/en/20/errors.html#error-3o7r


@pytest.fixture
def env_vars(postgres_url):
    with mock_environ(
        dotenv_file=".env.test",
        POSTGRES_URL=postgres_url,
        # Set low pool size to make it easier to produce a 429.
        # Remember that create_defaults needs to run successfully first!
        POOL_SIZE="5",
        POOL_MAX_OVERFLOW="0",
        POOL_TIMEOUT="0",
    ):
        yield


@pytest.mark.asyncio
async def test_too_many_requests(aclient):
    _creds = {"email": "jdoe@example.com", "password": "secret"}

    async def _login():
        return (await aclient.post(f"/api/auth/login", json=_creds)).status_code

    status_codes = await asyncio.gather(*[_login() for _ in range(10)])
    assert 500 not in status_codes
    assert 429 in status_codes
