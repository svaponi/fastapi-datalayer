import uuid

import asyncpg
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from asyncpg_datalayer.db import DB
from asyncpg_datalayer.migrationtool.main import apply_migrations
from testcontainers.postgres import PostgresContainer

from app import migrations_dir
from app.app import create_app
from app.datalayer.facade import DatalayerFacade
from tests.testutils.mock_environ import mock_environ


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine", driver=None) as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="function")
async def postgres_url(postgres_container: PostgresContainer):
    db_url = postgres_container.get_connection_url()
    db_name = "_" + uuid.uuid4().hex
    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute(f"CREATE DATABASE {db_name};")
    finally:
        await conn.close()
    yield db_url.removesuffix(postgres_container.dbname) + db_name
    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute(f"DROP DATABASE IF EXISTS {db_name} WITH(FORCE);")
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def db(postgres_url):
    await apply_migrations(postgres_url, migrations_dir)
    yield DB(postgres_url, echo=True)


@pytest.fixture
def facade(db):
    return DatalayerFacade(db)


@pytest.fixture
def env_vars(postgres_url):
    with mock_environ(dotenv_file=".env.test", POSTGRES_URL=postgres_url, LOG_SQL="1"):
        yield


@pytest_asyncio.fixture
async def app(env_vars):
    app = create_app()
    # LifespanManager assures that lifespan events are sent to the ASGI app.
    # see https://github.com/florimondmanca/asgi-lifespan#usage
    async with LifespanManager(app):
        yield app


@pytest_asyncio.fixture
async def aclient(app):
    # AsyncClient won't trigger lifespan events, therefore we need to use LifespanManager.
    # see https://fastapi.tiangolo.com/advanced/async-tests/
    # see https://github.com/florimondmanca/asgi-lifespan#usage
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as aclient:
        yield aclient
