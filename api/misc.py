import secrets
import math

from api.templates import PATTERN_DATA

def generate_random_string(length: int) -> str:
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(int))

def get_score(trackid, miss, fine, good, excellent, marvelous):

    pattern = next((item for item in PATTERN_DATA if item.get("c") == trackid), None)
    if pattern is None:
        return -1

    total = miss + fine + good + excellent + marvelous

    if total != pattern["tc"]:
        return -2

    ind = 1000000 / total
    score = math.floor((marvelous * ind) + (excellent * (1 / 3) * ind) + (good * (1 / 10) * ind))
    return score

def get_accuracy(miss, fine, good, excellent, marvelous):
    total = miss + fine + good + excellent + marvelous
    accuracy = (marvelous) + (excellent * 0.75) + (good * 0.5) + (fine * 0.25) / total
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