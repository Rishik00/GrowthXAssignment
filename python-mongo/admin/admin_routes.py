from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import List
from dotenv import load_dotenv
import os

from models.models import admins_db
from models.mongoclient import MongoAssignment, MyMongoClient
from admin.admin_utils import create_access_token, get_current_admin

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

router = APIRouter()
client = MyMongoClient(MONGO_URI, dbname="User", cname="UserAssignments")
client.ping()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/token")
async def for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint to generate an access token for admins."""
    admin = admins_db.get(form_data.username)

    if not admin or not pwd_context.verify(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 2. View all assignments (Protected)
@router.get("/assignments/", response_model=List[MongoAssignment])
async def view_all_assignments(
    limit: int = 5, username: str = Depends(get_current_admin)
):
    
    print(f'Fetching something for the validated username: {username}')
    assignments = client.get_all_documents(limit=limit)
    return assignments


@router.get("/assignments/{assignment_id}", response_model=MongoAssignment)
async def view_assignment_by_id(
    assignment_id: int, admin: str = Depends(get_current_admin)
):
    """View a specific assignment by its ID."""
    assignment = client.get_document_by_id(assignment_id)

    if assignment:
        return assignment
    
    raise HTTPException(status_code=404, detail="Assignment not found")

@router.delete("/assignments/{assignment_id}", response_model=int)
async def delete_assignment(
    assignment_id: int, admin: str = Depends(get_current_admin)
):
    """Delete a specific assignment by its ID."""
    print("Deleting assignment from the database? You must be an admin then!")
    deleted = client.delete_one_document(assignment_id)

    if deleted:
        return assignment_id
    
    raise HTTPException(status_code=404, detail="Assignment not found")
