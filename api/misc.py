import secrets
import math

from api.templates import PATTERN_DATA, PIANO_DATA, PIANO_UPGRADE_DATA

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