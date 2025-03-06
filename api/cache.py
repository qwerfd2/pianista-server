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
from api.templates import START_TOUR_STATUS, TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, TOUR_MASTER_STAGE_DATA, PATTERN_DATA, MUSIC_DATA, COMPOSER_STAT_DATA, STORE_GAME_ITEM_DATA
from api.database import database, results, users
from api.misc import get_score, get_accuracy, get_star, get_fc, get_user_level, get_user_piano_bonus, get_fc, get_user_level, get_user_piano, get_piano_unlock, get_random_score

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

async def get_user_public_data(user_id):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)

    user_level = get_user_level(user)
    pianoId, piano_level = get_user_piano(user)

    return {
        "nickname": user["nickname"],
        "pianoId": pianoId,
        "pianoLevel": piano_level,
        "level": user_level,
    }

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
            "updatedAt": data["updatedAt"],
            "publicData": await get_user_public_data(owner),
            "master": False
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    query = tour_cache.insert().values(data=leaderboard, patternType=patternType, packId=packId)
    await cache_database.execute(query)

    print(leaderboard)

    return leaderboard


# ------------------------------------------
# Collection Leaderboard
async def get_my_collection_leaderboard_ranking(owner, patternId, isMaster):
    query = collection_cache.select().where(collection_cache.c.patternId == patternId)
    start_rank = 0
    new_rank = 0
    result = await cache_database.fetch_one(query)
    if result:
        leaderboard = result["data"]
        for index, entry in enumerate(leaderboard):
            if entry["owner"] == owner:
                start_rank = index + 1  # Rankings are 1-based

    new_lb = await generate_collection_leaderboard(patternId)

    # here
    for index, entry in enumerate(new_lb):
        if entry["owner"] == owner:
            new_rank = index + 1  # Rankings are 1-based

    return start_rank, new_rank

async def get_collection_leaderboard(patternId):
    query = collection_cache.select().where(collection_cache.c.patternId == patternId)
    result = await cache_database.fetch_one(query)
    if result:
        return result["data"]
    else:
        return await generate_collection_leaderboard(patternId)

async def generate_collection_leaderboard(patternId):

    query = results.select().where(results.c.patternId == patternId)
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
            "patternId": patternId,
            "score": sum_score,
            "accuracy": sum_accuracy,
            "updatedAt": data["updatedAt"],
            "publicData": await get_user_public_data(owner),
            "master": False
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    query = collection_cache.insert().values(data=leaderboard, patternId=patternId)
    await cache_database.execute(query)

    return leaderboard

# ------------------------------------------
# League Data

league_session = []
league_end = 0
league_count = 1

def save_league_session():
    print("[CACHE] League Bot ranking updated.")
    with open("league_session.json", "w") as f:
        json.dump({"end_at": league_end, "league_count": league_count, "data": league_session}, f)

def load_league_session():
    print("[CACHE] Loading league session...")
    with lock:
        global league_session, league_end, league_count
        with open("league_session.json", "r") as f:
            obj = json.load(f)
            league_session = obj["data"]
            league_count = obj["league_count"]
            league_end = obj["end_at"]
            print("[CACHE] League session loaded.")

def generate_league_session():
    league_session = []
    for rank in range(1, 22):
        rank_object = []
        for player in range(9):
            score1 = get_random_score(rank)
            score2 = get_random_score(rank)
            score3 = get_random_score(rank)
            total_score = score1 + score2 + score3
            rank_object.append({
                "objectId": random.randint(1, 999999),
                "owner": math.random.randint(10000000, 99999999),
                "tier": rank,
                "nextTier": None,
                "leagueId":9999999,
                "musicId1": 1,
                "musicId2": 1,
                "musicId3": 1,
                "score1": score1,
                "score2": score2,
                "score3": score3,
                "totalScore": total_score,
                "marbleId1":3,
                "marbleAchieve1":False,
                "marbleId2":4,
                "marbleAchieve2":False,
                "marbleId3":5,
                "marbleAchieve3":False,
                "bonusMarbleId":2,
                "bonusMarbleAchieve":False,
                "updatedAt":int(time.time() * 1000),
                "rewardProvide":False,
                "playCount":0,

            })
        league_session.append(rank_object)
    
    save_league_session()

