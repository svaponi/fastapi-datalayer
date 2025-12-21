import asyncio

import pytest

from tests.testutils.mock_environ import mock_environ


# See https://docs.sqlalchemy.org/en/20/errors.html#error-3o7r


@pytest.fixture
def env_vars(postgres_url):
    with mock_environ(
        dotenv_file=".env.test",
        POSTGRES_URL=postgres_url,
        # Set pool size to 1 to make it easier to reproduce the error
        POOL_SIZE="1",
        POOL_MAX_OVERFLOW="0",
        POOL_TIMEOUT="0",
    ):
        yield


@pytest.mark.asyncio
async def test_too_many_requests(aclient):

    _creds = {"email": "user", "password": "secret"}

    async def _get():
        return (await aclient.post(f"/api/auth/login", json=_creds)).status_code

    status_codes = await asyncio.gather(*[_get() for _ in range(10)])
    assert 500 not in status_codes
    assert 429 in status_codes
