from pydantic import BaseModel
from datetime import date
from typing import Optional

class RegionBase(BaseModel):
    name: str

class RegionCreate(RegionBase):
    pass

class Region(RegionBase):
    id: int
    class Config:
        from_attributes = True


class StoreBase(BaseModel):
    region_id: int

class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    id: int
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    brand: str
    category: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    product_id: int
    store_id: int
    date: date
    quantity: int
    value: float

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: int
    class Config:
        from_attributes = True
