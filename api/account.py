from starlette.responses import Response
from starlette.routing import Route
import json
import time
import httpx

from config import FULL_UNLOCK
from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt
from api.misc import generate_random_string, add_mail
from api.templates import START_TOUR_STATUS, START_COMPOSER_STATUS, START_COLLECTION_STATUS, START_PIANO_STATUS, START_MAIL, START_LEAGUE, RESET_DATA

async def create_insert_user(userId, password, is_oauth):

    query = users.insert().values(
            userid=userId,
            password=password,
            diamond=0, 
            gold = 10000,
            created_at = int(time.time() * 1000),
            clearCount = 0,
            daily = 0,
            composer = START_COMPOSER_STATUS,
            collection = START_COLLECTION_STATUS,
            clear = [],
            piano = START_PIANO_STATUS,
            tour = START_TOUR_STATUS,
            item = [],
            league = START_LEAGUE,
            termsAgree = False
        )
    user_id = await database.execute(query)

    user_mail = START_MAIL.copy()
    if not is_oauth:
        await add_mail(user_id, "Please Read: Your Account's Backup Key", "Your account was created in Guest Mode.\nIf you change your device or reinstall the game in the future, you would need to migrate your profile.\nTo do so, the Access Key (AK) below is necessary.\nGo to the website provided by the admin, and enter this as the old AK.\nYou will receive the same mail for the new account. Enter this as the new AK.\nBelow is your AK:\n\n" + userId + password + "\n\nTake a screenshot of this message. For security, this mail is only available for 30 days.\nWhen migrating, Existing device will lose their progress.\nThus, do not share the AK with anyone.", 31, None, None, None)



    for mail in user_mail:
        await add_mail(user_id, mail["subject"], mail["description"], 99999, mail["item"], mail["quantity"], None)

async def create_authentication(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)

    if decrypted_data != []:
        response_data = {"code": -100}
    else:
        # processing
        userId = generate_random_string(32)
        password = generate_random_string(32)

        await create_insert_user(userId, password, False)

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

async def obtain_user_data(user, userId):
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
                            "ticket": 0,
                            "lastTicketCharge": 0,
                            "lastOnetimeBonus": 0,
                            "termsAgree": user['termsAgree'],
                            "welcomeGift": True,
                            "freeTicketEndAt": True,
                            "createdAt": user["created_at"],
                            "blocked": 0,
                            "clearCount": user['clearCount']
                        }
                    },
                    "code": 100,
                    "invoke": [{"name": "newAccessToken", "params":[session_token]}]}
    return response_data
    
async def login(request):
    decrypted_data, user_unused, session_unused, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 5:
        response_data = {"code": -100}
    else:
        # For facebook, these matches as well (uid, token (after graph check))
        type = decrypted_data[0]
        userId = decrypted_data[1]
        password = decrypted_data[2]

        query = users.select().where(users.c.userid == userId, users.c.password == password)
        user = await database.fetch_one(query)

        if user:
            response_data = await obtain_user_data(user, userId)
        elif type in [1, 2]:
            # do oauth create user
            # Check user creds first
            if type == 1 and False:
                # Facebook
                verification_success = await check_facebook_creds(userId, password)
                if verification_success:
                    # SUCCESS, Insert user and return object. Check if token is new (wrong password)
                    query = users.select().where(users.c.userid == userId)
                    user = await database.fetch_one(query)
                    if user is None:
                        await create_insert_user(userId, password, True)
                        query = users.select().where(users.c.userid == userId, users.c.password == password)
                        user = await database.fetch_one(query)
                    else:
                        # update password to the user's token
                        query = users.update().where(users.c.id == user["id"]).values(password=password)
                        await database.execute(query)
                    
                    response_data = await obtain_user_data(user, userId)
                else:
                    response_data = {"code": -201}
            elif type == 1:
                print("Facebook not supported yet")
                response_data = {"code": -101}
            else:
                print("Apple not supported yet")
                response_data = {"code": -101}

        else:
            response_data = {"code": -101}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def get_ad_count(request):
    response_data = {"result":[0,0],"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)
    
async def get_game_item_list(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
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
    
    if FULL_UNLOCK:
        remain_days = 90
    else:
        remain_days = 0
    
    response_data = {
        "result": {
            "objectId": 11805,
            "owner": user["id"],
            "holdDays": 0,
            "remainDays": remain_days,
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
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

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
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        nickname = decrypted_data[0]

        if 2 <= len(nickname) <= 12:
            query = users.select().where(users.c.nickname == nickname)
            exist_user = await database.fetch_one(query)

            if exist_user is None:
                reset_gem_count = user['diamond'] - RESET_DATA[0]['n']
                if reset_gem_count >= 0:
                    query = users.update().where(users.c.id == user["id"]).values(nickname=nickname, diamond=reset_gem_count)
                    await database.execute(query)
                    response_data = {"result": None, "code": 100, "invoke": []}
                else:
                    response_data = {"code": -206}
            else:
                response_data = {"code": -207}
        else:
            response_data = {"code": -102}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def agree_terms(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))


    query = users.update().where(users.c.id == user["id"]).values(termsAgree=True)
    await database.execute(query)
    response_data = {"result": None, "code": 100, "invoke": []}


    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def apple_extend_token(request):
    # Simply skips apple server check and return success. Need to check jwt
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)

    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        token = decrypted_data[0]

    return_object = {
        "result": token,
        "code": 100,
        "invoke": []
    }
    encrypted_response = encrypt(return_object)
    return Response(encrypted_response)

async def check_facebook_creds(username, token):
    url = "https://graph.facebook.com/me?access_token=" + token
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("id") == username:
                return True
            else:
                return False
        else:
            return False


routes = [
    Route('/Account/createAuthentication', create_authentication, methods=["POST"]),
    Route('/Account/createUserBegin', create_user_begin, methods=["POST"]),
    Route('/Account/createUserCommit', create_user_commit, methods=["POST"]),
    Route('/Account/agreeTerms', agree_terms, methods=["POST"]),
    Route('/Account/login', login, methods=["POST"]),
    Route('/Account/getAdCount', get_ad_count, methods=["POST"]),
    Route('/Account/getGameItemList', get_game_item_list, methods=["POST"]),
    Route('/Account/getSubscription', get_subscription, methods=["POST"]),
    Route('/Account/changeNicknameBegin', change_nickname_begin, methods=["POST"]),
    Route('/Account/changeNicknameCommit', change_nickname_commit, methods=["POST"]),
    Route('/Apple/extendToken', apple_extend_token, methods=["POST"]),
]