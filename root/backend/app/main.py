from fastapi import FastAPI
from backend.app.api.health import router as health_router

app = FastAPI()

app.include_router(health_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}