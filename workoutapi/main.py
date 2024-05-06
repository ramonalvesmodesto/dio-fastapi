from fastapi import FastAPI
from fastapi_pagination import add_pagination
from workoutapi.routers import api_router

app = FastAPI(title="workoutApi")
app.include_router(api_router)
add_pagination(app)
