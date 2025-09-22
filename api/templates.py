import json
import os

from sqlalchemy import true

MUSIC_DATA = []
PATTERN_DATA = []
PIANO_DATA = []
PIANO_UPGRADE_DATA = []
STORE_GAME_ITEM_DATA = []
STORE_GOLD_DATA = []
STORE_TICKET_DATA = []
TOUR_EASY_STAGE_DATA = []
TOUR_NORMAL_STAGE_DATA = []
TOUR_HARD_STAGE_DATA = []
TOUR_MASTER_STAGE_DATA = []
COMPOSER_STAT_DATA = []
ITEM_DATA = []
PUBLIC_USER_DATA = []
LEAGUE_SCHEDULE_DATA = []
LOCALIZATION_DATA = []
MARBLE_DATA = []
RESET_DATA = []
TOUR_PACK_DATA = []
GAME_CONFIG_DATA = []

FULL_TOUR_STATUS = []
FULL_COLLECTION_STATUS = []
FULL_PIANO_STATUS = []

START_TOUR_STATUS = []
START_COMPOSER_STATUS = []
START_COLLECTION_STATUS = []
START_PIANO_STATUS = []
START_MAIL = []
START_LEAGUE = {"leagueId":1, "endAt":0,"tier":0,"musicId1":None,"score1":None,"patternId1": None,"musicId2":None,"score2":None,"patternId2": None,"musicId3":None,"score3":None,"marbleId1":3,"patternId3": None,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":0,"playCount":0,"leaderboardCache":[],"feed":[]}

def init_templates():
    global MUSIC_DATA, PATTERN_DATA, PIANO_DATA, PIANO_UPGRADE_DATA, STORE_GAME_ITEM_DATA, STORE_GOLD_DATA, STORE_TICKET_DATA, TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, TOUR_MASTER_STAGE_DATA, COMPOSER_STAT_DATA, ITEM_DATA, PUBLIC_USER_DATA, LEAGUE_SCHEDULE_DATA, LOCALIZATION_DATA, MARBLE_DATA, RESET_DATA, TOUR_PACK_DATA, GAME_CONFIG_DATA
    global START_TOUR_STATUS, START_COMPOSER_STATUS, START_COLLECTION_STATUS, START_PIANO_STATUS, START_MAIL
    global FULL_TOUR_STATUS, FULL_COLLECTION_STATUS, FULL_PIANO_STATUS
    
    base_path = 'data/client/common/1'
    start_base_path = 'start'
    print("[TEMPLATES] Initializing templates...")

    try:
        with open(os.path.join(base_path, 'musicdata.json'), 'r', encoding='utf-8') as f:
            MUSIC_DATA = json.load(f)

        with open(os.path.join(base_path, 'patterndata.json'), 'r', encoding='utf-8') as f:
            PATTERN_DATA = json.load(f)

        with open(os.path.join(base_path, 'pianodata.json'), 'r', encoding='utf-8') as f:
            PIANO_DATA = json.load(f)

        with open(os.path.join(base_path, 'pianoupgradedata.json'), 'r', encoding='utf-8') as f:
            PIANO_UPGRADE_DATA = json.load(f)

        with open(os.path.join(base_path, 'storegameitemdata.json'), 'r', encoding='utf-8') as f:
            STORE_GAME_ITEM_DATA = json.load(f)

        with open(os.path.join(base_path, 'storegolddata.json'), 'r', encoding='utf-8') as f:
            STORE_GOLD_DATA = json.load(f)

        with open(os.path.join(base_path, 'storeticketdata.json'), 'r', encoding='utf-8') as f:
            STORE_TICKET_DATA = json.load(f)

        with open(os.path.join(base_path, 'toureasystagedata.json'), 'r', encoding='utf-8') as f:
            TOUR_EASY_STAGE_DATA = json.load(f)

        with open(os.path.join(base_path, 'tournormalstagedata.json'), 'r', encoding='utf-8') as f:
            TOUR_NORMAL_STAGE_DATA = json.load(f)

        with open(os.path.join(base_path, 'tourhardstagedata.json'), 'r', encoding='utf-8') as f:
            TOUR_HARD_STAGE_DATA = json.load(f)

        with open(os.path.join(base_path, 'tourmasterstagedata.json'), 'r', encoding='utf-8') as f:
            TOUR_MASTER_STAGE_DATA = json.load(f)

        with open(os.path.join(base_path, 'composerstatdata.json'), 'r', encoding='utf-8') as f:
            COMPOSER_STAT_DATA = json.load(f)

        with open(os.path.join(base_path, 'itemdata.json'), 'r', encoding='utf-8') as f:
            ITEM_DATA = json.load(f)
            
        with open(os.path.join(base_path, 'publicuserdata.json'), 'r', encoding='utf-8') as f:
            PUBLIC_USER_DATA = json.load(f)

        with open(os.path.join(base_path, 'leaguescheduledata.json'), 'r', encoding='utf-8') as f:
            LEAGUE_SCHEDULE_DATA = json.load(f)

        with open(os.path.join(base_path, 'localeendata.json'), 'r', encoding='utf-8') as f:
            LOCALIZATION_DATA = json.load(f)

        with open(os.path.join(base_path, 'marbledata.json'), 'r', encoding='utf-8') as f:
            MARBLE_DATA = json.load(f)

        with open(os.path.join(base_path, 'resetdata.json'), 'r', encoding='utf-8') as f:
            RESET_DATA = json.load(f)

        with open(os.path.join(base_path, 'tourpackdata.json'), 'r', encoding='utf-8') as f:
            TOUR_PACK_DATA = json.load(f)

        with open(os.path.join(base_path, 'gameconfigdata.json'), 'r', encoding='utf-8') as f:
            GAME_CONFIG_DATA = json.load(f)

        with open(os.path.join(start_base_path, 'start_tour_status.json'), 'r', encoding='utf-8') as f:
            START_TOUR_STATUS = json.load(f)

        with open(os.path.join(start_base_path, 'start_composer_status.json'), 'r', encoding='utf-8') as f:
            START_COMPOSER_STATUS = json.load(f)

        with open(os.path.join(start_base_path, 'start_collection_status.json'), 'r', encoding='utf-8') as f:
            START_COLLECTION_STATUS = json.load(f)

        with open(os.path.join(start_base_path, 'start_piano_status.json'), 'r', encoding='utf-8') as f:
            START_PIANO_STATUS = json.load(f)

        with open(os.path.join(start_base_path, 'start_mail.json'), 'r', encoding='utf-8') as f:
            START_MAIL = json.load(f)

        for item in ITEM_DATA:
            if item['ct'] == 3: # patterns
                FULL_COLLECTION_STATUS.append({
                    "patternId": item['c'],
                    "clear": False
                })

        for piano in PIANO_DATA:
            FULL_PIANO_STATUS.append({
                "pianoId": piano['c'],
                "level": 30,
                "equip": False
            })
        FULL_PIANO_STATUS[0]['equip'] = True

        for tour in TOUR_PACK_DATA:
            FULL_TOUR_STATUS.append({
                "packId": tour['c'],
                "unlocked": True,
                "easyLastStage": 0,
                "normalLastStage": 0,
                "hardLastStage": 0,
                "masterLastStage": 0,
                "totalClearStage": 0
            })

        print("[TEMPLATES] Templates initialized successfully.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")