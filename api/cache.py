import os
import databases
import sqlalchemy
from sqlalchemy import Table, Column, Integer, JSON
from sqlalchemy.ext.asyncio import create_async_engine
import datetime
import json
import datetime
import time
import random

from api.templates import TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, LEAGUE_SCHEDULE_DATA
from api.database import database, results, users
from api.misc import get_user_level, get_user_level, get_user_piano, get_random_score, random_public_info, all_songs_from_composer, get_user_piano, add_mail, get_rank_reward, get_league_rank

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
league_count = datetime.datetime.now().day
league_id = 1

def save_league_session():
    print("[CACHE] League Bot ranking updated.")
    with open("league_session.json", "w") as f:
        json.dump({"league_count": league_count, "league_id": league_id, "data": league_session}, f)

async def load_league_session():
    print("[CACHE] Loading league session...")
    global league_session, league_count, league_id
    with open("league_session.json", "r") as f:
        obj = json.load(f)
        league_session = obj["data"]
        league_id = obj["league_id"]
        if obj['league_count'] != datetime.datetime.now().day:
            print("[CACHE] League outdated, reloading.")
            await reset_league()
        else:
            print("[CACHE] League session loaded.")

async def reset_league():
    query = users.select()
    all_users = await database.fetch_all(query)

    for user in all_users:
        user = dict(user)

        user['daily'] = 0

        leaderboard = get_league_leaderboard(user)
        rank = get_league_rank(leaderboard, user['id'], 0)

        tier = user['league']['tier']
        if (tier == 1):
            append = "st"
        elif (tier == 2):
            append = "nd"
        elif (tier == 3):
            append = "rd"
        else:
            append = "th"

        if (rank < 4 and user['league']['tier'] <= 20):
            user['mail'] = add_mail(user['mail'], "You have been promoted in League!", "Congratulation! You ranked in the " + str(rank) + str(append) + " place in the league.\nYou have been promoted to the previous league.\nKeep pushing forward!", 7, 1, get_rank_reward(tier, 2))
            tier += 1
            
        elif (rank > 7 and user['league']['tier'] > 0):
            user['mail'] = add_mail(user['mail'], "You have been demoted in League!", "Unfortunately, you ranked in the " + str(rank) + "th place in the league.\nYou have been demoted to the previous league.\nBetter luck next time!", 7, 2, 10)
            tier -= 1

        else:
            user['mail'] = add_mail(user['mail'], "you stayed in the same League!", "You ranked in the " + str(rank) + str(append) + " place in the league.\nYour league has remained consistent.\nKeep it going!", 7, 1, get_rank_reward(tier, 1))

        query = users.update().where(users.c.id == user['id']).values(mail=user['mail'], daily=user['daily'])
        await database.execute(query)

    generate_league_session()

def generate_league_session():
    global league_session, league_count, league_id

    league_session = []
    league_count = datetime.datetime.now().day
    league_id += 1

    for rank in range(1, 22):
        rank_object = []
        for player in range(9):
            score1 = get_random_score(rank)
            score2 = get_random_score(rank)
            score3 = get_random_score(rank)

            schedule = next((sched for sched in LEAGUE_SCHEDULE_DATA if sched["c"] == league_count), None)

            song_1 = random.choice(all_songs_from_composer(schedule['ci1']))
            song_2 = random.choice(all_songs_from_composer(schedule['ci2']))
            song_3 = random.choice(all_songs_from_composer(schedule['ci3']))

            total_score = score1 + score2 + score3
            rank_object.append({
                "objectId": random.randint(1, 999999),
                "owner": random.randint(10000000, 99999999),
                "tier": rank,
                "nextTier": None,
                "leagueId":league_id,
                "musicId1": song_1,
                "musicId2": song_2,
                "musicId3": song_3,
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
                "publicData": random_public_info(rank)
            })

        league_session.append(rank_object)

    save_league_session()

def get_league_leaderboard(user):
    user_rank_index = user['league']['tier']
    leaderboard = league_session[user_rank_index].copy()
    piano_id, piano_lvl = get_user_piano(user)

    score1 = user['league']['score1'] or 0
    score2 = user['league']['score2'] or 0
    score3 = user['league']['score3'] or 0
    leaderboard.append({
        "objectId": random.randint(1, 999999),
        "owner": user['id'],
        "tier": user['league']['tier'],
        "nextTier": None,
        "leagueId":league_id,
        "musicId1": user['league']['musicId1'],
        "musicId2": user['league']['musicId2'],
        "musicId3": user['league']['musicId3'],
        "score1": user['league']['score1'],
        "score2": user['league']['score2'],
        "score3": user['league']['score3'],
        "totalScore": score1 + score2 + score3,
        "marbleId1": user['league']['marbleId1'],
        "marbleAchieve1": user['league']['marbleAchieve1'],
        "marbleId2":user['league']['marbleId2'],
        "marbleAchieve2": user['league']['marbleAchieve2'],
        "marbleId3":user['league']['marbleId3'],
        "marbleAchieve3":user['league']['marbleAchieve3'],
        "bonusMarbleId": user['league']['bonusMarbleId'],
        "bonusMarbleAchieve": user['league']['bonusMarbleAchieve'],
        "updatedAt": user['league']['updatedAt'],
        "rewardProvide":False,
        "playCount": user['league']['playCount'],
        "publicData": {"nickname": user['nickname'], "pianoId": piano_id, "pianoLevel": piano_lvl, "level": get_user_level(user)}
    })

    leaderboard.sort(key=lambda x: x["totalScore"], reverse=True)
    return leaderboard