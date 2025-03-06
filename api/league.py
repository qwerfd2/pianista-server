from starlette.responses import Response
from starlette.routing import Route
import json
import time
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string, add_mail, get_rank_reward
from api.cache import start_game, complete_game, league_count, league_end, generate_league_session, get_league_leaderboard

async def reset_league():
    # Get all the `user` in `users` table
    # for each user,

    query = users.select()
    all_users = await database.fetch_all(query)

    for user in all_users:
        user = dict(user)

        leaderboard = get_league_leaderboard(user)

        # Check if they've been promoted, dempoed, or stayed the same
        rank = 0

        for participant in leaderboard:
            rank += 1
            if participant['owner'] == user['id']:
                break

        # If user is 1, 2, or 3 rank, promote. If 10, 9, or 8, demote. Else, stay the same
        tier = user['league']['tier']
        if (tier == 1):
            append = "st"
        elif (tier == 2):
            append = "nd"
        elif (tier == 3):
            append = "rd"
        else:
            append = "th"

        if (rank < 4 and user['league']['tier'] > 0):
            user['mail'] = add_mail(user['mail'], "You have been promoted in League!", "Congratulation! You ranked in the " + rank + append + " place in the league.\nYou have been promoted to the previous league.\nKeep pushing forward!", 7, 1, get_rank_reward(tier, 2))
            tier += 1
            
        elif (rank > 7 and user['league']['tier'] < 20):
            user['mail'] = add_mail(user['mail'], "You have been demoted in League!", "Unfortunately, you ranked in the " + rank + "th place in the league.\nYou have been demoted to the previous league.\nBetter luck next time!", 7, 2, 10)
            tier -= 1

        else:
            user['mail'] = add_mail(user['mail'], "you stayed in the same League!", "You ranked in the " + rank + + append + " place in the league.\nYour league has remained consistent.\nKeep it going!", 7, 1, get_rank_reward(tier, 1))
        

        user['league'] = {"tier":tier,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False}

        query = users.update().where(users.c.id == user['id']).values(league=user['league'], mail=user['mail'])
        await database.execute(query)

    # Generate new league leaderboard by calling 

    generate_league_session()

async def get_group_status(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))

    response_data = {"result":{"objectId":928693,"tier":user['league']['tier'],"count":league_count,"endAt":league_end or int(time.time() * 1000 + 99999000),"seasonOff":False},"code":100,"invoke":[]}

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

    response_data ={"result":{"groupPlayers":[{"objectId":9030102,"owner":4041061,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":100043,"score1":842485,"musicId2":100005,"score2":834210,"musicId3":None,"score3":None,"totalScore":1676695,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":True,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":2,"publicData":{"nickname":"ffffjjo","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030101,"owner":4010674,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"nosejajajajq","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030099,"owner":4041060,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"ididoeowl","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030093,"owner":4038110,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"HellAbove","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030085,"owner":1,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":100043,"score1":842486,"musicId2":100005,"score2":834210,"musicId3":None,"score3":None,"totalScore":1676696,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"tess","pianoId":400007,"pianoLevel":14,"level":12}},{"objectId":9030084,"owner":4039756,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"Brieiscool","pianoId":400001,"pianoLevel":1,"level":1}},{"objectId":9030077,"owner":3994410,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"Obfenda","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030068,"owner":4041057,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"짐인","pianoId":400000,"pianoLevel":1,"level":1}},{"objectId":9030067,"owner":4038536,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":2,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"1vyx5hade","pianoId":400003,"pianoLevel":1,"level":1}},{"objectId":9030066,"owner":4018858,"tier":20,"nextTier":None,"leagueId":928693,"musicId1":None,"score1":None,"musicId2":None,"score2":None,"musicId3":None,"score3":None,"totalScore":0,"marbleId1":3,"marbleAchieve1":False,"marbleId2":4,"marbleAchieve2":False,"marbleId3":5,"marbleAchieve3":False,"bonusMarbleId":1,"bonusMarbleAchieve":False,"updatedAt":int(time.time() * 1000 - 999000),"rewardProvide":False,"playCount":0,"publicData":{"nickname":"fhwigheufhwo","pianoId":400000,"pianoLevel":3,"level":1}}],"feeds":[]},"code":100,"invoke":[]}

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def take_comfort_ticket(request):
    
    response_data = {"result":[],"code":100,"invoke":[{"name":"itemTradeReceipt","params":[{"itemId":3,"quantity":0,"tag":"leagueComfortTicketBenefit"}]}]}

    encrypted_response = encrypt(response_data)

    return Response(encrypted_response)

async def start_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 3:
        response_data = {"code": -100}
    else:
        patternId = decrypted_data[0]
        items_used = decrypted_data[2]

        response_data = {
            "result": {},
            "code": 100,
            "invoke": []
        }

        response_data["result"] = await start_game(user, patternId, 1, False, items_used, patternId, None)

    encrypted_response = encrypt(response_data)
    return Response(encrypted_response)

async def complete_the_game(request):
    decrypted_data, user, session, error_response = await get_user_and_validate_session(request)
    if error_response:
        return Response(encrypt(json.dumps(error_response)))
    
    if len(decrypted_data) != 9:
        response_data = {"code": -100}
    else:
        response_field = await complete_game(2, user, decrypted_data[0], decrypted_data[1], decrypted_data[2], decrypted_data[3], decrypted_data[4], decrypted_data[5], decrypted_data[6], decrypted_data[7], decrypted_data[8], False)
        response_code = response_field.get('code', 100)
        response_data = {
            "result": response_field,
            "code": response_code,
            "invoke": []
        }
    encrypted_response = encrypt(response_data)
    return Response(encrypted_response) 

routes = [
    Route('/League/getGroupStatus', get_group_status, methods=["POST"]),
    Route('/League/join', join, methods=["POST"]),
    Route('/League/getStatus', get_status, methods=["POST"]),
    Route('/League/getGroupPlayers', get_group_players, methods=["POST"]),
    Route('/League/takeComfortTicket', take_comfort_ticket, methods=["POST"]),
    Route('/League/start', start_the_game, methods=["POST"]),
    Route('/League/complete', complete_the_game, methods=["POST"]),
]