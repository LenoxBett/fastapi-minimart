from pydantic import BaseModel
from datetime import datetime

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