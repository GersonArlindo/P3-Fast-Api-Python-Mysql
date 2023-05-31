from fastapi import APIRouter
from schema.user_schema import UserSchema
from config.db import conn
from model.users import users

user = APIRouter()

@user.get("/")
def root():
    return {"message": " Hi, I am FastApi with router" }

@user.post("/api/user")
def create_user(data_user: UserSchema):
    try:
        new_user = data_user.dict()
        print(new_user)
        conn.execute(users.insert().values(new_user))
        conn.commit()
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"
