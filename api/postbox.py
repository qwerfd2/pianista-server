from starlette.responses import Response
from starlette.routing import Route
import json

from api.database import database, users, get_user_and_validate_session
from api.crypt import encrypt

def add_gift(user, item, quantity):
    # you can actually gift pretty much everything. Currencies, charts, pianos, vip time, items, etc. But I will not add all of them here since most are rendered obsolete.

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
    for msg in user['mail']:
        if (msg['status'] == 0):
            msg["owner"] = user["id"]
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
        user = dict(user)
        for mail in user['mail']:
            if mail["objectId"] == mail_id and mail["status"] == 0:
                item = mail["item"]
                quantity = mail["quantity"]
                user['mail'].remove(mail)
                break
        
        invoke = []
        if not item:
            response_data = {"code": -101}
        else:
            user = add_gift(user, item, quantity)

            query = users.update().where(users.c.id == user["id"]).values(
                diamond=user["diamond"],
                gold=user["gold"],
                item=user["item"],
                mail=user["mail"],
                piano=user["piano"]
            )
            await database.execute(query)
            invoke = [{"name": "itemTradeReceipt","params":[{"itemId": item,"quantity": quantity}]}]

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
    
    user = dict(user)
    end_params = []
    
    for mail in user['mail']:
        if mail["status"] == 0:
            item = mail["item"]
            quantity = mail["quantity"]

            if (item and quantity):
                end_params.append({
                    "itemId": item,
                    "quantity": quantity
                })
                mail["status"] = 1

    user["mail"] = [mail for mail in user["mail"] if mail['status'] == 0]
    
    for items in end_params:
        user = add_gift(user, items['itemId'], items['quantity'])

    query = users.update().where(users.c.id == user["id"]).values(
        diamond=user["diamond"],
        gold=user["gold"],
        item=user["item"],
        mail=user["mail"],
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