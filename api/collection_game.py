from starlette.responses import Response
from starlette.routing import Route
import json
import datetime
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string
from api.templates import PATTERN_DATA
from api.cache import tour_cache, get_my_collection_leaderboard_ranking, get_collection_leaderboard, start_game, complete_game
from api.database import database, results

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []

    # Find all rows in 'results' table with column 'owner' == user['id']
    query = results.select().where(results.c.owner == user["id"])
    user_results = await database.fetch_all(query)


    # Add the results to result_object
    for i, result in enumerate(user_results, start=0):
        result_dict = dict(result)  # Convert the Record object to a dictionary
        result_dict['owner'] = user['id']
        result_object.append(result_dict)
        
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

    if len(decrypted_data) != 2:
        response_data = {"code": -100}
    else:
        patternId = decrypted_data[0]
        isMaster = decrypted_data[1]

        rank_start, rank_now = await get_my_collection_leaderboard_ranking(user["id"], patternId, isMaster)

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
    
    if len(decrypted_data) != 3:
        response_data = {"code": -100}
    else:

        patternId = decrypted_data[0]
        isMaster = decrypted_data[2]

        rank_result = await get_collection_leaderboard(patternId)

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
    
    if len(decrypted_data) != 3:
        response_data = {"code": -100}
    else:
        patternId = decrypted_data[0]
        items_used = decrypted_data[1]

        response_data = {
            "result": {},
            "code": 100,
            "invoke": []
        }

        response_data["result"] = await start_game(user, patternId, 1, False, patternId, None)

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def complete_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 9:
        response_data = {"code": -100}
    else:
        response_field = await complete_game(1, user, decrypted_data[0], decrypted_data[1], decrypted_data[2], decrypted_data[3], decrypted_data[4], decrypted_data[5], decrypted_data[6], decrypted_data[7], decrypted_data[8], False)
        response_code = response_field.get('code', 100)
        response_data = {
            "result": response_field,
            "code": response_code,
            "invoke": []
        }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)   

async def get_collection(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    
    response_data = {
        "result": [],
        "code": 100,
        "invoke": []
    }
    i = 1
    for collection in user["collection"]:
        i += 1
        collection["objectId"] = i
        collection["owner"] = user["id"]
        response_data["result"].append(collection)

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)   


routes = [
     Route('/CollectionGame/getStatus', get_status, methods=["POST"]),
     Route('/CollectionGame/getCollection', get_collection, methods=["POST"]),
     Route('/CollectionGame/getMyRank', get_my_rank, methods=["POST"]),
     Route('/CollectionGame/getRanking', get_ranking, methods=["POST"]),
     Route('/CollectionGame/start', start_the_game, methods=["POST"]),
     Route('/CollectionGame/complete', complete_the_game, methods=["POST"]),
]