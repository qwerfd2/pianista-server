from starlette.responses import Response
from starlette.routing import Route
import json
import datetime
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    i = 0
    response_object = []
    for msg in user['mail']:
        i += 1
        msg["objectId"] = i
        msg["owner"] = user["id"]
        response_object.append(msg)

    response_data = {"result":{"over":False,"msg":response_object},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

routes = [
    Route('/Postbox/getStatus', get_status, methods=["POST"]),
]