def get_league_leaderboard():
    return True
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

async def start_game(user, patternId, mode, master, items, var1, var2):
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
            "master": master,
            "startAt": int(time.time() * 1000),
            "endAt": None
        }
    if mode == 0:
        obj["type"] = var1
        obj["stageId"] = var2
    else:
        obj["stageId"] = var1

    user = dict(user)
    cost = 0
    for item_code in items:
        print("item code", item_code)
        print("item found", item_code)
        found = False
        # Check if the user owns the item
        for user_item in user["item"]:
            if user_item["itemId"] == item_code:
                # Reduce quantity by 1
                print("found in user items")
                found = True
                user_item["quantity"] -= 1
                if user_item["quantity"] <= 0:
                    user['item'].remove(user_item)
        if not found:
            # Only support coins (why would you need to buy with gem?)
            item = next((item for item in STORE_GAME_ITEM_DATA if item["c"] == item_code), None)
            if item:
                cost += item["p"]

    if cost:
        user['gold'] -= cost

    query = users.update().where(users.c.id == user["id"]).values(
        gold=user["gold"],
        item=user["item"]
    )
    await database.execute(query)

    add_play_session(obj["objectId"], obj)

    return obj

async def complete_game(mode, user, objectId, miss, fine, good, excellent, marvelous, maxCombo, speed, fade, smth):
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
    if (orig_score < 0):
        return {"code": orig_score}
    
    orig_score = math.floor(orig_score)
    pianoContext = get_user_piano_bonus(user)
    pianoScore = next((context["advantageValue"] for context in pianoContext if context["advantageType"] == 0), 0)
    statScore = math.floor(curComposer['stat'] * 0.001 * orig_score)
    pianoScore = math.floor(pianoScore)
    accuracy = get_accuracy(miss, fine, good, excellent, marvelous)
    return_obj["accuracy"] = accuracy
    return_obj["pianoScore"] = pianoScore
    starCount = get_star(return_obj["patternId"], accuracy)
    return_obj["statScore"] = statScore
    return_obj["score"] = orig_score + statScore + pianoScore
    
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

    pity_give = False

    user = dict(user)

    is_challenge_done = True
    isMaster = return_obj["type"] == 2

    if mode == 0:
        tour_award_gold = 0
        tour_award_gem = 0
        
        if isMaster:
            data_object = next((obj for obj in TOUR_MASTER_STAGE_DATA if obj["pi"] == return_obj["patternId"]), None)
            
            if (miss > data_object['mv1']):
                is_challenge_done = False
            if (data_object['mt2'] == 1 and maxCombo < data_object['mv2']):
                is_challenge_done = False
            if (data_object['mt2'] == 3 and return_obj["score"] < data_object['mv2']):
                is_challenge_done = False

            if data_object and is_challenge_done:
                tour_award_gold = data_object["gr"] if data_object["gr"] else 0
                tour_award_gem = data_object["jr"] if data_object["jr"] else 0
                is_challenge_done = False
                # Increment tour clear count

                for tour in user["tour"]:
                    if tour["packId"] == data_object['pid']:
                        if tour['masterLastStage'] < data_object['s']:
                            tour['masterLastStage'] = data_object['s']
                            tour["totalClearStage"] = data_object['s']
                            break

                user_tour_object = next((tour for tour in user["tour"] if tour["packId"] == data_object['pid']), None)
                data_object['pid']

            elif is_challenge_done != True:
                pity_give = True
        else:
            do_easy = True
            do_normal = False
            do_hard = True
            if pattern["pty"] == 0:
                do_normal = True
                use_data = TOUR_NORMAL_STAGE_DATA
            elif pattern["pty"] == 1:
                do_normal = True
                do_hard = True
                use_data = TOUR_HARD_STAGE_DATA
            else:
                use_data = TOUR_EASY_STAGE_DATA

            data_object = next((obj for obj in use_data if obj["pi"] == return_obj["patternId"]), None)

            if 'mv1' in data_object and data_object['mv1'] is not None:
                if miss > data_object['mv1']:
                    is_challenge_done = False
            if 'mt2' in data_object and data_object['mt2'] is not None and 'mv2' in data_object and data_object['mv2']:
                if (data_object['mt2'] == 1 and maxCombo < data_object['mv2']):
                    is_challenge_done = False
                if (data_object['mt2'] == 3 and return_obj["score"] < data_object['mv2']):
                    is_challenge_done = False

            if data_object and is_challenge_done:

                tour_award_gold = data_object["gr"] if data_object["gr"] else 0
                tour_award_gem = data_object["jr"] if data_object["jr"] else 0

                if do_hard:
                    data_object = next((obj for obj in TOUR_HARD_STAGE_DATA if obj["pi"] == return_obj["patternId"]), None)
                    if data_object:
                        tour_award_gold = data_object["gr"] if data_object["gr"] else 0
                        tour_award_gem = data_object["jr"] if data_object["jr"] else 0
                if do_normal:
                    data_object = next((obj for obj in TOUR_NORMAL_STAGE_DATA if obj["pi"] == return_obj["patternId"]), None)
                    if data_object:
                        tour_award_gold = data_object["gr"] if data_object["gr"] else 0
                        tour_award_gem = data_object["jr"] if data_object["jr"] else 0
    
    if pity_give or mode != 0:
        if pattern["pty"] == 0: # normal
            base = 50
        elif pattern["pty"] == 1 or pity_give: # technical / master fail
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

    # Update/add best score to results table

    query = results.select().where(results.c.owner == user["id"], results.c.patternId == return_obj["patternId"])
    existing_result = await database.fetch_one(query)

    if existing_result:
        if return_obj["score"] > existing_result["score"]:
            query = results.update().where(results.c.objectId == existing_result["objectId"]).values(
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

    # Add user gold and diamond
    
    if (mode != 0):
        user['gold'] += takeGold
    else:
        user['gold'] += tour_award_gold
        user['diamond'] += tour_award_gem

        # Set clear collection status

        for collection in user["collection"]:
            if collection['patternId'] == return_obj["patternId"]:
                if (collection['clear'] == False):
                    collection['clear'] = True
                    break

    # Increment composer level

    for composer in user["composer"]:
        if composer['composerId'] == composerID:
            if (composer['stat'] < 20):
                composer['exp'] += totalEXP
                if composer['exp'] >= COMPOSER_STAT_DATA[composer['stat'] + 1]['e']:
                    composer['stat'] += 1
                    composer['exp'] -= COMPOSER_STAT_DATA[composer['stat'] + 1]['e']
                break

    # increment user clear count

    user['clearCount'] += 1

    unlocked_piano = await get_piano_unlock(user, return_obj, pattern["pty"], isMaster, is_challenge_done, speed, fade)

    if (len(unlocked_piano)):
        for piano in unlocked_piano:
            unlock_piano_object = {
                "pianoId": piano,
                "level": 1,
                "equip": False
            }
            user['piano'].append(unlock_piano_object)

    # Update these fields

    query = users.update().where(users.c.id == user["id"]).values(
        gold=user["gold"],
        diamond=user["diamond"],
        composer=user["composer"],
        collection=user["collection"],
        tour=user["tour"],
        clearCount=user["clearCount"],
        piano=user["piano"]
    )
    await database.execute(query)

    # Keep temporary queue clean

    delete_play_session(objectId)

    return return_obj
