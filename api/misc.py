import secrets
import math

from api.templates import PATTERN_DATA, PIANO_DATA, PIANO_UPGRADE_DATA
from api.database import database, results

def generate_random_string(length: int) -> str:
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(length))

def get_user_level(user):
    level = 0
    for composer in user["composer"]:
        level += composer["stat"]

    return level

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

    # total star count for difficulty TODO

    query = results.select().where(results.c.owner == user["id"])
    user_results = await database.fetch_all(query)

    normal_stars = 0
    tech_stars = 0
    master_stars = 0

    # Add the results to result_object
    for i, result in enumerate(user_results, start=0):
        pattern = next((pattern for pattern in PATTERN_DATA if pattern["c"] == result["patternId"]), None)
        if pattern['pty'] == 1 and pattern['master']:
            master_stars += pattern['star']
        elif pattern['pty'] == 1:
            tech_stars += pattern['star']
        elif pattern['pty'] == 0:
            normal_stars += pattern['star']

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

    if play_session['stageId'] == 612 and difficulty == 1 and play_session['maxCombo'] == 1143:
        target.append(400030)

    if play_session['stageId'] == 822 and difficulty == 1 and speed == 3 and fade == 2:
        target.append(400031)

    # Check if the target is already unlocked

    real_target = []

    for target_piano in target:
        piano_object = next((piano for piano in user['piano'] if piano["pianoId"] == target_piano), None)

        if piano_object == None:
            real_target.append(target_piano)

    return real_target