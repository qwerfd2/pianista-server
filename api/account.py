from starlette.responses import Response
from starlette.routing import Route
import json
import time

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt
from api.misc import generate_random_string
from api.templates import START_TOUR_STATUS, START_COMPOSER_STATUS, START_COLLECTION_STATUS, START_PIANO_STATUS, START_MAIL, START_LEAGUE

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
            diamond=0, 
            gold = 10000,
            created_at = int(time.time() * 1000),
            clearCount = 0,
            composer = START_COMPOSER_STATUS,
            collection = START_COLLECTION_STATUS,
            clear = [],
            piano = START_PIANO_STATUS,
            tour = START_TOUR_STATUS,
            item = [],
            mail = START_MAIL,
            league = START_LEAGUE,
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

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def create_user_begin(request):
    decrypted_data, user_unused, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 4:
        response_data = {"code": -100}
    else:
        userId = decrypted_data[1]
        password = decrypted_data[2]
        nickname = decrypted_data[3]

        if 2 <= len(nickname) <= 12:
            query = users.select().where(users.c.userid == userId, users.c.password == password, users.c.nickname == None)
            user = await database.fetch_one(query)

            if user:
                query = users.select().where(users.c.nickname == nickname)
                existing_nickname = await database.fetch_one(query)

                if not existing_nickname:
                    response_data = {"result": None, "code": 100, "invoke": []}
                else:
                    response_data = {"code": -207}
            else:
                response_data = {"code": -103}
        else:
            response_data = {"code": -102}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def create_user_commit(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 5:
        response_data = {"code": -100}
    else:
        userId = decrypted_data[1]
        password = decrypted_data[2]
        nickname = decrypted_data[4]

        if 2 <= len(nickname) <= 12:
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
                    response_data = {"code": -207}
            else:
                response_data = {"code": -103}
        else:
            response_data = {"code": -102}


    encrypted_response = encrypt(response_data)
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
                                "shardedUser": {
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
                                    "lastTicketCharge": 0,
                                    "lastOnetimeBonus": 0,
                                    "termsAgree": True,
                                    "welcomeGift": True,
                                    "freeTicketEndAt": True,
                                    "createdAt": 1740232040429,
                                    "blocked": 0,
                                    "clearCount": user['clearCount']
                                }
                            },
                            "code": 100,
                            "invoke": [{"name": "newAccessToken", "params":[session_token]}]}
        else:
            response_data = {"code": -101}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def get_ad_count(request):
    response_data = {"result":[1,int(time.time() * 1000) - 9900000],"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def get_game_item_list(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    body = await request.body()
    item_object = []
    i = 0
    for item in user["item"]:
        i += 1
        item["objectId"] = i
        item["owner"] = user["id"]
        item_object.append(item)

    response_data = {"result":item_object,"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def get_subscription(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    response_data = {
        "result": {
            "objectId": 11805,
            "owner": user["id"],
            "holdDays": 0,
            "remainDays": 365,
            "referenceDate": int(time.time() * 1000) - 100000,
            "pastDays": 0
        },
        "code": 100,
        "invoke": []
    }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def change_nickname_begin(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        nickname = decrypted_data[0]

        if 2 <= len(nickname) <= 12:
            query = users.select().where(users.c.nickname == nickname)
            exist_user = await database.fetch_one(query)

            if exist_user is None:
                response_data = {"result": None, "code": 100, "invoke": []}
            else:
                response_data = {"code": -207}
        else:
            response_data = {"code": -102}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def change_nickname_commit(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        nickname = decrypted_data[0]

        if 2 <= len(nickname) <= 12:
            query = users.select().where(users.c.nickname == nickname)
            exist_user = await database.fetch_one(query)

            if exist_user is None:
                query = users.update().where(users.c.id == user["id"]).values(nickname=nickname)
                await database.execute(query)
                response_data = {"result": None, "code": 100, "invoke": []}

            else:
                response_data = {"code": -207}
        else:
            response_data = {"code": -102}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

routes = [
    Route('/Account/createAuthentication', create_authentication, methods=["POST"]),
    Route('/Account/createUserBegin', create_user_begin, methods=["POST"]),
    Route('/Account/createUserCommit', create_user_commit, methods=["POST"]),
    Route('/Account/login', login, methods=["POST"]),
    Route('/Account/getAdCount', get_ad_count, methods=["POST"]),
    Route('/Account/getGameItemList', get_game_item_list, methods=["POST"]),
    Route('/Account/getSubscription', get_subscription, methods=["POST"]),
    Route('/Account/changeNicknameBegin', change_nickname_begin, methods=["POST"]),
    Route('/Account/changeNicknameCommit', change_nickname_commit, methods=["POST"]),
]