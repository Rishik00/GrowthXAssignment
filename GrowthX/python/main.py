# main.py
from fastapi import FastAPI
from user import router as assignment_router

app = FastAPI()

# Include the assignment router
app.include_router(assignment_router)
