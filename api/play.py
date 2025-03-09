import json
import asyncio
from threading import Lock
import math
import time
import random

from api.templates import TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, TOUR_MASTER_STAGE_DATA, PATTERN_DATA, MUSIC_DATA, COMPOSER_STAT_DATA, STORE_GAME_ITEM_DATA, LEAGUE_SCHEDULE_DATA
from api.database import database, results, users
from api.misc import get_score, get_accuracy, get_star, get_fc, get_user_piano_bonus, get_fc, get_piano_unlock, add_feed
from api.cache import league_count, league_id

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
        await asyncio.sleep(240)

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
        found = False
        # Check if the user owns the item
        for user_item in user["item"]:
            if user_item["itemId"] == item_code:
                # Reduce user item quantity by 1
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

    all_combo = get_fc(miss, fine, good, excellent, marvelous, maxCombo)

    if (mode != 2):
        return_obj["score"] = orig_score + statScore + pianoScore
    else:
        difficulty_bonus = [0,2000,5000,10000,30000,60000,90000,120000,150000,180000,210000]

        accuracy_score = 0
        if accuracy >= 0.90:
            accuracy_score += 5000
        if accuracy >= 0.93:
            accuracy_score += 5000
        if accuracy >= 0.96:
            accuracy_score += 5000
        if accuracy == 1.0:
            accuracy_score += 5000

        if all_combo:
            accuracy_score += 20000

        if fade:
            accuracy_score += 10000

        difficulty_score = difficulty_bonus[pattern["d"]]

        return_obj["score"] = orig_score + statScore + pianoScore + accuracy_score + difficulty_score
    
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
    if expBoost:
        expContext.append([6002006, expBoost])
        totalEXP += expBoost
    levelBoost = math.floor(curComposer["stat"] * 0.01 * totalEXP)
    expContext.append([6003002, levelBoost])
    totalEXP += levelBoost

    user = dict(user)

    first_clear_bonus = 0
    if user['daily'] == 0:
        # first clear of the day
        first_clear_bonus = 10
        user['daily'] = 1

    if first_clear_bonus:
        expContext.append([6002001, first_clear_bonus])
        totalEXP += first_clear_bonus

    bonus = math.floor(totalEXP / 2)
    expContext.append([6002007, bonus])
    totalEXP += bonus

    takeGold = 0
    goldContext = []

    pity_give = False

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

            tour_object = next(tour for tour in user["tour"] if tour["packId"] == data_object['pid'])
            is_already_completed = False
            if tour_object['masterLastStage'] >= data_object['s']:
                is_already_completed = True

            if data_object and is_challenge_done and not is_already_completed:
                tour_award_gold = data_object["gr"] if data_object["gr"] else 0
                tour_award_gem = data_object["jr"] if data_object["jr"] else 0
                # Increment tour clear count

                for tour in user["tour"]:
                    if tour["packId"] == data_object['pid']:
                        if tour['masterLastStage'] < data_object['s']:
                            tour['masterLastStage'] = data_object['s']
                            tour["totalClearStage"] = data_object['s']
                            break

            elif data_object and (is_challenge_done != True or is_already_completed):
                pity_give = True
        else:

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

            tour_object = next(tour for tour in user["collection"] if tour["patternId"] == return_obj["patternId"])
            is_already_completed = False
            if tour_object['clear']:
                is_already_completed = True

            if data_object and is_challenge_done and not is_already_completed:

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
            elif data_object and (is_challenge_done != True or is_already_completed):
                pity_give = True
    
    if pity_give or mode != 0:
        if pattern["pty"] == 0: # normal
            base = 50
        elif pattern["pty"] == 1 or pity_give: # technical / master fail
            base = 70
        else:
            base = 30

        takeGold += base
        if (starCount == 5): # 5 star bonus
            goldContext.append([6002003, 20])
            takeGold += 20

        if (accuracy >= 0.99): # technical bonus
            goldContext.append([6002004, 20])
            takeGold += 20

        goldBoost = next((context["advantageValue"] for context in pianoContext if context["advantageType"] == 1), 0)
        if goldBoost:
            goldContext.append([6003003, goldBoost])
            takeGold += goldBoost
        
        goldContext.append([6003002, levelBoost])
        takeGold += levelBoost

        if first_clear_bonus:
            goldContext.append([6002001, first_clear_bonus])
            takeGold += first_clear_bonus

        bonus = math.floor(takeGold / 2)
        goldContext.append([6002007, bonus])
        takeGold += bonus

    return_obj["goldContext"] = goldContext
    return_obj["takeGold"] = takeGold
    
    return_obj["allCombo"] = all_combo
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
    if (mode != 2):

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

    else:
        # do league specific saving
        schedule = next((sched for sched in LEAGUE_SCHEDULE_DATA if sched["c"] == league_count), None)
        is_best = 0

        if music['cps'] == schedule['ci1']:
            if return_obj['score'] > (user['league']['score1'] or 0):
                is_best = 1
                user['league']['musicId1'] = music['c']
                user['league']['score1'] = return_obj['score']
                user['league']['patternId1'] = return_obj['patternId']
        if music['cps'] == schedule['ci2']:
            if return_obj['score'] > (user['league']['score2'] or 0):
                is_best = 2
                user['league']['musicId2'] = music['c']
                user['league']['score2'] = return_obj['score']
                user['league']['patternId2'] = return_obj['patternId']
        if music['cps'] == schedule['ci3']:
            if return_obj['score'] > (user['league']['score3'] or 0):
                is_best = 3
                user['league']['musicId3'] = music['c']
                user['league']['score3'] = return_obj['score']
                user['league']['patternId3'] = return_obj['patternId']

        user['league']['updatedAt'] = int(time.time() * 1000)
        user['league']['playCount'] += 1

        if is_best:
            field_list = ["", "score1", "score2", "score3"]
            score_list = [entry[field_list[is_best]] for entry in user['league']['leaderboardCache'] if entry[field_list[is_best]] is not None]

            if return_obj['score'] > max(score_list):
                user = add_feed(user, 5, music['cps'], league_id)

    # Add user gold and diamond
    user['gold'] += takeGold
    if (mode == 0):
        user['gold'] += tour_award_gold
        user['diamond'] += tour_award_gem

        # Set clear collection status
        chart_ids = [music['pty3']]

        if pattern["pty"] == 0:
            chart_ids.append(music['pty1'])
        elif pattern["pty"] == 1:
            chart_ids.append(music['pty1'])
            chart_ids.append(music['pty2'])

        if not isMaster:
            for collection in user["collection"]:
                if collection['patternId'] in chart_ids:
                    if not collection['clear']:
                        collection['clear'] = True

    # Increment composer level
    for composer in user["composer"]:
        if composer['composerId'] == composerID:
            if (composer['stat'] < 20):
                composer['exp'] += totalEXP
                if composer['exp'] >= COMPOSER_STAT_DATA[composer['stat'] + 1]['e']:
                    composer['exp'] -= COMPOSER_STAT_DATA[composer['stat'] + 1]['e']
                    composer['stat'] += 1
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
        piano=user["piano"],
        daily=user['daily'],
        league=user['league']
    )
    await database.execute(query)

    # Keep temporary queue clean
    delete_play_session(objectId)

    return return_obj