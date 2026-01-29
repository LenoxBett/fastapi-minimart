from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import Union, List, Annotated
from db import get_db
from sqlalchemy import select
from models import Product, Sale, User, Base, engine, SessionLocal
from jsonmap import ProductPostMap, ProductGetMap, SaleGetMap, SalePostMap, UserPostLogin, UserPostRegister
from myjwt import create_access_token, authenticate_user,get_password_hash,verify_password
from datetime import timedelta
from jsonmap import Token
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)

app = FastAPI()

# create tables on startup


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Duka FastAI": "1.0"}

# =====================
# AUTH
# =====================
@app.post("/register", response_model=Token)
def register_user(
    user: UserPostRegister,
    db: Session = Depends(get_db),
):
    # Check if email already exists
    existing_user = db.execute(
        select(User).where(User.email == user.email)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)

    model_obj = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )

    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)

    access_token = create_access_token(
        data={"sub": user.email, "scope": ""},
        expires_delta=timedelta(minutes=30),
    )

    return Token(access_token=access_token, token_type="bearer")



@app.post("/login", response_model=Token)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "scope": " ".join(form_data.scopes),
        },
        expires_delta=timedelta(minutes=30),
    )

    return Token(access_token=access_token, token_type="bearer")


# =====================
# PRODUCTS
# =====================
@app.get("/products", response_model=List[ProductGetMap])
def get_products(db: Session = Depends(get_db)):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=ProductGetMap)
def create_product(
    json_product_obj: ProductPostMap,
    db: Session = Depends(get_db),
):
    model_obj = Product(
        name=json_product_obj.name,
        buying_price=json_product_obj.buying_price,
        selling_price=json_product_obj.selling_price,
    )

    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj

# =====================
# SALES
# =====================
@app.get("/sales", response_model=List[SaleGetMap])
def get_sales(db: Session = Depends(get_db)):
    return db.scalars(select(Sale)).all()


@app.post("/sales", response_model=SaleGetMap)
def create_sale(
    json_sale_obj: SalePostMap,
    db: Session = Depends(get_db),
):
    model_obj = Sale(
        product_id=json_sale_obj.product_id,
        quantity=json_sale_obj.quantity,
    )

    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj
