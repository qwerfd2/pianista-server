from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
import secrets
import bcrypt
import sqlalchemy
import json
import datetime

from api.database import users, admins, results, sessions, mails, admins, database

TABLE_MAP = {
        "users": (users, ["id", "userid", "password", "nickname", "diamond", "gold", "created_at", "termsAgree"]),
        "results": (results, ["objectId", "owner", "patternId", "score", "star", "accuracy", "maxCombo", "allCombo", "updatedAt", "master"]),
        "mails": (mails, ["objectId", "owner", "expiredAt", "subject", "description", "noticeId", "item", "quantity", "status"]),
        "sessions": (sessions, ["id", "userid", "session"]),
        "admins": (admins, ["id", "username", "password", "token"]),
    }

async def is_admin(request: Request):
    token = request.cookies.get("token")
    if not token:
        return False
    query = admins.select().where(admins.c.token == token)
    admin = await database.fetch_one(query)
    if not admin:
        return False
    return True

async def web_migrate_page(request: Request):
    with open("web/migrate.html", "r", encoding="utf-8") as file:
        html_template = file.read()
    return HTMLResponse(content=html_template)

async def web_login_page(request: Request):
    with open("web/login.html", "r", encoding="utf-8") as file:
        html_template = file.read()
    return HTMLResponse(content=html_template)

async def web_admin_page(request: Request):
    adm = await is_admin(request)
    if not adm:
        response = RedirectResponse(url="/Login")
        response.delete_cookie("token")
        return response
    with open("web/admin.html", "r", encoding="utf-8") as file:
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

async def web_login_login(request: Request):
    form_data = await request.json()
    username = form_data.get("username")
    password = form_data.get("password")

    query = admins.select().where(admins.c.username == username)
    admin = await database.fetch_one(query)

    if not admin:
        return JSONResponse({"status": "failed", "message": "Invalid username or password."}, status_code=400)
    
    if not bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
        return JSONResponse({"status": "failed", "message": "Invalid username or password."}, status_code=400)
    
    token = secrets.token_hex(64)
    admin_update = admins.update().where(admins.c.id == admin["id"]).values(token=token)
    await database.execute(admin_update)

    return JSONResponse({"status": "success", "message": token})

