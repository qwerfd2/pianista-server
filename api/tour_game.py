from starlette.responses import Response
from starlette.routing import Route
import json

from api.database import get_user_and_validate_session
from api.crypt import encrypt
from api.templates import TOUR_EASY_STAGE_DATA, TOUR_NORMAL_STAGE_DATA, TOUR_HARD_STAGE_DATA, TOUR_MASTER_STAGE_DATA
from api.cache import get_my_tour_leaderboard_ranking, get_tour_leaderboard, start_game, complete_game

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []
    i = 0
    for tour in user["tour"]:
        i += 1
        tour["objectId"] = i
        tour["owner"] = user["id"]
        result_object.append(tour)
        
    response_data = {
        "result": result_object,
        "code": 100,
        "invoke": []
    }

    encrypted_response = encrypt(response_data)
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

        rank_start, rank_now = await get_my_tour_leaderboard_ranking(user["id"], pack, diff, isMaster)

        response_data = {
            "result": [rank_start, rank_now],
            "code": 100,
            "invoke": []
        }

    encrypted_response = encrypt(response_data)
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

        rank_result = await get_tour_leaderboard(pack, diff)

        response_data = {
            "result": rank_result,
            "code": 100,
            "invoke": []
        }

    encrypted_response = encrypt(response_data)
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
        items_used = decrypted_data[3]
        is_master = 1
        if tour_diff == 0:
            stage_data = TOUR_NORMAL_STAGE_DATA
        elif tour_diff == 1:
            stage_data = TOUR_HARD_STAGE_DATA
        elif tour_diff == 2:
            is_master = 2
            stage_data = TOUR_MASTER_STAGE_DATA
        else:
            stage_data = TOUR_EASY_STAGE_DATA

        # find patternId
        patternId = next((stage["pi"] for stage in stage_data if stage["c"] == tour_id), None)

        response_data = {
            "result": {},
            "code": 100,
            "invoke": []
        }

        response_data["result"] = await start_game(user, patternId, 0, is_master, items_used, tour_diff, tour_id)

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def complete_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 10:
        response_data = {"code": -100}
    else:
        response_field = await complete_game(0, user, decrypted_data[0], decrypted_data[1], decrypted_data[2], decrypted_data[3], decrypted_data[4], decrypted_data[5], decrypted_data[6], decrypted_data[7], decrypted_data[8], decrypted_data[9])
        response_code = 100
        response_code = response_field.get('code', 100)
        response_data = {
            "result": response_field,
            "code": response_code,
            "invoke": []
        }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)      

routes = [
    Route('/TourGame/getStatus', get_status, methods=["POST"]),
    Route('/TourGame/getMyRank', get_my_rank, methods=["POST"]),
    Route('/TourGame/getRanking', get_ranking, methods=["POST"]),
    Route('/TourGame/start', start_the_game, methods=["POST"]),
    Route('/TourGame/complete', complete_the_game, methods=["POST"]),
]