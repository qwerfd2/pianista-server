from starlette.responses import Response
from starlette.routing import Route
import json
import datetime
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string
from api.templates import PIANO_UPGRADE_DATA

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    result_object = []
    i = 0
    for piano in user["piano"]:
        i += 1
        piano["objectId"] = i
        piano["owner"] = user["id"]
        result_object.append(piano)
        
    response_data = {
        "result": result_object,
        "code": 100,
        "invoke": []
    }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def upgrade(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        piano_id = decrypted_data[0]
        piano = next((piano for piano in user['piano'] if piano["pianoId"] == piano_id), {})
        if (piano == {}):
            response_data = {"code": -100}
        else:
            user = dict(user)
            if (piano["level"] >= len(PIANO_UPGRADE_DATA)):
                response_data = {"code": -101}
            else:   
                
                cost = PIANO_UPGRADE_DATA[piano["level"]]["p"]
                if (cost == 0):
                    response_data = {"code": -102}
                else:
                    if (user["gold"] < cost):
                        response_data = {"code": -103}
                    else:
                        cur_piano = {}
                        user["gold"] -= cost
                        for piano in user['piano']:
                            if piano["pianoId"] == piano_id:
                                piano["level"] += 1
                                cur_piano = piano
                                break

                        query = users.update().where(users.c.id == user["id"]).values(
                            gold=user["gold"],
                            piano=user["piano"]
                        )
                        await database.execute(query)
                        response_data = {
                            "result": cur_piano,
                            "code": 100,
                            "invoke": []
                        }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def equip(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        piano_id = decrypted_data[0]
        piano = next((piano for piano in user['piano'] if piano["pianoId"] == piano_id), {})
        if (piano == {}):
            response_data = {"code": -101}
        else:
            found = False
            for piano in user['piano']:
                if piano["pianoId"] == piano_id:
                    found = True
                    piano["equip"] = True
                else:
                    piano["equip"] = False

            if not found:
                response_data = {"code": -102}
            else:
                query = users.update().where(users.c.id == user["id"]).values(
                    piano=user["piano"]
                )
                
                response_data = {
                    "result": {},
                    "code": 100,
                    "invoke": []
                }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def take_piano(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 3:
        response_data = {"code": -100}
    else:
        user = dict(user)
        piano_id = decrypted_data[0]
        piano = next((piano for piano in user['piano'] if piano["pianoId"] == piano_id), {})
        print(piano)
        if piano is None:

            piano_obj = {
                "pianoId": piano_id,
                "level": 1,
                "equip": False
            }
            user['piano'].append(piano_obj)
            query = users.update().where(users.c.id == user["id"]).values(
                piano=user["piano"]
            )
            await database.execute(query)
            
        response_data = {
            "result": {},
            "code": 100,
            "invoke": []
        }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

routes = [
    Route('/PianoInventory/getStatus', get_status, methods=["POST"]),
    Route('/PianoInventory/upgrade', upgrade, methods=["POST"]),
    Route('/PianoInventory/equip', equip, methods=["POST"]),
    Route('/PianoInventory/takePiano', take_piano, methods=["POST"]),
]