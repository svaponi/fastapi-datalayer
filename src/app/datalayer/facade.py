import sys


import fastapi


from asyncpg_datalayer.db import DB

from .agency import AgencyRepository
from .chat import ChatRepository
from .chat_message import ChatMessageRepository
from .chat_message_to_user import ChatMessageToUserRepository
from .user_account import UserAccountRepository
from .user_auth import UserAuthRepository
from .user_device import UserDeviceRepository


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
        self.agency = AgencyRepository(db)
        self.chat = ChatRepository(db)
        self.chat_message = ChatMessageRepository(db)
        self.chat_message_to_user = ChatMessageToUserRepository(db)
        self.user_account = UserAccountRepository(db)
        self.user_auth = UserAuthRepository(db)
        self.user_device = UserDeviceRepository(db)

    ### custom methods go below ###
