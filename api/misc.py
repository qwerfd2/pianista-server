import secrets
import math
import random
import time

from api.templates import PATTERN_DATA, PIANO_DATA, PIANO_UPGRADE_DATA, PUBLIC_USER_DATA, MUSIC_DATA
from api.database import database, results

def generate_random_string(length: int) -> str:
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(length))

def get_user_level(user):
    level = 0
    for composer in user["composer"]:
        level += composer["stat"]

    return level - 29

def get_user_piano_bonus(user):
    piano = next((piano for piano in user["piano"] if piano["equip"] == True), None)
    piano_data = next((data for data in PIANO_DATA if data["c"] == piano["pianoId"]), None)
    piano_upgrade_data = next((piano_upgrade for piano_upgrade in PIANO_UPGRADE_DATA if piano_upgrade["c"] == piano["level"]), None)

    piano_context = []

    score_bonus = (piano_data["od1"] + piano_upgrade_data["sc"])
    piano_context.append({"advantageType":0, "advantageValue":score_bonus})

    advantage_2 = piano_data["o2"]

    if (advantage_2 == 1): # coin
        value = (piano_data["od2"] + piano_upgrade_data["gd"])
    elif (advantage_2 == 2): # exp
        value = (piano_data["od2"] + piano_upgrade_data["ex"])
    elif (advantage_2 == 3): # life
        value = (piano_data["od2"] + piano_upgrade_data["en"])
    else: # shield
        value = (piano_data["od2"] + piano_upgrade_data["sd"])

    piano_context.append({"advantageType":advantage_2, "advantageValue":value})
    return piano_context

def get_user_piano(user):
    piano = next((piano for piano in user["piano"] if piano["equip"] == True), None)
    return piano["pianoId"], piano["level"]

def get_score(trackid, miss, fine, good, excellent, marvelous):
    pattern = next((item for item in PATTERN_DATA if item.get("c") == trackid), None)
    if pattern is None:
        return -1

    total = miss + fine + good + excellent + marvelous

    if total != pattern["tc"]:
        return -2

    ind = 1000000 / total
    score = math.floor((marvelous * ind) + (excellent * (1/3) * ind) + (good * (0.042) * ind))
    return score

def get_fc(miss, fine, good, excellent, marvelous, totalCombo):
    total = miss + fine + good + excellent + marvelous
    return totalCombo == total

def get_fc(miss, fine, good, excellent, marvelous, totalCombo):
    total = miss + fine + good + excellent + marvelous
    return totalCombo == total

def get_accuracy(miss, fine, good, excellent, marvelous):
    total = miss + fine + good + excellent + marvelous
    accuracy = ((marvelous) + (excellent * 0.75) + (good * 0.5) + (fine * 0.25)) / total
    return accuracy

def get_star(trackid, accuracy):
    pattern = next((item for item in PATTERN_DATA if item.get("c") == trackid), None)
    if pattern is None:
        return -1

    if pattern["pty"] == 1: # hard
        if accuracy >= 0.96:
            return 5
        elif accuracy >= 0.93:
            return 4
        elif accuracy >= 0.72:
            return 3
        elif accuracy >= 0.51:
            return 2
        elif accuracy >= 0.20:
            return 1
        else:
            return 0
    else: # else
        if accuracy >= 0.90:
            return 5
        elif accuracy >= 0.80:
            return 4
        elif accuracy >= 0.70:
            return 3
        elif accuracy >= 0.60:
            return 2
        elif accuracy >= 0.50:
            return 1
        else:
            return 0
        