async def web_admin_get_table(request: Request):
    # Parse query params
    params = request.query_params
    adm = await is_admin(request)
    if not adm:
        return JSONResponse({"data": [], "last_page": 1, "total": 0}, status_code=400)
    
    table_name = params.get("table")
    page = int(params.get("page", 1))
    size = int(params.get("size", 25))
    sort = params.get("sort")
    dir_ = params.get("dir", "asc")
    search = params.get("search", "").strip()
    schema = params.get("schema", "0") == "1"

    if schema:
        table, _ = TABLE_MAP[table_name]
        columns = table.columns  # This is a ColumnCollection
        schema = {col.name: str(col.type).upper() for col in columns}
        return JSONResponse(schema)

    # Validate table
    if table_name not in TABLE_MAP:
        return JSONResponse({"data": [], "last_page": 1, "total": 0}, status_code=400)

    # Validate size
    if size < 10:
        size = 10
    if size > 100:
        size = 100

    table, allowed_fields = TABLE_MAP[table_name]

    # Build query
    query = table.select()

    # Search
    if search:
        search_clauses = []
        for field in allowed_fields:
            col = getattr(table.c, field, None)
            if col is not None:
                search_clauses.append(col.like(f"%{search}%"))
        if search_clauses:
            query = query.where(sqlalchemy.or_(*search_clauses))

    # Sort
    if sort in allowed_fields:
        col = getattr(table.c, sort, None)
        if col is not None:
            if isinstance(col.type, sqlalchemy.types.String):
                if dir_ == "desc":
                    query = query.order_by(sqlalchemy.func.lower(col).desc())
                else:
                    query = query.order_by(sqlalchemy.func.lower(col).asc())
            else:
                if dir_ == "desc":
                    query = query.order_by(col.desc())
                else:
                    query = query.order_by(col.asc())

    # Pagination
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Get total count for pagination
    count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(table)
    if search:
        search_clauses = []
        for field in allowed_fields:
            col = getattr(table.c, field, None)
            if col is not None:
                search_clauses.append(col.like(f"%{search}%"))
        if search_clauses:
            count_query = count_query.where(sqlalchemy.or_(*search_clauses))
    total = await database.fetch_val(count_query)
    last_page = max(1, (total + size - 1) // size)

    # Fetch data
    rows = await database.fetch_all(query)
    data = [dict(row) for row in rows]

    return JSONResponse({"data": data, "last_page": last_page, "total": total})

async def web_admin_table_set(request: Request):
    params = await request.json()
    adm = await is_admin(request)
    if not adm:
        return JSONResponse({"status": "failed", "message": "Invalid token."}, status_code=400)

    table_name = params.get("table")
    row = params.get("row")

    if table_name not in TABLE_MAP:
        return JSONResponse({"status": "failed", "message": "Invalid table name."}, status_code=401)
    
    table, _ = TABLE_MAP[table_name]
    columns = table.columns  # This is a ColumnCollection

    # To get a dict of column names and types:
    schema = {col.name: str(col.type) for col in columns}

    # VERIFY that the row data conforms to the schema
    try:
        row_data = row
        if not isinstance(row_data, dict):
            raise ValueError("Row data must be a JSON object.")
        id_field = None
        # Find primary key field (id or objectId)
        for pk in ["id", "objectId"]:
            if pk in row_data:
                id_field = pk
                break
        if not id_field:
            raise ValueError("Row data must contain a primary key ('id' or 'objectId').")
        for key, value in row_data.items():
            if key not in schema:
                raise ValueError(f"Field '{key}' does not exist in table schema.")
            # Type checking
            expected_type = schema[key]
            if expected_type.startswith("INTEGER"):
                if not isinstance(value, int):
                    raise ValueError(f"Field '{key}' must be an integer.")
            elif expected_type.startswith("FLOAT"):
                if not isinstance(value, float) and not isinstance(value, int):
                    raise ValueError(f"Field '{key}' must be a float.")
            elif expected_type.startswith("BOOLEAN"):
                if not isinstance(value, bool):
                    raise ValueError(f"Field '{key}' must be a boolean.")
            elif expected_type.startswith("JSON"):
                if not isinstance(value, dict) and not isinstance(value, list):
                    raise ValueError(f"Field '{key}' must be a JSON object or array.")
            elif expected_type.startswith("VARCHAR") or expected_type.startswith("STRING"):
                if not isinstance(value, str):
                    raise ValueError(f"Field '{key}' must be a string.")
            elif expected_type.startswith("DATETIME"):
                # Try to convert to Python datetime object
                try:
                    if isinstance(value, str):
                        dt_obj = datetime.datetime.fromisoformat(value)
                        row_data[key] = dt_obj
                    elif isinstance(value, (int, float)):
                        dt_obj = datetime.datetime.fromtimestamp(value)
                        row_data[key] = dt_obj
                    elif isinstance(value, datetime.datetime):
                        pass  # already a datetime object
                    else:
                        raise ValueError
                except Exception:
                    raise ValueError(f"Field '{key}' must be a valid ISO datetime string or timestamp.")
    except Exception as e:
        return JSONResponse({"status": "failed", "message": f"Invalid row data: {str(e)}"}, status_code=402)

    # Update the row in the database
    update_data = {k: v for k, v in row_data.items() if k != id_field}
    update_query = table.update().where(getattr(table.c, id_field) == row_data[id_field]).values(**update_data)
    await database.execute(update_query)

    return JSONResponse({"status": "success", "message": "Row updated successfully."})

async def web_admin_table_delete(request: Request):
    params = await request.json()
    adm = await is_admin(request)
    if not adm:
        return JSONResponse({"status": "failed", "message": "Invalid token."}, status_code=400)

    table_name = params.get("table")
    row_id = params.get("id")

    if table_name not in TABLE_MAP:
        return JSONResponse({"status": "failed", "message": "Invalid table name."}, status_code=401)
    
    if not row_id:
        return JSONResponse({"status": "failed", "message": "Row ID is required."}, status_code=402)
    
    table, _ = TABLE_MAP[table_name]

    if table_name in ["users", "sessions"]:
        delete_query = table.delete().where(table.c.id == row_id)
    else:
        delete_query = table.delete().where(table.c.objectId == row_id)

    result = await database.execute(delete_query)

    return JSONResponse({"status": "success", "message": "Row deleted successfully."})

async def web_admin_table_insert(request: Request):
    params = await request.json()
    adm = await is_admin(request)
    if not adm:
        return JSONResponse({"status": "failed", "message": "Invalid token."}, status_code=400)

    table_name = params.get("table")
    row = params.get("row")

    if table_name not in TABLE_MAP:
        return JSONResponse({"status": "failed", "message": "Invalid table name."}, status_code=401)
    
    table, _ = TABLE_MAP[table_name]
    columns = table.columns  # This is a ColumnCollection

    # To get a dict of column names and types:
    schema = {col.name: str(col.type) for col in columns}

    # VERIFY that the row data conforms to the schema
    try:
        row_data = row
        if not isinstance(row_data, dict):
            raise ValueError("Row data must be a JSON object.")
        for key, value in row_data.items():
            if key not in schema:
                raise ValueError(f"Field '{key}' does not exist in table schema.")
            # Type checking
            expected_type = schema[key]
            if expected_type.startswith("INTEGER"):
                if not isinstance(value, int):
                    raise ValueError(f"Field '{key}' must be an integer.")
            elif expected_type.startswith("FLOAT"):
                if not isinstance(value, float) and not isinstance(value, int):
                    raise ValueError(f"Field '{key}' must be a float.")
            elif expected_type.startswith("BOOLEAN"):
                if not isinstance(value, bool):
                    raise ValueError(f"Field '{key}' must be a boolean.")
            elif expected_type.startswith("JSON"):
                try:
                    json.loads(value)
                except:
                    raise ValueError(f"Field '{key}' must be a valid JSON string.")
            elif expected_type.startswith("VARCHAR") or expected_type.startswith("STRING"):
                if not isinstance(value, str):
                    raise ValueError(f"Field '{key}' must be a string.")
            elif expected_type.startswith("DATETIME"):
                # Try to convert to Python datetime object
                try:
                    if isinstance(value, str):
                        dt_obj = datetime.datetime.fromisoformat(value)
                        row_data[key] = dt_obj
                    elif isinstance(value, (int, float)):
                        dt_obj = datetime.datetime.fromtimestamp(value)
                        row_data[key] = dt_obj
                    elif isinstance(value, datetime.datetime):
                        pass  # already a datetime object
                    else:
                        raise ValueError
                except Exception:
                    raise ValueError(f"Field '{key}' must be a valid ISO datetime string or timestamp.")
    except Exception as e:
        return JSONResponse({"status": "failed", "message": f"Invalid row data: {str(e)}"}, status_code=402)
    # Insert the row into the database
    insert_data = {k: v for k, v in row_data.items() if k in schema}
    insert_query = table.insert().values(**insert_data)
    result = await database.execute(insert_query)
    return JSONResponse({"status": "success", "message": "Row inserted successfully.", "inserted_id": result})

routes = [
    Route("/Migrate", web_migrate_page, methods=["GET"]),
    Route("/Migrate/", web_migrate_page, methods=["GET"]),
    Route("/Migrate/Do", web_migrate_page_action, methods=["POST"]),
    Route("/Login", web_login_page, methods=["GET"]),
    Route("/Login/", web_login_page, methods=["GET"]),
    Route("/Login/Login", web_login_login, methods=["POST"]),
    Route("/Admin", web_admin_page, methods=["GET"]),
    Route("/Admin/", web_admin_page, methods=["GET"]),
    Route("/Admin/Table", web_admin_get_table, methods=["GET"]),
    Route("/Admin/Table/Update", web_admin_table_set, methods=["POST"]),
    Route("/Admin/Table/Delete", web_admin_table_delete, methods=["POST"]),
    Route("/Admin/Table/Insert", web_admin_table_insert, methods=["POST"]),
]