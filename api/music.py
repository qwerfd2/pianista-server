from starlette.responses import Response
from starlette.routing import Route
import json
import time

from api.database import get_user_and_validate_session
from api.crypt import encrypt
import api.cache

async def get_rotation_list(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {
        "result": {
            "objectId": 11805,
            "owner": user["id"],
            "music1":api.cache.league_session[0][0]['musicId1'],
            "music2":api.cache.league_session[0][0]['musicId2'],
            "music3":api.cache.league_session[0][0]['musicId3'],
            "resetCount":0,
            "expiredAt":int(time.time() * 1000) +9900000,
        },
        "code": 100,
        "invoke": []
    }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(error_response))
    
    result_object = []
    i = 0
    for composer in user["composer"]:
        i += 1
        composer["objectId"] = i
        composer["owner"] = user["id"]
        result_object.append(composer)

    response_data = {
        "result": result_object,
        "code": 100,
        "invoke": []
    }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

routes = [
    Route('/Music/getRotationList', get_rotation_list, methods=["POST"]),
    Route('/Music/getStatus', get_status, methods=["POST"]),
]