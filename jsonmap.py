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

    # class Config:
    #     from_attributes = True

class ProductGetMap(ProductPostMap):
    id: int

class SalePostMap(BaseModel):
    product_id: int
    quantity: int

class SaleGetMap(SalePostMap):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []