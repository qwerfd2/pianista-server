import os
import databases
import sqlalchemy
from sqlalchemy import Table, Column, Boolean, Float, Integer, String, JSON, DateTime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
import datetime
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
import json

from api.crypt import decrypt

DB_NAME = "player.db"
DB_PATH = os.path.join(os.getcwd(), DB_NAME)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("userid", String(32), unique=True, nullable=False),
    Column("password", String(32), unique=True, nullable=False),
    Column("nickname", String(32), unique=True, nullable=True),
    Column("diamond", Integer, nullable=True),
    Column("gold", Integer, nullable=True),
    Column("created_at", Integer),
    Column("blocked", Boolean, default=False),
    Column("clearCount", Integer, default = 0),
    Column("composer", JSON, default='[]'),
    Column("clear", JSON, default='[]'),
    Column("piano", JSON, default='[]'),
    Column("tour", JSON, default='[]'),
    Column("item", JSON, default='[]'),
    Column("mail", JSON, default='[]'),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("userid", String(32), unique=True, nullable=False),
    Column("session", String(256), unique=True, nullable=False)
)

results = Table(
    "results",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("owner", Integer, nullable=False),
    Column("patternId", Integer, nullable=False),
    Column("score", Integer, nullable=False),
    Column("star", Integer, nullable=False),
    Column("accuracy", Float, nullable=False),
    Column("maxCombo", Integer, nullable=False),
    Column("allCombo", Boolean, nullable=False),
    Column("updatedAt", Integer, default=datetime.datetime.utcnow),
    Column("master", Boolean, nullable=False)
)


async def init_db():
    if not os.path.exists(DB_PATH):
        print("[DB] Creating new database:", DB_PATH)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    await engine.dispose()
    print("[DB] Database initialized successfully.")

async def get_user_and_validate_session(request: Request):
    access_token = request.headers.get("X-Photon-AccessToken")
    body = await request.body()
    decrypted_data = decrypt(body.decode('utf-8'))
    print("1",decrypted_data)
    if not access_token:
        return decrypted_data, None, None, {"code": -100}
    else:
        query = sessions.select().where(sessions.c.session == access_token)
        session = await database.fetch_one(query)
        
        if not session:
            return decrypted_data, None, None, {"code": -101}
        else:
            user_id = session["userid"]
            query = users.select().where(users.c.userid == user_id)
            user = await database.fetch_one(query)
            
            if not user:
                return decrypted_data, None, session, {"code": -102}
            else:
                return decrypted_data, user, session, None