from starlette.responses import Response
from starlette.routing import Route
import json
import datetime
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string



routes = [
    # Route('/CollectionGame/getStatus', get_status, methods=["POST"]),
    # Route('/CollectionGame/getCollection', get_collection, methods=["POST"]),
    # Route('/CollectionGame/getMyRank', get_my_rank, methods=["POST"]),
    # Route('/CollectionGame/getRanking', get_ranking, methods=["POST"]),
    # Route('/CollectionGame/start', start, methods=["POST"]),
    # Route('/CollectionGame/complete', complete, methods=["POST"]),
]