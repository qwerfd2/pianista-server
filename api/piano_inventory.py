from starlette.responses import Response
from starlette.routing import Route
import json
import datetime
import math

from api.database import database, users, sessions, get_user_and_validate_session
from api.crypt import encrypt, decrypt
from api.misc import generate_random_string

routes = [
    Route('/PianoInventory/getStatus', get_status, methods=["POST"]),
    Route('/PianoInventory/upgrade', upgrade, methods=["POST"]),
    Route('/PianoInventory/equip', equip, methods=["POST"]),
]