async def get_piano_unlock(user, play_session, difficulty, is_master, is_challenge_done, speed, fade):

    tour_piano = [[[10,400001], [20,400002], [30,400003], [40,400004], [50,400005]], # normal
                  [[10,400007], [20,400008], [30,400009], [40,400010], [50,400011]], # tech
                  [[10,400013], [20,400014], [30,400015], [40,400016], [50,400017]]] # master

    # check tour unlocks
    target = []

    if play_session['stageId'] <= 50:
        if (play_session['stageId'] % 10 == 0):
            if (difficulty == 1 and is_master):
                if (is_challenge_done):
                    piano_catalog = tour_piano[2]
                    for piano in piano_catalog:
                        if piano[0] == play_session['stageId']:
                            target.append(piano[1])

            else:
                if (is_challenge_done):
                    if (difficulty == 1):
                        # unlock tech difficulty 
                        piano_catalog = tour_piano[1]
                        for piano in piano_catalog:
                            if piano[0] == play_session['stageId']:
                                target.append(piano[1])
                    if (difficulty >= 0):
                        # unlock normal difficulty
                        piano_catalog = tour_piano[0]
                        for piano in piano_catalog:
                            if piano[0] == play_session['stageId']:
                                target.append(piano[1])
    
    # Check play count unlocked pianos
    play_count_piano = [[30,400019], [150,400020], [300,400021], [500,400022], [900,400023]]

    for piano in play_count_piano:
        if user['clearCount'] >= piano[0]:
            target.append(piano[1])

    # total star count for difficulty
    query = results.select().where(results.c.owner == user["id"])
    user_results = await database.fetch_all(query)

    normal_stars = 0
    tech_stars = 0
    master_stars = 0

    # Add the results to result_object
    for i, result in enumerate(user_results, start=0):
        pattern = next((pattern for pattern in PATTERN_DATA if pattern["c"] == result["patternId"]), None)
        if pattern['pty'] == 1 and result['master']:
            master_stars += result['star']
        elif pattern['pty'] == 1:
            tech_stars += result['star']
        elif pattern['pty'] == 0:
            normal_stars += result['star']

    if normal_stars >= 250:
        target.append(400024)
    
    if tech_stars >= 250:
        target.append(400025)

    if master_stars >= 250:
        target.append(400026)

    # check total piano count
    if len(user['piano']) >= 18:
        target.append(400027)

    if len(user['piano']) >= 27:
        target.append(400028)

    # check special piano
    if play_session['stageId'] == 822 and difficulty == 1 and play_session['maxCombo'] == 1143:
        target.append(400031)

    if play_session['stageId'] == 612 and difficulty == 1 and speed == 3 and fade == 1:
        target.append(400030)

    # Check if the target is already unlocked
    real_target = []

    for target_piano in target:
        piano_object = next((piano for piano in user['piano'] if piano["pianoId"] == target_piano), None)

        if piano_object == None:
            real_target.append(target_piano)

    return real_target

def get_random_score(rank):
    config = [[100000,680000], [150000,700000], [200000,720000], [250000,740000], [300000,760000], [350000,780000], [400000,800000], [450000,820000], [500000,840000], [550000,860000], [600000,880000], [650000,900000], [700000,920000], [750000,940000], [800000,960000], [850000,980000], [900000,1000000], [950000,1100000], [1000000,1200000], [1050000,1300000], [1100000,1310000]]

    rank -= 1
    min_score, max_score = config[rank]
    random_score = random.randint(min_score, max_score)
    return random_score

def get_rank_reward(rank, status):
    rank += 1
    config = [0,1,2,3,4,6,8,10,12,15,18,21,24,28,32,36,40,45,50,56,62,68]
    if status == 0:
        return 0
    elif status == 1:
        return config[rank - 1]
    else:
        return config[rank]
    
def add_mail(mail_object, subject, description, expire_days, item, amount):
    mail_object.append({
        "objectId": len(mail_object) + 1,
        "subject": subject,
        "description": description,
        "expire": int((time.time() + (expire_days * 86400)) * 1000),
        "status": 0,
        "item": item,
        "quantity": amount
    })
    return mail_object

def random_public_info(rank):

    piano_random = [[0,0],[1,3],[1,5],[1,7],[2,9],[3,11],[4,13],[6,15],[8,17],[10,19],[12,21],[14,23],[16,25],[18,27],[20,29],[22,30],[24,30],[26,30],[27,30],[28,30],[29,30],[30,30]]

    level_random = [[0,0],[1,50],[5,100],[10,150],[20,190],[30,230],[50,270],[70,310],[90,340],[110,370],[140,390],[170,420],[200,450],[240,470],[280,490],[320,510],[360,530],[400,550],[440,570],[480,590],[520,600],[560,600]]

    info = random.choice(PUBLIC_USER_DATA)

    piano_level = random.randint(piano_random[rank][0], piano_random[rank][1])

    user_level = random.randint(level_random[rank][0], level_random[rank][1])

    return {"nickname":info['n'],"pianoId":info['p'],"pianoLevel":piano_level,"level":user_level}

def all_songs_from_composer(cps):
    songs = []
    for song in MUSIC_DATA:
        if song['cps'] == cps:
            songs.append(song['c'])
    return songs

def get_end_of_day():
    now = time.time()
    end_of_day = time.mktime(time.localtime(now)[:3] + (23, 59, 59, 0, 0, -1))
    return int(end_of_day * 1000)

def get_league_rank(leaderboard, user_id, type):
    rank = 0
    sort_order = ["", "score1", "score2", "score3"]
    if type:
        leaderboard.sort(key=lambda x: x[sort_order[type]], reverse=True)

    for participant in leaderboard:
        rank += 1
        if participant['owner'] == user_id:
            break

    return rank

def add_feed(user, id, param1, league_id):
    args_object = []
    if param1:
        args_object.append(param1)

    user['league']['feed'].append({"objectId":len(user['league']['feed']) + 1,"createdAt":int(time.time() * 1000),"leagueId":league_id,"userObjectId":user["id"], 'feedId': id, "args": args_object})
    return user