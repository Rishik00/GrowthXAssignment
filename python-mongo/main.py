from fastapi import FastAPI

from user.user_routes import router as user_router
from admin.admin_routes import router as admin_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(user_router, prefix='/user')
app.include_router(admin_router, prefix='/admin')