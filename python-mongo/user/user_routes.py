from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

from models.models import users_db
from user.user_utils import create_access_token, get_current_user
from models.mongoclient import MyMongoClient, UserAssignment

load_dotenv()
router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
client = MyMongoClient(MONGO_URI, dbname="User", cname="UserAssignments")
client.ping()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Endpoint to generate token
@router.post("/token")
async def for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if user is None or user.password != form_data.password:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 1. Add a new assignment (Protected)
@router.post("/assignments/", response_model=int)
async def add_assignment(
    assignment: UserAssignment, username: str = Depends(get_current_user)
):
    print(f'Fetching something for the validated username: {username}')
    new_assignment_id = client.insert_one_document(assignment)
    return new_assignment_id

# 2. View all assignments (Protected)
@router.get("/assignments/", response_model=List[UserAssignment])
async def view_all_assignments(
    limit: int = 5, username: str = Depends(get_current_user)
):
    
    print(f'Fetching something for the validated username: {username}')
    assignments = client.get_all_documents(limit=limit)
    return assignments

# 3. View an assignment by ID (Protected)
@router.get("/assignments/{assignment_id}", response_model=UserAssignment)
async def view_assignment_by_id(
    assignment_id: int, username: str = Depends(get_current_user)
):
    assignment = client.get_document_by_field('assignment_id', assignment_id)
    print(assignment)
    if assignment:
        return assignment
    raise HTTPException(status_code=404, detail="Assignment not found")

@router.get("/user_assignments/{user}", response_model=UserAssignment)
async def get_assignment_by_username(
    user: str, username: str = Depends(get_current_user)
):
    # Fetch assignment by username
    print(user)
    assignment = client.get_document_by_field('user', user)
    print(assignment)
    if assignment:
        return assignment
    raise HTTPException(status_code=404, detail="Assignment not found")


