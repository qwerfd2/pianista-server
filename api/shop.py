from starlette.responses import Response
from starlette.routing import Route
import json

from api.database import database, users, get_user_and_validate_session
from api.crypt import encrypt
from api.templates import STORE_GOLD_DATA

async def buy_gold(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 1:
        response_data = {"code": -100}
    
    sku = decrypted_data[0]

    sku_item = next((item for item in STORE_GOLD_DATA if item["c"] == sku), None)

    if not sku_item:
        response_data = {"code": -101}
    else:
        user = dict(user)
        cost = sku_item["p"]
        # assume cost is in diamonds (why would you set it to anything else?)
        if user["diamond"] < cost:
            response_data = {"code": -102}
        else:
            user["diamond"] -= cost
            user["gold"] += sku_item["q"]
            user["gold"] += sku_item["bq"]
            user['gold'] = min(user['gold'], 99999999)
            query = users.update().where(users.c.id == user["id"]).values(
                diamond=user["diamond"],
                gold=user["gold"]
            )
            await database.execute(query)
            response_data = {"result": {}, "code": 100, "invoke": []}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

routes = [
  Route('/Shop/buyGold', buy_gold, methods=["POST"]),
]