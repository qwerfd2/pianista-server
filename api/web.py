from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse

from api.database import users, database

async def web_migrate_page(request: Request):
    with open("web/migrate.html", "r", encoding="utf-8") as file:
        html_template = file.read()
    return HTMLResponse(content=html_template)

async def web_main_page(request: Request):
    with open("web/main.html", "r", encoding="utf-8") as file:
        html_template = file.read()
    return HTMLResponse(content=html_template)

async def web_migrate_page_action(request: Request):
    form_data = await request.json()
    old_ak = form_data.get("old_ak")
    new_ak = form_data.get("new_ak")

    if not old_ak or not new_ak or len(old_ak) != 64 or len(new_ak) != 64:
        return JSONResponse({"status": "failed", "message": "AK format is incorrect."}, status_code=400)
    
    if old_ak == new_ak:
        return JSONResponse({"status": "failed", "message": "Old AK and New AK cannot be the same."}, status_code=400)

    old_userid = old_ak[:-32]
    new_userid = new_ak[:-32]
    old_password = old_ak[-32:]
    new_password = new_ak[-32:]

    query = users.select().where((users.c.userid == old_userid) & (users.c.password == old_password))
    old_user = await database.fetch_one(query)

    if not old_user:
        return JSONResponse({"status": "failed", "message": "Old AK is incorrect."}, status_code=400)

    new_user = await database.fetch_one(users.select().where((users.c.userid == new_userid) & (users.c.password == new_password)))
    if not new_user:
        return JSONResponse({"status": "failed", "message": "New AK is incorrect."}, status_code=400)

    temp_userid = "TEMP_" + old_userid
    temp_password = "TEMP_" + old_password

    old_user_update = users.update().where(users.c.id == old_user["id"]).values(userid=temp_userid, password=temp_password)
    await database.execute(old_user_update)

    new_user_update = users.update().where(users.c.id == new_user["id"]).values(userid=old_userid, password=old_password)
    await database.execute(new_user_update)

    final_old_user_update = users.update().where(users.c.id == old_user["id"]).values(userid=new_userid, password=new_password)
    await database.execute(final_old_user_update)

    return JSONResponse({"status": "success", "message": "Migration completed successfully."})

routes = [
    Route("/Migrate", web_migrate_page, methods=["GET"]),
    Route("/Migrate/", web_migrate_page, methods=["GET"]),
    Route("/Migrate/Do", web_migrate_page_action, methods=["POST"]),
]