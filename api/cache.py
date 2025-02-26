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
import datetime
import asyncio
from threading import Lock
import math
import random

from api.crypt import decrypt
from api.templates import START_TOUR_STATUS, TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA
from api.database import database, results

# ------------------------------------------
# Init

DB_NAME = "leaderboard.db"
DB_PATH = os.path.join(os.getcwd(), DB_NAME)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

cache_database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

tour_cache = Table(
    "tour",
    metadata,
    Column("objectId", Integer, primary_key=True, autoincrement=True),
    Column("patternType", Integer, nullable=False),
    Column("packId", Integer, nullable=False),
    Column("master", Boolean, nullable=False),
    Column("data", JSON, nullable=False),
)
collection_cache = Table(
    "song",
    metadata,
    Column("objectId", Integer, primary_key=True, autoincrement=True),
    Column("patternId", Integer, nullable=False),
    Column("master", Boolean, nullable=False),
    Column("data", JSON, nullable=False),
)

async def init_cache_db():
    if not os.path.exists(DB_PATH):
        print("[DB] Creating new cache database:", DB_PATH)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    await engine.dispose()
    print("[DB] Cache Database initialized successfully.")

# ------------------------------------------
# Tour Leaderboard

async def get_my_tour_leaderboard_ranking(owner, packId, patternType, isMaster):
    query = select([tour_cache]).where(tour_cache.c.packId == packId, tour_cache.c.patternType == patternType, tour_cache.c.master == isMaster)
    start_rank = 0
    new_rank = 0
    result = await database.fetch_one(query)
    if result:
        leaderboard = json.loads(result["data"])
        for index, entry in enumerate(leaderboard):
            if entry["owner"] == owner:
                start_rank = index + 1  # Rankings are 1-based

    new_lb = await generate_tour_leaderboard(packId, patternType, isMaster)

    # here
    for index, entry in enumerate(new_lb):
        if entry["owner"] == owner:
            new_rank = index + 1  # Rankings are 1-based

    return [start_rank, new_rank]

async def get_tour_leaderboard(packId, patternType, isMaster):
    query = select([tour_cache]).where(tour_cache.c.packId == packId, tour_cache.c.patternType == patternType, tour_cache.c.master == isMaster)
    result = await database.fetch_one(query)
    if result:
        return json.loads(result["data"])
    else:
        return await generate_tour_leaderboard(packId, patternType, isMaster)

async def generate_tour_leaderboard(packId, patternType, isMaster):
    if patternType == 0:
        isMaster = False
        stage_data = TOUR_NORMAL_STAGE_DATA
    elif patternType == 1:
        stage_data = TOUR_HARD_STAGE_DATA
    else:
        patternType = 2
        isMaster = False
        stage_data = TOUR_EASY_STAGE_DATA

    pi_list = [stage["pi"] for stage in stage_data if stage["pid"] == packId]

    query = select([results]).where(results.c.patternId.in_(pi_list), results.c.master == isMaster)
    result_entries = await database.fetch_all(query)

    owner_data = {}
    for result in result_entries:
        owner = result["owner"]
        if owner not in owner_data:
            owner_data[owner] = {
                "score": 0,
                "accuracy": 0,
                "count": 0,
                "updatedAt": result["updatedAt"]
            }
        owner_data[owner]["score"] += result["score"]
        owner_data[owner]["accuracy"] += result["accuracy"]
        owner_data[owner]["count"] += 1
        if result["updatedAt"] > owner_data[owner]["updatedAt"]:
            owner_data[owner]["updatedAt"] = result["updatedAt"]

    leaderboard = []
    for owner, data in owner_data.items():
        sum_score = data["score"]
        sum_accuracy = data["accuracy"] / data["count"]
        leaderboard.append({
            "objectId": random.randint(10000, 99999),
            "owner": owner,
            "patternType": patternType,
            "packId": packId,
            "score": sum_score,
            "accuracy": sum_accuracy,
            "updatedAt": data["updatedAt"],
            "master": isMaster
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    query = tour_cache.insert().values(data=leaderboard, patternType=patternType, packId=packId, master=isMaster)
    await database.execute(query)

    return leaderboard

# ------------------------------------------
# Play session

play_sessions = {}
lock = Lock()

def add_play_session(session_id, session_data, expiration=600):
    with lock:
        play_sessions[session_id] = {
            "data": session_data,
            "expires_at": datetime.datetime.utcnow + datetime.timedelta(seconds=expiration)
        }

# Get play session from cache
def get_play_session(session_id):
    with lock:
        session = play_sessions.get(session_id)
        if session and session["expires_at"] > datetime.datetime.utcnow:
            return session["data"]
        elif session:
            del play_sessions[session_id]
    return None

def delete_play_session(session_id):
    with lock:
        if session_id in play_sessions:
            del play_sessions[session_id]

async def cleanup_expired_sessions():
    while True:
        with lock:
            current_time = datetime.datetime.utcnow
            expired_sessions = [session_id for session_id, session in play_sessions.items() if session["expires_at"] <= current_time]
            for session_id in expired_sessions:
                del play_sessions[session_id]
        await asyncio.sleep(120)

async def start_cleanup_task():
    asyncio.create_task(cleanup_expired_sessions())

async def start_game(user, patternId, mode):
    return {}

async def complete_game(objectId, miss, fine, good, excellent, marvelous, maxCombo, isMaster):
    return {}
