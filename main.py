from typing import Union

from fastapi import FastAPI
from models import Base, engine

app = FastAPI()

# create tables on startup


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(Bind=engine)


@app.get("/")
def read_root():
    return {"Duka FastAI": "1.0"}