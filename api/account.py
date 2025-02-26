from starlette.responses import Response
from starlette.routing import Route
import json
import datetime

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string

async def create_authentication(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    
    if decrypted_data != []:
        response_data = {"code": -100}
    else:
        # processing
        userId = generate_random_string(32)
        password = generate_random_string(32)

        query = users.insert().values(
            userid=userId,
            password=password,
            diamond=1000, 
            gold = 9999999
        )
        await database.execute(query)

        response_data = {
            "result": {
                "objectId": 1,
                "provider": 0,
                "userId": userId,
                "password": password
            },
            "code": 100,
            "invoke": []
        }

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)

async def create_user_begin(request):
    decrypted_data, user_unused, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 4:
        response_data = {"code": -100}
    else:
        userId = decrypted_data[1]
        password = decrypted_data[2]
        nickname = decrypted_data[3]

        if 6 <= len(nickname) <= 20:
            query = users.select().where(users.c.userid == userId, users.c.password == password, users.c.nickname == None)
            user = await database.fetch_one(query)

            if user:
                query = users.select().where(users.c.nickname == nickname)
                existing_nickname = await database.fetch_one(query)

                if not existing_nickname:
                    response_data = {"result": None, "code": 100, "invoke": []}
                else:
                    response_data = {"code": -101}
            else:
                response_data = {"code": -103}
        else:
            response_data = {"code": -102}

    encrypted_response = encrypt(json.dumps(response_data))
    return Response(encrypted_response)
    
async def create_user_commit(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 5:
        response_data = {"code": -100}
    else:
        userId = decrypted_data[1]
        password = decrypted_data[2]
        nickname = decrypted_data[4]

        if 6 <= len(nickname) <= 20:
            query = users.select().where(users.c.userid == userId, users.c.password == password, users.c.nickname == None)
            user = await database.fetch_one(query)

            if user:
                query = users.select().where(users.c.nickname == nickname)
                existing_nickname = await database.fetch_one(query)

                if not existing_nickname:
                    query = users.update().where(users.c.id == user["id"]).values(nickname=nickname)
                    await database.execute(query)

                    response_data = {"result": None, "code": 100, "invoke": []}
                else:
                    response_data = {"code": -101}
            else:
                response_data = {"code": -103}
        else:
            response_data = {"code": -102}


    encrypted_response = encrypt(json.dumps(response_data))
    
    return Response(encrypted_response)
    
async def login(request):
    decrypted_data, user_unused, session_unused, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 5:
        response_data = {"code": -100}
    else:
        userId = decrypted_data[1]
        password = decrypted_data[2]

        query = users.select().where(users.c.userid == userId, users.c.password == password)
        user = await database.fetch_one(query)

        if user:
            query = sessions.select().where(sessions.c.userid == userId)
            session = await database.fetch_one(query)

            session_token = generate_random_string(200)

            if session:
                query = sessions.update().where(sessions.c.userid == userId).values(session=session_token)
                await database.execute(query)
            else:
                query = sessions.insert().values(userid=userId, session=session_token)
                await database.execute(query)

                query = sessions.select().where(sessions.c.userid == userId)
                session = await database.fetch_one(query)

            response_data = {"result": {
                                "sharedUser": {
                                    "objectId": user["id"],
                                    "shardId": 2,
                                    "authObjectId": session["id"],
                                    "nickname": user["nickname"],
                                    "channel": 2
                                },
                                "unlockTourPack": [],
                                "user": {
                                    "objectId": user["id"],
                                    "nicknameReset": 0,
                                    "diamond": user["diamond"],
                                    "gold": user["gold"],
                                    "ticket": 10,
                                    "lastTicketCharge": datetime.datetime.utcnow - datetime.timedelta(seconds=100),
                                    "lastOnetimeBonus": None,
                                    "termsAgree": True,
                                    "welcomeGift": False,
                                    "freeTicketEndAt": None,
                                    "createdAt": user["created_at"],
                                    "blocked": user["blocked"],
                                    "clearCount": user["clearCount"]
                                }
                            },
                            "code": 100,
                            "invoke": [{"name": "newAccessToken", "params":[session_token]}]}
        else:
            response_data = {"code": -101}

        encrypted_response = encrypt(json.dumps(response_data))
    
    return Response(encrypted_response)
    
async def get_ad_count(request):
    body = await request.body()
    try:
        response_data = {"result":[0,datetime.datetime.utcnow + datetime.timedelta(seconds=90000)],"code":100,"invoke":[]}

        encrypted_response = encrypt(json.dumps(response_data))
        
        return Response(encrypted_response)
    except Exception as e:
        return Response(encrypt(json.dumps({"code": -500})))
    
    
async def get_game_item_list(request):
    body = await request.body()
    try:
        response_data = {"result":[],"code":100,"invoke":[]}

        encrypted_response = encrypt(json.dumps(response_data))
        
        return Response(encrypted_response)
    except Exception as e:
        return Response(encrypt(json.dumps({"code": -500})))
    
async def get_subscription(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    response_data = {
        "result": {
            "objectId": 11805,
            "owner": user["id"],
            "holdDays": 0,
            "remainDays": 30,
            "referenceDate": datetime.datetime.utcnow() - datetime.timedelta(seconds=90000),
            "pastDays": 0
        },
        "code": 100,
        "invoke": []
    }

    encrypted_response = encrypt(json.dumps(response_data))

    return Response(encrypted_response)

routes = [
    Route('/Account/createAuthentication', create_authentication, methods=["POST"]),
    Route('/Account/createUserBegin', create_user_begin, methods=["POST"]),
    Route('/Account/createUserCommit', create_user_commit, methods=["POST"]),
    Route('/Account/createUserCommit', login, methods=["POST"]),
    Route('/Account/getAdCount', get_ad_count, methods=["POST"]),
    Route('/Account/getGameItemList', get_game_item_list, methods=["POST"]),
    Route('/Account/getSubscription', get_subscription, methods=["POST"]),
]