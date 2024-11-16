# endpoints.py
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from mongo_user import UserAssignment, MongoAssignment, UserMongoClient

# Set up MongoDB connection (replace with your actual URI)
mongo_uri = "mongodb+srv://myAtlasDBUser:db123@myatlasclusteredu.pn2vp0w.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
client = UserMongoClient(mongo_uri, dbname="User", cname="UserAssignments")
client.ping()  # Ping the database on startup

router = APIRouter()

# 1. Endpoint to add a new assignment
@router.post("/assignments/", response_model=int)
async def add_assignment(assignment: UserAssignment):
    new_assignment_id = client.insert_one_document(assignment)
    return new_assignment_id

# 2. Endpoint to view all assignments
@router.get("/assignments/", response_model=List[MongoAssignment])
async def view_all_assignments(limit: int = 5):
    assignments = client.get_all_documents(limit=limit)
    return assignments

# 3. Endpoint to view an assignment by ID
@router.get("/assignments/{assignment_id}", response_model=MongoAssignment)
async def view_assignment_by_id(assignment_id: int):
    assignment = client.get_document_by_id(assignment_id)
    if assignment:
        return assignment
    raise HTTPException(status_code=404, detail="Assignment not found")
