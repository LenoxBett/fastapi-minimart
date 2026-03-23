from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import Union, List, Annotated
from db import get_db
from sqlalchemy import select, func
from models import Product, Sale,Purchase, User, Base, engine
from jsonmap import ProductPostMap, ProductGetMap, SaleGetMap, SalePostMap, UserPostLogin, UserPostRegister, PurchaseGetMap, PurchasePostMap
from myjwt import create_access_token, authenticate_user,get_password_hash,verify_password,get_current_active_user,security, HTTPAuthorizationCredentials
from datetime import timedelta
from jsonmap import Token
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_products(
    # current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    return db.scalars(select(Product)).all()



@app.post("/products", response_model=ProductGetMap)
def create_product(
    json_product_obj: ProductPostMap,
    # current_user: Annotated[User, Depends(get_current_active_user)],
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
def get_sales(
    current_user: Annotated[User, Depends(security)],
    db: Session = Depends(get_db),
):
    sales=select(Sale).options(selectinload(Sale.product))
    return db.scalars(sales).all()
    # db: Session = Depends(get_db)):
    # return db.scalars(select(Sale)).all()


@app.post("/sales", response_model=SaleGetMap)
def create_sale(
    current_user: Annotated[User, Depends(security)],
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

    # db.add(model_obj)
    # db.commit()
    # db.refresh(model_obj)
    # return model_obj


# =====================
# PURCHASES
# =====================
@app.get("/purchase", response_model=List[PurchaseGetMap])
def get_purchases(
    current_user: Annotated[User, Depends(security)],
    db: Session = Depends(get_db),
):
    purchases = select(Purchase).options(selectinload(Purchase.product))
    return db.scalars(purchases).all()

@app.post("/purchase", response_model=PurchaseGetMap)
def create_purchase(
    current_user: Annotated[User, Depends(security)],
    json_purchase_obj: PurchasePostMap,
    db: Session = Depends(get_db),
):
    model_obj = Purchase(
        product_id=json_purchase_obj.product_id,
        quantity=json_purchase_obj.quantity,
    )

    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return model_obj

# =====================
#DASHBOARD
# =====================
@app.get("/dashboard/spp")
def sales_per_product(
    current_user: Annotated[User, Depends(security)],
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label("total_sold")
        )
        .join(Sale)
        .group_by(Product.id)
    )

    results = db.execute(stmt).all()

    return [
        {
            "product_id": r.id,
            "product_name": r.name,
            "total_sold": r.total_sold or 0
        }
        for r in results
    ]

@app.get("/dashboard/rspp")
def remaining_sales_per_product(
    current_user: Annotated[User, Depends(security)],
    db: Session = Depends(get_db),
):
    sales_subq = (
        select(
            Sale.product_id,
            func.sum(Sale.quantity).label("sold")
        )
        .group_by(Sale.product_id)
        .subquery()
    )

    purchase_subq = (
        select(
            Purchase.product_id,
            func.sum(Purchase.quantity).label("purchased")
        )
        .group_by(Purchase.product_id)
        .subquery()
    )

    stmt = (
        select(
            Product.id,
            Product.name,
            (
                func.coalesce(purchase_subq.c.purchased, 0) -
                func.coalesce(sales_subq.c.sold, 0)
            ).label("remaining")
        )
        .outerjoin(sales_subq, Product.id == sales_subq.c.product_id)
        .outerjoin(purchase_subq, Product.id == purchase_subq.c.product_id)
    )

    results = db.execute(stmt).all()

    return [
        {
            "product_id": r.id,
            "product_name": r.name,
            "remaining_quantity": r.remaining
        }
        for r in results
    ]

@app.get("/dashboard/ppp")
def profit_per_product(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    stmt = (
        select(
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label("total_sold"),
            Product.buying_price,
            Product.selling_price,
            (
                func.sum(Sale.quantity)
                * (Product.selling_price - Product.buying_price)
            ).label("profit")
        )
        .join(Sale)
        .group_by(Product.id)
    )

    result = db.execute(stmt).all()

    return [
        {
            "product_id": r.id,
            "product_name": r.name,
            "total_sold": r.total_sold or 0,
            "buying_price": r.buying_price,
            "selling_price": r.selling_price,
            "profit": float(r.profit or 0),
        }
        for r in result
    ]

@app.get("/dashboard/pppd")
def profit_per_product_per_day(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    sale_date = func.date(Sale.created_at).label("sale_date")
    stmt = (
        select(
            sale_date,
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label("total_sold"),
            Product.buying_price,
            Product.selling_price,
            (
                func.sum(Sale.quantity)
                * (Product.selling_price - Product.buying_price)
            ).label("profit")
        )
        .join(Sale)
        .group_by(sale_date, Product.id)
        .order_by(sale_date, Product.id)
    )

    result = db.execute(stmt).all()

    return [
        {
            "date": r.sale_date,
            "product_id": r.id,
            "product_name": r.name,
            "total_sold": r.total_sold or 0,
            "buying_price": r.buying_price,
            "selling_price": r.selling_price,
            "profit": float(r.profit or 0),
        }
        for r in result
    ]

