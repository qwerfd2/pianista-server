from starlette.responses import Response
from starlette.routing import Route
import time
import json

from api.crypt import encrypt, decrypt

async def get_timestamp(request):
    body = await request.body()

    decrypted_data = decrypt(body.decode('utf-8'))
    
    if decrypted_data != []:
        response_data = {"code": -100}
    else:
        timestamp = int(time.time() * 1000)
        
        response_data = {
            "result": timestamp,
            "code": 100,
            "invoke": []
        }
    
    encrypted_response = encrypt(response_data)
    
    return Response(encrypted_response)


    
routes = [
    Route('/Platform/getTimestamp', get_timestamp, methods=["POST"])
]