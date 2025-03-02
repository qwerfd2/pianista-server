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
import time
import random

from api.crypt import decrypt
from api.templates import START_TOUR_STATUS, TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, PATTERN_DATA, MUSIC_DATA, COMPOSER_STAT_DATA
from api.database import database, results, users
from api.misc import get_score, get_accuracy, get_star, get_fc, get_user_level, get_user_piano_bonus, get_fc

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
    query = tour_cache.select().where(tour_cache.c.packId == packId, tour_cache.c.patternType == patternType)
    start_rank = 0
    new_rank = 0
    result = await cache_database.fetch_one(query)
    if result:
        leaderboard = result["data"]
        for index, entry in enumerate(leaderboard):
            if entry["owner"] == owner:
                start_rank = index + 1  # Rankings are 1-based

    new_lb = await generate_tour_leaderboard(packId, patternType)

    # here
    for index, entry in enumerate(new_lb):
        if entry["owner"] == owner:
            new_rank = index + 1  # Rankings are 1-based

    return start_rank, new_rank

async def get_tour_leaderboard(packId, patternType):
    query = tour_cache.select().where(tour_cache.c.packId == packId, tour_cache.c.patternType == patternType)
    result = await cache_database.fetch_one(query)
    if result:
        return result["data"]
    else:
        return await generate_tour_leaderboard(packId, patternType)

async def generate_tour_leaderboard(packId, patternType):
    if patternType == 0:
        stage_data = TOUR_NORMAL_STAGE_DATA
    elif patternType == 1:
        stage_data = TOUR_HARD_STAGE_DATA
    else:
        patternType = 2
        stage_data = TOUR_EASY_STAGE_DATA

    pi_list = [stage["pi"] for stage in stage_data if stage["pid"] == packId]

    query = results.select().where(results.c.patternId.in_(pi_list))
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
            "objectId": random.randint(1, 99999999),
            "owner": owner,
            "patternType": patternType,
            "packId": packId,
            "score": sum_score,
            "accuracy": sum_accuracy,
            "updatedAt": data["updatedAt"]
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    query = tour_cache.insert().values(data=leaderboard, patternType=patternType, packId=packId)
    await cache_database.execute(query)

    print(leaderboard)

    return leaderboard

# ------------------------------------------
# Play session

play_sessions = {}
lock = Lock()

def save_play_session():
    with open("play_sessions.json", "w") as f:
        json.dump(play_sessions, f)

def load_play_session():
    print("[CACHE] Loading play sessions...")
    with lock:
        global play_sessions
        with open("play_sessions.json", "r") as f:
            play_sessions = json.load(f)
            print("[CACHE] Play sessions loaded.")

def add_play_session(session_id, session_data, expiration=6000000):
    
    with lock:
        global play_sessions
        play_sessions[str(session_id)] = {
            "data": session_data,
            "expires_at": int(time.time() * 1000) + expiration
        }
        print("called")
        save_play_session()


# Get play session from cache
def get_play_session(session_id):
    with lock:
        global play_sessions
        session = play_sessions.get(str(session_id))
        if session:
            return session["data"]

    return None

def delete_play_session(session_id):
    with lock:
        global play_sessions
        if session_id in play_sessions:
            del play_sessions[str(session_id)]
            save_play_session()

async def cleanup_expired_sessions():
    while True:
        global play_sessions
        with lock:
            current_time = int(time.time() * 1000)
            expired_sessions = [session_id for session_id, session in play_sessions.items() if session["expires_at"] <= current_time]
            for session_id in expired_sessions:
                del play_sessions[str(session_id)]
        save_play_session()
        await asyncio.sleep(120)

async def start_cleanup_task():
    asyncio.create_task(cleanup_expired_sessions())

async def start_game(user, patternId, mode, var1, var2):
    obj = {
            "objectId": random.randint(1, 99999999),
            "owner": user["id"],
            "patternId": patternId,
            "type": 1,
            "exp": None,
            "expContext": None,
            "goldContext": None,
            "pianoContext": [],
            "score": None,
            "statScore": None,
            "pianoScore": None,
            "star": None,
            "accuracy": None,
            "maxCombo": None,
            "takeGold": None,
            "allCombo": None,
            "miss": None,
            "tier1": None,
            "tier2": None,
            "tier3": None,
            "tier4": None,
            "status": 0,
            "startAt": int(time.time() * 1000),
            "endAt": None
        }
    if mode == 0:
        obj["type"] = var1
        obj["stageId"] = var2

    add_play_session(obj["objectId"], obj)

    return obj

