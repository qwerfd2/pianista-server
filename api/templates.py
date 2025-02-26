import json
import os

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

START_TOUR_STATUS = []

def init_templates():
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

        with open(os.path.join(start_base_path, 'start_tour_status.json'), 'r', encoding='utf-8') as f:
            START_TOUR_STATUS = json.load(f)

        

        print("[TEMPLATES] Templates initialized successfully.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")