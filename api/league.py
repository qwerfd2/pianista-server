from starlette.responses import Response
from starlette.routing import Route
import json
import time
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string

async def get_group_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":{"objectId":928693,"tier":0,"count":10,"endAt":int(time.time()*1000 + 9999000),"seasonOff":False},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def join(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":None,"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":[],"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def get_group_players(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data ={"result":{"groupPlayers":[{"objectId":9030102,"owner":4041061,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":100043,"score1":842485,"musicId2":100005,"score2":834210,"musicId3":None,"score3":None,"totalScore":1676695,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":True,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":2,"publicData":{"nickname":"ffffjjo","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030101,"owner":4010674,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"nosejajajajq","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030099,"owner":4041060,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"ididoeowl","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030093,"owner":4038110,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"HellAbove","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030085,"owner":1,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"tess","pianoId":400007,"pianoLevel":14,"level":12}},{"objectId":9030084,"owner":4039756,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"Brieiscool","pianoId":400001,"pianoLevel":1,"level":1}},{"objectId":9030077,"owner":3994410,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"Obfenda","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030068,"owner":4041057,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"짐인","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030067,"owner":4038536,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"1vyx5hade","pianoId":400003,"pianoLevel":1,"level":1}},{"objectId":9030066,"owner":4018858,"tier":0,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"fhwigheufhwo","pianoId":400000,"pianoLevel":3,"level":1}}],"feeds":[]},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def take_comfort_ticket(request):
    
    response_data = {"result":[],"code":100,"invoke":[{"name":"itemTradeReceipt","params":[{"itemId":3,"quantity":0,"tag":"leagueComfortTicketBenefit"}]}]}

    encrypted_response = encrypt(response_data)

    return Response(encrypted_response)

routes = [
    Route('/League/getGroupStatus', get_group_status, methods=["POST"]),
    Route('/League/join', join, methods=["POST"]),
    Route('/League/getStatus', get_status, methods=["POST"]),
    Route('/League/getGroupPlayers', get_group_players, methods=["POST"]),
    Route('/League/takeComfortTicket', take_comfort_ticket, methods=["POST"]),
    # Route('/League/start', start_the_game, methods=["POST"]),
    # Route('/League/complete', complete_the_game, methods=["POST"]),
]