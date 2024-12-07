from pydantic import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Admin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password: str

admins_db = {
    "admin2": Admin(username="admin2", password=pwd_context.hash("password2")),
    "admin1": Admin(username="admin1", password=pwd_context.hash("password1"))
}

users_db = {
    "user1": User(username="user1", password="password1"),
    "user2": User(username="user2", password="password2"),
}