async def complete_game(mode, user, objectId, miss, fine, good, excellent, marvelous, maxCombo, speed, fade, isMaster):
    return_obj = get_play_session(objectId)
    if return_obj == None:
        return {"code": -400}
    
    pattern = next((pattern for pattern in PATTERN_DATA if pattern["c"] == return_obj["patternId"]), None)
    musicID = pattern["m"]

    music = next((music for music in MUSIC_DATA if music["c"] == musicID), None)
    composerID = music["cps"]
    curComposer = {}
    for composer in user["composer"]:
        if composer["composerId"] == composerID:
            curComposer = composer
            break
    
    orig_score = get_score(return_obj["patternId"], miss, fine, good, excellent, marvelous)
    pianoContext = get_user_piano_bonus(user)
    pianoScore = next((context["advantageValue"] for context in pianoContext if context["advantageType"] == 0), 0)
    statScore = math.floor(curComposer['stat'] * 0.001 * orig_score)
    accuracy = get_accuracy(miss, fine, good, excellent, marvelous)
    return_obj["accuracy"] = accuracy
    return_obj["pianoScore"] = pianoScore
    starCount = get_star(return_obj["patternId"], accuracy)
    return_obj["statScore"] = statScore
    return_obj["score"] = math.floor(orig_score + statScore + pianoScore)
    
    totalEXP = 0
    expContext = []



    if pattern["pty"] == 0: # normal
        base = 50
    elif pattern["pty"] == 1: # technical
        base = 70
    else:
        base = 30
    expContext.append([6002002, base])
    totalEXP += base
    if (starCount == 5): # 5 star bonus
        expContext.append([6002003, 20])
        totalEXP += 20

    if (accuracy >= 0.99): # technical bonus
        expContext.append([6002004, 20])
        totalEXP += 20
    if (fade):
        expContext.append([6002005, 10])
        totalEXP += 10

    expBoost = next((context["advantageValue"] for context in pianoContext if context["advantageType"] == 2), 0)
    expContext.append([6002006, expBoost])
    totalEXP += expBoost
    levelBoost = math.floor(curComposer["stat"] * 0.01 * totalEXP)
    expContext.append([6003003, levelBoost])
    expContext.append([6002007, totalEXP])
    totalEXP += totalEXP
    totalEXP += levelBoost

    takeGold = 0
    goldContext = []

    if pattern["pty"] == 0: # normal
        base = 50
    elif pattern["pty"] == 1: # technical
        base = 70
    else:
        base = 30
    goldContext.append([6002002, base])
    takeGold += base
    if (starCount == 5): # 5 star bonus
        goldContext.append([6002003, 20])
        takeGold += 20

    if (accuracy >= 0.99): # technical bonus
        goldContext.append([6002004, 20])
        takeGold += 20

    goldBoost = next((context["advantageValue"] for context in pianoContext if context["advantageType"] == 2), 0)
    goldContext.append([6003003, goldBoost])
    takeGold += goldBoost
    
    goldContext.append([6003003, levelBoost])
    goldContext.append([6002007, takeGold])
    takeGold += takeGold
    takeGold += levelBoost
    return_obj["goldContext"] = goldContext
    return_obj["takeGold"] = takeGold
    
    return_obj["allCombo"] = get_fc(miss, fine, good, excellent, marvelous, maxCombo)
    return_obj["exp"] = totalEXP
    return_obj["expContext"] = expContext
    return_obj["pianoContext"] = pianoContext
    return_obj["star"] = starCount
    return_obj["maxCombo"] = maxCombo
    return_obj["miss"] = miss
    return_obj["tier1"] = fine
    return_obj["tier2"] = good
    return_obj["tier3"] = excellent
    return_obj["tier4"] = marvelous
    return_obj["status"] = 1
    return_obj["endAt"] = int(time.time() * 1000)

    query = results.select().where(results.c.owner == user["id"], results.c.patternId == return_obj["patternId"])
    existing_result = await database.fetch_one(query)

    if existing_result:
        if return_obj["score"] > existing_result["score"]:
            query = results.update().where(results.c.id == existing_result["id"]).values(
                score=return_obj["score"],
                star=starCount,
                accuracy=accuracy,
                maxCombo=maxCombo,
                allCombo=return_obj["allCombo"],
                updatedAt=int(time.time() * 1000),
                master=isMaster
            )
            await database.execute(query)
    else:
        query = results.insert().values(
            owner=user["id"],
            patternId=return_obj["patternId"],
            score=return_obj["score"],
            star=starCount,
            accuracy=accuracy,
            maxCombo=maxCombo,
            allCombo=return_obj["allCombo"],
            updatedAt=int(time.time() * 1000),
            master=isMaster
        )
        await database.execute(query)
    
    print(user['gold'], takeGold)
    user = dict(user)
    user['gold'] += takeGold

    for composer in user["composer"]:
        if composer['composerId'] == composerID:
            if (composer['stat'] < 20):
                composer['exp'] += totalEXP
                if composer['exp'] >= COMPOSER_STAT_DATA[composer['stat'] + 1]['e']:
                    composer['stat'] += 1
                    composer['exp'] -= COMPOSER_STAT_DATA[composer['stat'] + 1]['e']
                break

    curComposer['exp'] += totalEXP

    query = users.update().where(users.c.id == user["id"]).values(
        gold=user["gold"],
        composer=user["composer"]
    )
    await database.execute(query)

    delete_play_session(objectId)

    return return_obj
