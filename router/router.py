from fastapi import APIRouter, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR
from schema.user_schema import UserSchema, DataUser
from config.db import conn
from model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List

user = APIRouter()


@user.get("/")
def root():
    return {"message": "Hi, I am FastAPI with router"}

@user.get("/api/user", response_model=List[UserSchema])
def get_users(): 
    result = conn.execute(users.select()).fetchall()
    conn.commit()
    print(result)
    return result

@user.get("/api/user/{user_id}", response_model=UserSchema)
def get_user(user_id: str):
    result = conn.execute(users.select().where(users.c.id == user_id)).first()
    print(result)
    return result

@user.post("/api/user", status_code=HTTP_201_CREATED)
def create_user(data_user: UserSchema):
    try:
        new_user = data_user.dict()
        print(new_user)
        new_user['user_pass'] = generate_password_hash(data_user.user_pass, "pbkdf2:sha256:30", 40)
        conn.execute(users.insert().values(new_user))
        conn.commit()
        return Response(status_code=HTTP_201_CREATED)
    except Exception as e:
        return Response(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=str(e))

@user.put("/api/user/{user_id}")
def update_user(user_id: str, data_update: UserSchema):
    encryp_pass = generate_password_hash(data_update.user_pass, "pbkdf2:sha256:30", 30)
    conn.execute(users.update().values(name=data_update.name, username=data_update.username,
    user_pass=encryp_pass).where(users.c.id == user_id))
    result = conn.execute(users.select().where(users.c.id == user_id)).first()
    conn.commit()

    return result

@user.delete("/api/user/{user_id}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    conn.execute(users.delete().where(users.c.id == user_id))
    conn.commit()

    return Response(status_code=HTTP_204_NO_CONTENT)

@user.post("/api/user/login")
def user_login(data_user: DataUser):
    result = conn.execute(users.select().where(users.c.username == data_user.username)).first()
    if result != None:
        check_pass = check_password_hash(result[3], data_user.user_pass)
        if check_pass:
            return {
                "status": 200,
                "message": "Access Success"
            }

    return {
        "status": 401,
        "message": "Access Denied"
    }