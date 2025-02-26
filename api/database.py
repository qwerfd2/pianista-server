import os
import databases
import sqlalchemy
from sqlalchemy import Table, Column, Boolean, Float, Integer, String, JSON, DateTime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
import datetime
from starlette.responses import JSONResponse, Response
from starlette.requests import Request

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
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
    Column("blocked", Boolean, nullable=False, default = False),
    Column("clearCount", Integer, nullable=False, default = 0),
    Column("composer", JSON, nullable=False, default='[]'),
    Column("clear", JSON, nullable=False, default='[]'),
    Column("piano", JSON, nullable=False, default='[]'),
    Column("tour", JSON, nullable=False, default='[]'),
    Column("item", JSON, nullable=False, default='[]'),
    Column("mail", JSON, nullable=False, default='[]'),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("userid", String(32), unique=True, nullable=False),
    Column("session", String(256), unique=True, nullable=False)
)

result = Table(
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
    Column("updatedAt", DateTime, default=datetime.datetime.utcnow),
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