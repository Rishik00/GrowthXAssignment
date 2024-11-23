from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from mongo_user import UserAssignment, MongoAssignment, UserMongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Admin(BaseModel):
    username: str
    password: str

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
MONGO_URI = os.getenv("MONGO_URI")

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB client
client = UserMongoClient(MONGO_URI, dbname="User", cname="UserAssignments")
client.ping()

# FastAPI app initialization
app = FastAPI()

# OAuth2 token URL
auth_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Admin database with hashed passwords
admins_db = {
    "admin2": Admin(username="admin2", password=pwd_context.hash("password1")),
}

# Models
class Admin(BaseModel):
    username: str
    password: str

def create_access_token(data: dict):
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(auth_scheme)):
    """Validate and retrieve the current admin from the JWT."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin: str = payload.get("sub")
        if admin is None:
            raise credentials_exception
        return admin
    except JWTError:
        raise credentials_exception

@app.post("/token")
async def for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint to generate an access token for admins."""
    admin = admins_db.get(form_data.username)

    if not admin or not pwd_context.verify(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 2. View all assignments (Protected)
@app.get("/assignments/", response_model=List[MongoAssignment])
async def view_all_assignments(
    limit: int = 5, username: str = Depends(get_current_admin)
):
    
    print(f'Fetching something for the validated username: {username}')
    assignments = client.get_all_documents(limit=limit)
    return assignments


@app.get("/assignments/{assignment_id}", response_model=MongoAssignment)
async def view_assignment_by_id(
    assignment_id: int, admin: str = Depends(get_current_admin)
):
    """View a specific assignment by its ID."""
    assignment = client.get_document_by_id(assignment_id)

    if assignment:
        return assignment
    
    raise HTTPException(status_code=404, detail="Assignment not found")

@app.delete("/assignments/{assignment_id}", response_model=int)
async def delete_assignment(
    assignment_id: int, admin: str = Depends(get_current_admin)
):
    """Delete a specific assignment by its ID."""
    print("Deleting assignment from the database? You must be an admin then!")
    deleted = client.delete_one_document(assignment_id)

    if deleted:
        return assignment_id
    
    raise HTTPException(status_code=404, detail="Assignment not found")
