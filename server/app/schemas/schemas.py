from pydantic import BaseModel
from datetime import date
from typing import Optional


class SalesDataBase(BaseModel):
    master_distributor: Optional[str] = None
    distributor: Optional[str] = None
    line_of_business: Optional[str] = None
    supplier: Optional[str] = None
    agency: Optional[str] = None
    category: Optional[str] = None
    segment: Optional[str] = None
    brand: Optional[str] = None
    sub_brand: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    retailer_group: Optional[str] = None
    retailer_sub_group: Optional[str] = None
    channel: Optional[str] = None
    sub_channel: Optional[str] = None
    salesmen: Optional[str] = None
    order_number: Optional[str] = None
    customer: Optional[str] = None
    customer_account_name: Optional[str] = None
    customer_account_number: Optional[str] = None
    item: Optional[str] = None
    item_description: Optional[str] = None
    promo_item: Optional[str] = None
    foc_nonfoc: Optional[str] = None
    unit_selling_price: Optional[float] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    year: Optional[int] = None
    month: Optional[str] = None
    invoiced_quantity: Optional[float] = None
    value: Optional[float] = None


class SalesDataCreate(SalesDataBase):
    pass


class SalesData(SalesDataBase):
    id: int

    class Config:
        from_attributes = True
