from starlette.responses import Response
from starlette.routing import Route
import json
import datetime
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string
from api.templates import TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, TOUR_MASTER_STAGE_DATA, PATTERN_DATA
from api.cache import tour_cache, get_my_tour_leaderboard_ranking, get_tour_leaderboard, start_game, complete_game

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []
    for tour in json.loads(user["tour"]):

        tour["objectId"] = math.random(10000, 99999)
        tour["owner"] = user["id"]
        result_object.append(tour)
        
    response_data = {
        "result": result_object,
        "code": 100,
        "invoke": []
    }

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)

async def get_my_rank(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    if len(decrypted_data) != 3:
        response_data = {"code": -100}
    else:
        pack = decrypted_data[0]
        diff = decrypted_data[1]
        isMaster = decrypted_data[2]

        rank_result = get_my_tour_leaderboard_ranking(user["id"], pack, diff, isMaster)

        response_data = {
            "result": rank_result,
            "code": 100,
            "invoke": []
        }

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)

async def get_ranking(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 4:
        response_data = {"code": -100}
    else:

        pack = decrypted_data[0]
        diff = decrypted_data[1]
        isMaster = decrypted_data[2]

        rank_result = get_tour_leaderboard(pack, diff, isMaster)

        response_data = {
            "result": rank_result,
            "code": 100,
            "invoke": []
        }

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)

async def start_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 4:
        response_data = {"code": -100}
    else:
        tour_diff = decrypted_data[0]
        tour_id = decrypted_data[1]
        items_used = decrypted_data[2]

        if tour_diff == 0:
            isMaster = False
            stage_data = TOUR_NORMAL_STAGE_DATA
        elif tour_diff == 1:
            stage_data = TOUR_HARD_STAGE_DATA
        else:
            tour_diff = 2
            stage_data = TOUR_EASY_STAGE_DATA

        # find patternId
        patternId = next((stage["pi"] for stage in stage_data if stage["c"] == tour_id), None)

        response_data = await start_game(user, patternId, 0)

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)

async def complete_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 10:
        response_data = {"code": -100}
    else:
        response_data = await complete_game(decrypted_data[0], decrypted_data[1], decrypted_data[2], decrypted_data[3], decrypted_data[4], decrypted_data[5], decrypted_data[6], decrypted_data[9])

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)      

routes = [
    Route('/TourGame/getStatus', get_status, methods=["POST"]),
    Route('/TourGame/getMyRank', get_my_rank, methods=["POST"]),
    Route('/TourGame/getRanking', get_ranking, methods=["POST"]),
    Route('/TourGame/start', start_the_game, methods=["POST"]),
    Route('/TourGame/complete', complete_the_game, methods=["POST"]),
]