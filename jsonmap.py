from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserPostRegister(BaseModel):
    email: str
    username: str | None = None
    password: str

class UserPostLogin(BaseModel):
    email: str
    password: str

class ProductPostMap(BaseModel):
    name: str
    buying_price: float
    selling_price: float

class ProductGetMap(ProductPostMap):
    id: int

class SalePostMap(BaseModel):
    product_id: int
    quantity: int

class SaleGetMap(SalePostMap):
    id: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    scopes: str | None = None

class PurchasePostMap(BaseModel):
    product_id: int
    quantity: int


class PurchaseGetMap(PurchasePostMap):
    id: int
    created_at: datetime