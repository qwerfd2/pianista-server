from starlette.responses import Response
from starlette.routing import Route
import json
import time
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string
from api.cache import start_game, complete_game, league_count, league_id, get_league_leaderboard

def get_end_of_day():
    now = time.time()
    end_of_day = time.mktime(time.localtime(now)[:3] + (23, 59, 59, 0, 0, -1))
    return int(end_of_day * 1000)

async def get_group_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":{"objectId":928693,"tier":user['league']['tier'],"count":league_count,"endAt":get_end_of_day(),"seasonOff":False},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def join(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":None,"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []

    if (user['league']['score1']):
        result_object.append({"objectId":1,"owner":user['id'],"leagueId":league_id,"patternId":user['league']['patternId1'],"score":user['league']['score1'],"updatedAt":user['league']['updatedAt']})
    if (user['league']['score2']):
        result_object.append({"objectId":2,"owner":user['id'],"leagueId":league_id,"patternId":user['league']['patternId2'],"score":user['league']['score2'],"updatedAt":user['league']['updatedAt']})
    if (user['league']['score3']):
        result_object.append({"objectId":3,"owner":user['id'],"leagueId":league_id,"patternId":user['league']['patternId3'],"score":user['league']['score3'],"updatedAt":user['league']['updatedAt']})

    response_data = {"result":result_object,"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_group_players(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data ={"result":{"groupPlayers": get_league_leaderboard(user),"feeds":[]},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def take_comfort_ticket(request):
    
    response_data = {"result":[],"code":100,"invoke":[{"name":"itemTradeReceipt","params":[{"itemId":3,"quantity":0,"tag":"leagueComfortTicketBenefit"}]}]}

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
        response_field = await complete_game(2, user, decrypted_data[0], decrypted_data[1], decrypted_data[2], decrypted_data[3], decrypted_data[4], decrypted_data[5], decrypted_data[6], decrypted_data[7], decrypted_data[8], False)
        response_code = response_field.get('code', 100)
        response_data = {
            "result": response_field,
            "code": response_code,
            "invoke": []
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
]