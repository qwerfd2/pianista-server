from starlette.responses import Response
from starlette.routing import Route
import json
import time
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string

async def get_rotation_list(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {
        "result": {
            "objectId": 11805,
            "owner": user["id"],
            "music1":100212,
            "music2":100018,
            "music3":100088,
            "resetCount":0,
            "expiredAt":int(time.time() * 1000) + 100000,
        },
        "code": 100,
        "invoke": []
    }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []
    for composer in json.loads(user["composer"]):

        composer["objectId"] = math.random(10000, 99999)
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