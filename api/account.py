from starlette.responses import Response
from starlette.routing import Route
import json

from api.database import database, users, sessions
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string

async def create_authentication(request):
    body = await request.body()
    try:
        decrypted_data = json.loads(decrypt(body.decode('utf-8')))
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
    except Exception as e:
        return Response(encrypt(json.dumps({"code": -500})))

async def create_user_begin(request):
    body = await request.body()
    try:
        decrypted_data = json.loads(decrypt(body.decode('utf-8')))
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
    except Exception as e:
        return Response(encrypt(json.dumps({"code": -500})))
    
async def create_user_commit(request):
    body = await request.body()
    try:
        decrypted_data = json.loads(decrypt(body.decode('utf-8')))
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
    except Exception as e:
        return Response(encrypt(json.dumps({"code": -500})))
    
async def login(request):
    body = await request.body()
    try:
        decrypted_data = json.loads(decrypt(body.decode('utf-8')))
        if len(decrypted_data) != 5:
            response_data = {"code": -100}
        else:
            userId = decrypted_data[1]
            password = decrypted_data[2]




            encrypted_response = encrypt(json.dumps(response_data))
        
        return Response(encrypted_response)
    except Exception as e:
        return Response(encrypt(json.dumps({"code": -500})))

routes = [
    Route('/Account/createAuthentication', create_authentication, methods=["POST"]),
    Route('/Account/createUserBegin', create_user_begin, methods=["POST"]),
    Route('/Account/createUserCommit', create_user_commit, methods=["POST"]),
    Route('/Account/createUserCommit', login, methods=["POST"]),
]