from fastapi import FastAPI
from workoutapi.routers import api_router

app = FastAPI(title='workoutApi')
app.include_router(api_router)

