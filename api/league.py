from starlette.responses import Response
from starlette.routing import Route
import json
import time
import random

from api.database import database, users, get_user_and_validate_session
from api.crypt import encrypt
from api.misc import get_user_level, get_user_piano, get_end_of_day, get_league_rank, add_feed
import api.cache
from api.play import start_game, complete_game
from api.templates import START_LEAGUE

async def get_group_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":{
        "objectId":user['league']['leagueId'],
        "tier":user['league']['tier'],
        "count":api.cache.league_count,
        "endAt":user['league']['endAt'],
        "seasonOff":False
        },"code":100,"invoke":[]}

    if (user['league']['endAt'] < int(time.time() * 1000)):
        await api.cache.load_league_session()
        response_data["result"]["seasonOff"] = True
        response_data["invoke"] = [{"name":"availableSeasonOff","params":[]}]

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def join(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    user = dict(user)
    tier = user['league']['tier']
    user['league'] = START_LEAGUE
    user['league']['updatedAt'] = int(time.time() * 1000)
    user['league']['endAt'] = get_end_of_day()
    user['league']['leagueId'] = api.cache.league_id
    user['league']['tier'] = tier

    user['league']['marbleId1'] = (tier * 5) + 3
    user['league']['marbleId2'] = (tier * 5) + 4
    user['league']['marbleId3'] = (tier * 5) + 5
    user['league']['bonusMarbleId'] = (tier * 5) + 2

    query = users.update().where(users.c.id == user['id']).values(league=user['league'])
    await database.execute(query)

    response_data = {"result":None,"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []

    if (user['league']['score1']):
        result_object.append({"objectId":1,"owner":user['id'],"leagueId":api.cache.league_id,"patternId":user['league']['patternId1'],"score":user['league']['score1'],"updatedAt":user['league']['updatedAt']})
    if (user['league']['score2']):
        result_object.append({"objectId":2,"owner":user['id'],"leagueId":api.cache.league_id,"patternId":user['league']['patternId2'],"score":user['league']['score2'],"updatedAt":user['league']['updatedAt']})
    if (user['league']['score3']):
        result_object.append({"objectId":3,"owner":user['id'],"leagueId":api.cache.league_id,"patternId":user['league']['patternId3'],"score":user['league']['score3'],"updatedAt":user['league']['updatedAt']})

    response_data = {"result":result_object,"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_group_players(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if api.cache.league_id != user['league']['leagueId']:
        # This is an old league
        leaderboard = user['league']['leaderboardCache']

    else:
        leaderboard = api.cache.get_league_leaderboard(user)

        user = dict(user)

        old_leaderboard = user['league']['leaderboardCache']

        user['league']['leaderboardCache'] = leaderboard

        all_played = next((feed for feed in user['league']['feed'] if feed["feedId"] == 6), None)

        if (user['league']['score1'] and user['league']['score2'] and user['league']['score3']) and all_played == None:
            user = add_feed(user, 6, None, api.cache.league_id)

        old_leaderboard_rank = get_league_rank(old_leaderboard, user['id'], 0)
        new_leaderboard_rank = get_league_rank(leaderboard, user['id'], 0)
        soaring = next((feed for feed in user['league']['feed'] if feed["feedId"] == 4), None)

        if (old_leaderboard_rank - new_leaderboard_rank > 5) and (soaring == None):
            user = add_feed(user, 4, None, api.cache.league_id)
        
        third = next((feed for feed in user['league']['feed'] if feed["feedId"] == 3), None)
        if (new_leaderboard_rank == 3) and (third == None):
            user = add_feed(user, 3, None, api.cache.league_id)

        second = next((feed for feed in user['league']['feed'] if feed["feedId"] == 2), None)
        if (new_leaderboard_rank == 2) and (second == None):
            user = add_feed(user, 2, None, api.cache.league_id)

        first = next((feed for feed in user['league']['feed'] if feed["feedId"] == 1), None)
        if (new_leaderboard_rank == 1) and (first == None):
            user = add_feed(user, 1, None, api.cache.league_id)

        query = users.update().where(users.c.id == user['id']).values(league=user['league'])
        await database.execute(query)

    response_data ={"result":{"groupPlayers": leaderboard,"feeds":user['league']['feed']},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def season_off(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = {}

    rank = get_league_rank(user['league']['leaderboardCache'], user['id'], 0)

    user_tier = user['league']['tier']

    if rank < 4:
        # promote
        if (user_tier <= 20):
            user_tier += 1
    elif rank > 7:
        # demote
        if (user_tier > 1):
            user_tier -= 1

    score1 = user['league']['score1'] or 0
    score2 = user['league']['score2'] or 0
    score3 = user['league']['score3'] or 0
    user_level = get_user_level(user)
    piano_id, piano_level = get_user_piano(user)
    
    result_object["objectId"] = 10
    result_object['owner'] = user['id']
    result_object['tier'] = user['league']['tier']
    result_object['nextTier'] = user_tier
    result_object['leagueId'] = user['league']['leagueId']
    result_object['musicId1'] = user['league']['musicId1']
    result_object['musicId2'] = user['league']['musicId2']
    result_object['musicId3'] = user['league']['musicId3']
    result_object['score1'] = user['league']['score1']
    result_object['score2'] = user['league']['score2']
    result_object['score3'] = user['league']['score3']
    result_object['totalScore'] = score1 + score2 + score3
    result_object['marbleId1'] = user['league']['marbleId1']
    result_object['marbleId2'] = user['league']['marbleId2']
    result_object['marbleId3'] = user['league']['marbleId3']
    result_object['marbleAchieve1'] = user['league']['marbleAchieve1']
    result_object['marbleAchieve2'] = user['league']['marbleAchieve2']
    result_object['marbleAchieve3'] = user['league']['marbleAchieve3']
    result_object['bonusMarbleId'] = user['league']['bonusMarbleId']
    result_object['bonusMarbleAchieve'] = user['league']['bonusMarbleAchieve']
    result_object['updatedAt'] = user['league']['updatedAt']
    result_object['playCount'] = user['league']['playCount']
    result_object['rewardProvide'] = True
    result_object['publicData'] = {"nickname":user['nickname'],"pianoId":piano_id,"pianoLevel":piano_level,"level":user_level}

    if (user_tier != user['league']['tier']):
        user['league']['tier'] = user_tier
        query = users.update().where(users.c.id == user['id']).values(league=user['league'])
        await database.execute(query)
    
    response_data = {"result":result_object,"code":100,"invoke":[]}
    
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def take_comfort_ticket(request):
    
    response_data = {"result":[],"code":100,"invoke":[{"name":"itemTradeReceipt","params":[{"itemId":1,"quantity":0,"tag":"leagueComfortTicketBenefit"}]}]}

    encrypted_response = encrypt(response_data)

    return Response(encrypted_response)

async def start_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 3:
        response_data = {"code": -100}
    else:
        patternId = decrypted_data[0]
        items_used = decrypted_data[2]

        response_data = {
            "result": {},
            "code": 100,
            "invoke": []
        }

        response_data["result"] = await start_game(user, patternId, 1, False, items_used, patternId, None)

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def complete_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 9:
        response_data = {"code": -100}
    else:
        response_field, invoke = await complete_game(2, user, decrypted_data[0], decrypted_data[1], decrypted_data[2], decrypted_data[3], decrypted_data[4], decrypted_data[5], decrypted_data[6], decrypted_data[7], decrypted_data[8], False)
        response_code = response_field.get('code', 100)
        response_data = {
            "result": response_field,
            "code": response_code,
            "invoke": invoke
        }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response) 

routes = [
    Route('/League/getGroupStatus', get_group_status, methods=["POST"]),
    Route('/League/join', join, methods=["POST"]),
    Route('/League/getStatus', get_status, methods=["POST"]),
    Route('/League/getGroupPlayers', get_group_players, methods=["POST"]),
    Route('/League/takeComfortTicket', take_comfort_ticket, methods=["POST"]),
    Route('/League/start', start_the_game, methods=["POST"]),
    Route('/League/complete', complete_the_game, methods=["POST"]),
    Route('/League/seasonOff', season_off, methods=["POST"]),
]