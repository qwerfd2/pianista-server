from starlette.applications import Starlette
from starlette.responses import FileResponse, Response
from starlette.routing import Route
from starlette.config import Config
from starlette.applications import Starlette
from starlette.routing import Route
import os
import json

config = Config("config.env")
HOST = config("HOST", default="192.168.0.106")
PORT = int(config("PORT", default=9069))
DEBUG = config("DEBUG", cast=bool, default=False)
SSL_CERT = config("SSL_CERT", default=None)
SSL_KEY = config("SSL_KEY", default=None)

server_url = f"http://{HOST}:{PORT}/"

from api.cdn import update_configs
update_configs(server_url)

from api.templates import init_templates
init_templates()

from api.database import database, init_db
from api.platform import routes as platform_routes
from api.account import routes as account_routes

root_folder = os.path.dirname(os.path.abspath(__file__))
allowed_folders = ["bundle", "files", "data", "manifest"]

async def serve_file(request):
    path = request.path_params['path']
    for folder in allowed_folders:
        if path.startswith(folder):
            file_path = os.path.join(root_folder, path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
    return Response("", status_code=404)

routes = [
    
]

routes = routes + platform_routes + account_routes

routes.append(Route("/{path:path}", serve_file))

app = Starlette(debug=DEBUG, routes=routes)

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

if __name__ == "__main__":
    import uvicorn
    ssl_context = (SSL_CERT, SSL_KEY) if SSL_CERT and SSL_KEY else None
    uvicorn.run(app, host=HOST, port=PORT, ssl_certfile=SSL_CERT, ssl_keyfile=SSL_KEY)