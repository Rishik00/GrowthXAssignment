from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from mongo_user import UserAssignment, MongoAssignment, UserMongoClient


load_dotenv()

client = UserMongoClient(os.getenv("MONGO_URI"), dbname="User", cname="UserAssignments")
client.ping()  # Ping the database on startup

# FastAPI app instance
app = FastAPI()

# OAuth2 configuration
auth_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User database
class User(BaseModel):
    username: str
    password: str

users_db = {
    "user1": User(username="user1", password="password1"),
    "user2": User(username="user2", password="password2"),
}

# Utility function to create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

def get_current_user(token: str = Depends(auth_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token using the secret key and algorithm from environment variables
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

# Endpoint to generate token
@app.post("/token")
async def for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if user is None or user.password != form_data.password:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 1. Add a new assignment (Protected)
@app.post("/assignments/", response_model=int)
async def add_assignment(
    assignment: UserAssignment, username: str = Depends(get_current_user)
):
    print(f'Fetching something for the validated username: {username}')
    new_assignment_id = client.insert_one_document(assignment)
    return new_assignment_id

# 2. View all assignments (Protected)
@app.get("/assignments/", response_model=List[MongoAssignment])
async def view_all_assignments(
    limit: int = 5, username: str = Depends(get_current_user)
):
    
    print(f'Fetching something for the validated username: {username}')
    assignments = client.get_all_documents(limit=limit)
    return assignments

# 3. View an assignment by ID (Protected)
@app.get("/assignments/{assignment_id}", response_model=MongoAssignment)
async def view_assignment_by_id(
    assignment_id: int, username: str = Depends(get_current_user)
):
    assignment = client.get_document_by_id(assignment_id)
    if assignment:
        return assignment
    raise HTTPException(status_code=404, detail="Assignment not found")
