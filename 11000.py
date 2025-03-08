from starlette.applications import Starlette
from starlette.responses import FileResponse, Response
from starlette.routing import Route
from starlette.config import Config
from starlette.applications import Starlette
from starlette.routing import Route
import os
import asyncio

config = Config("config.env")
HOST = config("HOST", default="192.168.0.106")
PORT = int(config("PORT", default=9069))
DEBUG = config("DEBUG", cast=bool, default=False)
SSL_CERT = config("SSL_CERT", default=None)
SSL_KEY = config("SSL_KEY", default=None)

#server_url = f"http://{HOST}:{PORT}/"
#server_url = f"https://pianista-cdn.pianista.io"

#from api.cdn import update_configs
#update_configs(server_url)

from api.templates import init_templates
init_templates()

from api.cache import load_play_session, load_league_session
load_play_session()
asyncio.run(load_league_session())

from api.database import database, init_db
from api.cache import cache_database, init_cache_db, generate_league_session
from api.platform import routes as platform_routes
from api.account import routes as account_routes
from api.music import routes as music_routes
from api.collection_game import routes as collection_routes
from api.piano_inventory import routes as piano_routes
from api.tour_game import routes as tour_routes
from api.postbox import routes as postbox_routes
from api.shop import routes as shop_routes
from api.league import routes as league_routes

from api.cache import start_cleanup_task

#generate_league_session()

root_folder = os.path.dirname(os.path.abspath(__file__))
allowed_folders = ["bundle", "files", "data", "manifest"]

async def serve_file(request):
    path = request.path_params['path']
    for folder in allowed_folders:
        if path.startswith(folder):
            file_path = os.path.join(root_folder, path)
            if os.path.isfile(file_path):
                response = FileResponse(file_path)
                response.headers["accepted-ranges"] = "bytes"
                response.headers["x-amz-cf-pop"] = "NRT57-P3"
                response.headers["x-amz-cf-id"] = "V2yGNNXOlpw0r5LurepznExa1wyh5bAAyJzMfpTJc-SoO1oFGnKViQ=="
                return response
    return Response("", status_code=404)

routes = []

routes = routes + platform_routes + account_routes + music_routes + collection_routes + piano_routes + tour_routes + postbox_routes + shop_routes + league_routes

routes.append(Route("/{path:path}", serve_file))

app = Starlette(debug=DEBUG, routes=routes)

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()
    await cache_database.connect()
    await init_cache_db()
    await start_cleanup_task()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await cache_database.disconnect()

if __name__ == "__main__":
    import uvicorn
    ssl_context = (SSL_CERT, SSL_KEY) if SSL_CERT and SSL_KEY else None
    uvicorn.run(app, host=HOST, port=PORT, ssl_certfile=SSL_CERT, ssl_keyfile=SSL_KEY, headers=[("server", "AmazonS3"), ("Content-Type", "application/json;charset=utf-8")])