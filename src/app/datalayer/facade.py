import sys

import fastapi
from asyncpg_datalayer.db import DB

from .users import UsersRepository


def get_db(request: fastapi.Request) -> DB:
    if not hasattr(request.app.state, "db"):
        message = """DB not found in app.state.
        Make sure to initialize the DB in your FastAPI app like this:

        ```
        import os
        import fastapi
        from asyncpg_datalayer.db_factory import create_db

        app = fastapi.FastAPI()
        app.state.db = create_db()
        ```
        """
        print(message, file=sys.stderr)
        raise RuntimeError("DB not found in app.state")
    return request.app.state.db


class DatalayerFacade:
    def __init__(self, db: DB = fastapi.Depends(get_db)) -> None:
        super().__init__()
        self.db = db
        self.users = UsersRepository(db)

    ### custom methods go below ###
