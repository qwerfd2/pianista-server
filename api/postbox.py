from starlette.responses import Response
from starlette.routing import Route
import json
import time

from api.database import database, users, get_user_and_validate_session, mails
from api.crypt import encrypt

def add_gift(user, item, quantity):
    # you can actually gift pretty much everything. Currencies, charts, pianos, vip time, items, etc. 
    # But I will not add all of them here since most are rendered obsolete.

    if item == None or quantity == None:
        return user
    
    if item == 1: # gem
        user['diamond'] += quantity
        user['diamond'] = min(user['diamond'], 99999999)

    elif item == 2: # gold
        user['gold'] += quantity
        user['gold'] = min(user['gold'], 99999999)

    elif item > 500000 and item < 700000: # items
        user_item = next((i for i in user['item'] if i["itemId"] == item), None)
        if user_item:
            for u_item in user["item"]:
                if u_item["itemId"] == item:
                    u_item["quantity"] += 1

        else:
            item_object = {"itemId": item, "quantity": quantity}
            user["item"].append(item_object)

    elif item >= 400000 and item < 500000: # pianos
        piano_object = next((piano for piano in user['piano'] if piano["pianoId"] == item), None)
        if piano_object == None:
            piano_object = {"pianoId": item, "level": 1, "equip": False}
            user["piano"].append(piano_object)


    return user

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    response_object = []
    query = mails.select().where(mails.c.owner == user["id"])
    user_mail = await database.fetch_all(query)
    now_time = int(time.time() * 1000)

    for msg in user_mail:
        msg = dict(msg)
        if (msg['status'] != 2 and (msg['expiredAt'] == None or msg['expiredAt'] > now_time)):
            response_object.append(msg)

    response_data = {"result":{"over":False,"msg":response_object},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_item(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    else:
        mail_id = decrypted_data[0]

        item = None
        quantity = None

        query = mails.select().where((mails.c.owner == user["id"]) & (mails.c.objectId == mail_id) & (mails.c.status == 0))
        mail = await database.fetch_one(query)
        if not mail:
            response_data = {"code": -100}

        else:
            item = mail["item"]
            quantity = mail["quantity"]

            invoke = []
            user = dict(user)
            if item and quantity:
                user = add_gift(user, item, quantity)

                query = users.update().where(users.c.id == user["id"]).values(
                    diamond=user["diamond"],
                    gold=user["gold"],
                    item=user["item"],
                    piano=user["piano"]
                )
                await database.execute(query)
                invoke = [{"name": "itemTradeReceipt","params":[{"itemId": item,"quantity": quantity}]}]

                mail_update = mails.update().where(mails.c.objectId == mail_id).values(status=2)
                await database.execute(mail_update)
            else:
                mail_update = mails.update().where(mails.c.objectId == mail_id).values(status=1)
                await database.execute(mail_update)

            response_data = {
                "result": None,
                "code": 100,
                "invoke": invoke
            }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_item_all(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    query = mails.select().where((mails.c.owner == user["id"]) & (mails.c.status == 0))
    user_mail = await database.fetch_all(query)
    
    end_params = []

    for mail in user_mail:
        if mail["status"] == 0:
            item = mail["item"]
            quantity = mail["quantity"]

            if (item and quantity):
                end_params.append({
                    "itemId": item,
                    "quantity": quantity
                })
                mail_update = mails.update().where(mails.c.objectId == mail["id"]).values(status=2)
                await database.execute(mail_update)
    user = dict(user)
    for items in end_params:
        user = add_gift(user, items['itemId'], items['quantity'])

    query = users.update().where(users.c.id == user["id"]).values(
        diamond=user["diamond"],
        gold=user["gold"],
        item=user["item"],
        piano=user["piano"]
    )
    await database.execute(query)

    response_data = {
        "result": None,
        "code": 100,
        "invoke": [{"name": "itemTradeReceipt","params": end_params}]
    }

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

routes = [
    Route('/Postbox/getStatus', get_status, methods=["POST"]),
    Route('/Postbox/getItem', get_item, methods=["POST"]),
    Route('/Postbox/getItemAll', get_item_all, methods=["POST"]),
]