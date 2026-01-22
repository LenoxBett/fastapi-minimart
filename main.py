from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Union, List
from db import get_db
from sqlalchemy import select
from models import Product, Sale
from models import Base, engine, SessionLocal
from jsonmap import ProductPostMap, ProductGetMap, SaleGetMap, SalePostMap

app = FastAPI()

# create tables on startup


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Duka FastAI": "1.0"}

@app.get("/products", response_model=List[ProductGetMap])
def get_products():
    prods = select(Product)
    return SessionLocal.scalars(prods)
# @app.get("/products", response_model=List[ProductGetMap])
# def get_products(db: Session = Depends(get_db)):
#     prods = db.query(Product).all()
#     return prods

@app.get("/sales" ,response_model=List[SaleGetMap])
def get_sales():
    sales = select(Sale).join(Sale.product)
    return SessionLocal.scalars(sales)